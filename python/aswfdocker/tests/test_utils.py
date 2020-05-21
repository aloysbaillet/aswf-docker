# Copyright (c) Contributors to the aswf-docker Project. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Tests for the utility commands
"""

import unittest
import logging
import tempfile
import os

from click.testing import CliRunner

from aswfdocker import utils, index, constants
from aswfdocker.cli import aswfdocker


class TestUtils(unittest.TestCase):
    def test_get_docker_org(self):
        self.assertEqual(utils.get_docker_org("", ""), "aswftesting")
        self.assertEqual(
            utils.get_docker_org(
                constants.MAIN_GITHUB_ASWF_DOCKER_URL, "refs/heads/master",
            ),
            "aswf",
        )
        self.assertEqual(
            utils.get_docker_org(
                constants.MAIN_GITHUB_ASWF_DOCKER_URL, "refs/heads/testing",
            ),
            "aswftesting",
        )
        self.assertEqual(
            utils.get_docker_org(
                "https://github.com/randomfork/aswf-docker", "refs/heads/master"
            ),
            "aswflocaltesting",
        )
        self.assertEqual(
            utils.get_docker_org(
                "https://github.com/randomfork/aswf-docker", "refs/heads/randombranch"
            ),
            "aswflocaltesting",
        )

    def test_get_docker_push(self):
        self.assertFalse(utils.get_docker_push("", ""))
        self.assertTrue(
            utils.get_docker_push(
                constants.MAIN_GITHUB_ASWF_DOCKER_URL, "refs/heads/master",
            )
        )
        self.assertTrue(
            utils.get_docker_push(
                constants.MAIN_GITHUB_ASWF_DOCKER_URL, "refs/heads/testing",
            )
        )
        self.assertFalse(
            utils.get_docker_push(
                "https://github.com/randomfork/aswf-docker", "refs/heads/master"
            )
        )
        self.assertFalse(
            utils.get_docker_push(
                "https://github.com/randomfork/aswf-docker", "refs/heads/randombranch"
            )
        )


class TestUtilsCli(unittest.TestCase):
    def setUp(self):
        logging.getLogger("").handlers = []
        self.maxDiff = None

    def test_cli_getdockerorg(self):
        runner = CliRunner()
        result = runner.invoke(aswfdocker.cli, ["getdockerorg"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "aswftesting")

    def test_cli_getdockerorgforced(self):
        runner = CliRunner()
        result = runner.invoke(
            aswfdocker.cli,
            [
                "--repo-uri",
                "https://github.com/AcademySoftwareFoundation/aswf-docker",
                "--source-branch",
                "refs/heads/master",
                "getdockerorg",
            ],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "aswf")

    def test_cli_getdockerpush(self):
        runner = CliRunner()
        result = runner.invoke(aswfdocker.cli, ["getdockerpush"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "false")

    def test_cli_download(self):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdirname:
            result = runner.invoke(
                aswfdocker.cli,
                [
                    "--repo-root",
                    tmpdirname,
                    "download",
                    "--package",
                    "tbb",
                    "--version",
                    "2019",
                ],
                catch_exceptions=False,
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.output, f"{tmpdirname}/packages/2019/tbb.tar.gz")
            self.assertTrue(os.path.exists(result.output))

    def test_cli_packages(self):
        runner = CliRunner()
        result = runner.invoke(aswfdocker.cli, ["packages"], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)
        pkgs = result.output.split("\n")
        self.assertGreater(len(pkgs), 20)
        clang_version = list(
            index.Index().iter_versions(constants.ImageType.PACKAGE, "clang")
        )[0]
        self.assertEqual(
            pkgs[0], f"common/ci-package-clang:{clang_version}",
        )

    def test_cli_images(self):
        runner = CliRunner()
        result = runner.invoke(aswfdocker.cli, ["images"], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)
        imgs = result.output.split("\n")
        self.assertGreater(len(imgs), 15)
        common_version = list(
            index.Index().iter_versions(constants.ImageType.IMAGE, "common")
        )[0]
        self.assertEqual(
            imgs[0], f"common/ci-common:{common_version}",
        )
