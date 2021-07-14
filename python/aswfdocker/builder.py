# Copyright (c) Contributors to the aswf-docker Project. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""
CI Image and Package Builder
"""
import logging
import subprocess
import json
import os
import tempfile
import typing

from aswfdocker import constants, aswfinfo, utils, groupinfo, index

logger = logging.getLogger(__name__)


class Builder:
    """Builder generates a "docker buildx bake" json file to drive the parallel builds of Docker images."""

    def __init__(
        self,
        build_info: aswfinfo.ASWFInfo,
        group_info: groupinfo.GroupInfo,
        push: bool = False,
    ):
        self.push = push
        self.build_info = build_info
        self.group_info = group_info
        self.index = index.Index()

    def make_bake_dict(self) -> typing.Dict[str, dict]:
        root: typing.Dict[str, dict] = {}
        root["target"] = {}
        versions_to_bake = set()
        for image, version in self.group_info.iter_images_versions():
            major_version = utils.get_major_version(version)
            version_info = self.index.version_info(major_version)
            if self.group_info.type == constants.ImageType.PACKAGE:
                if version in versions_to_bake:
                    # Only one version per image needed
                    continue
                if int(major_version) > 1000:
                    # Only bake images for ci_common!
                    continue
                versions_to_bake.add(version)
                tags = list(
                    map(
                        lambda tag: f"{constants.DOCKER_REGISTRY}/{self.build_info.docker_org}/ci-centos7-gl-conan:{tag}",
                        [version, major_version],
                    )
                )
                image_base = image.replace("ci-package-", "")
                group = self.index.get_group_from_image(
                    self.group_info.type, image_base
                )
                docker_file = f"packages/{group}/Dockerfile"
            else:
                tags = version_info.get_tags(version, self.build_info.docker_org, image)
                docker_file = f"{image}/Dockerfile"
            target_dict = {
                "context": ".",
                "dockerfile": docker_file,
                "args": {
                    "ASWF_ORG": self.build_info.docker_org,
                    "ASWF_PKG_ORG": self.build_info.package_org,
                    "ASWF_VERSION": version,
                    "CI_COMMON_VERSION": version_info.ci_common_version,
                    "ASWF_VFXPLATFORM_VERSION": version_info.major_version,
                },
                "labels": {
                    "org.opencontainers.image.created": self.build_info.build_date,
                    "org.opencontainers.image.revision": self.build_info.vcs_ref,
                },
                "tags": tags,
                "output": ["type=registry,push=true" if self.push and self.group_info.type == constants.ImageType.IMAGE else "type=docker"],
            }
            target_dict["args"].update(version_info.all_package_versions)
            if self.group_info.type == constants.ImageType.PACKAGE:
                target_dict["target"] = "ci-centos7-gl-conan"
            root["target"][f"{image}-{major_version}"] = target_dict

        root["group"] = {"default": {"targets": list(root["target"].keys())}}
        return root

    def make_bake_jsonfile(self) -> str:
        d = self.make_bake_dict()
        if not d["group"]["default"]["targets"]:
            return None
        groups = "-".join(self.group_info.names)
        versions = "-".join(self.group_info.versions)
        path = os.path.join(
            tempfile.gettempdir(),
            f"docker-bake-{self.group_info.type.name}-{groups}-{versions}.json",
        )
        with open(path, "w") as f:
            json.dump(d, f, indent=4, sort_keys=True)
        return path

    def _run(self, cmd: str, dry_run: bool):
        if dry_run:
            logger.info("Would build: '%s'", cmd)
        else:
            logger.info("Building: '%s'", cmd)
            subprocess.run(cmd, shell=True, check=True, cwd=self.build_info.repo_root)

    def _run_in_docker(self, base_cmd, cmd, dry_run):
        self._run(
            " ".join(base_cmd + cmd), dry_run=dry_run,
        )

    def build(self, dry_run: bool = False, progress: str = "") -> None:
        path = self.make_bake_jsonfile()
        if path:
            self._run(
                f"docker buildx bake -f {path} --progress {progress}", dry_run=dry_run
            )
        if self.group_info.type != constants.ImageType.PACKAGE:
            return
        for image, version in self.group_info.iter_images_versions(get_image=True):
            major_version = utils.get_major_version(version)
            version_info = self.index.version_info(major_version)
            envs = {"CONAN_USER_HOME": "/tmp/conan", "CCACHE_DIR": "/tmp/ccache"}
            if "CONAN_LOGIN_USERNAME" in os.environ:
                envs["CONAN_LOGIN_USERNAME"] = os.environ["CONAN_PASSWORD"]
            if "ARTIFACTORY_USER" in os.environ:
                envs["CONAN_LOGIN_USERNAME"] = os.environ["ARTIFACTORY_USER"]
            if "CONAN_PASSWORD" in os.environ:
                envs["CONAN_PASSWORD"] = os.environ["CONAN_PASSWORD"]
            if "ARTIFACTORY_TOKEN" in os.environ:
                envs["CONAN_PASSWORD"] = os.environ["ARTIFACTORY_TOKEN"]
            conan_base = os.path.join(utils.get_git_top_level(), "packages", "conan")
            vols = {
                os.path.join(conan_base, "settings"): "/tmp/conan/.conan",
                os.path.join(conan_base, "recipes"): "/tmp/conan/recipes",
                os.path.join(conan_base, "ccache"): "/tmp/ccache",
            }
            base_cmd = ["docker", "run", "-t"]
            for name, value in envs.items():
                base_cmd.append("-e")
                base_cmd.append(f"{name}={value}")
            for name, value in vols.items():
                base_cmd.append("-v")
                base_cmd.append(f"{name}:{value}")
            tag = f"{constants.DOCKER_REGISTRY}/{self.build_info.docker_org}/ci-centos7-gl-conan:{version_info.ci_common_version}"
            base_cmd.append(tag)
            self._run_in_docker(
                base_cmd,
                [
                    "conan",
                    "config",
                    "set",
                    f"general.default_profile={version_info.conan_profile}",
                ],
                dry_run,
            )
            full_version = version_info.package_versions.get('ASWF_' + image.upper() + '_VERSION')
            conan_version = f"{image}/{full_version}@{self.build_info.docker_org}/{version_info.conan_profile}"
            self._run_in_docker(
                base_cmd,
                ["conan", "create", f"/tmp/conan/recipes/{image}", conan_version],
                dry_run,
            )
            if self.push:
                self._run_in_docker(
                    base_cmd,
                    ["conan", "upload", "--all", "-r", "aswftesting", conan_version],
                    dry_run,
                )
