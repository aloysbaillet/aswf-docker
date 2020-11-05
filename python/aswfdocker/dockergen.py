# Copyright (c) Contributors to the aswf-docker Project. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Migration of ASWF docker images between docker organisations
"""
import logging
import os

import yaml
from jinja2 import Environment, PackageLoader

from aswfdocker import utils, index, constants


logger = logging.getLogger(__name__)


class DockerGen:
    def __init__(self, image_name):
        self.image_name = image_name
        self.env = Environment(loader=PackageLoader("aswfdocker", "data"))

    def _get_image_data(self):
        image_data_path = os.path.join(
            utils.get_git_top_level(), f"ci-{self.image_name}/data.yaml"
        )
        with open(image_data_path) as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    def generate_dockerfile(self):
        image_data = self._get_image_data()
        template = self.env.get_template("ci-image-dockerfile.tmpl")
        dockerfile_path = os.path.join(
            utils.get_git_top_level(), f"ci-{self.image_name}/Dockerfile"
        )

        with open(dockerfile_path, "w") as f:
            f.write(template.render(image_data))
        return dockerfile_path

    def check_dockerfile(self):
        image_data = self._get_image_data()
        template = self.env.get_template("ci-image-dockerfile.tmpl")
        dockerfile_path = os.path.join(
            utils.get_git_top_level(), f"ci-{self.image_name}/Dockerfile"
        )

        with open(dockerfile_path) as f:
            ok = f.read() == template.render(image_data)
        return dockerfile_path, ok

    def generate_readme(self):
        image_data = self._get_image_data()
        image_data["index"] = index.Index()
        image_data["constants"] = constants

        template = self.env.get_template("ci-image-readme.tmpl")
        readme_path = os.path.join(
            utils.get_git_top_level(), f"ci-{self.image_name}/Readme.md"
        )

        with open(readme_path, "w") as f:
            f.write(template.render(image_data))
        return readme_path

    def check_readme(self):
        image_data = self._get_image_data()
        image_data["index"] = index.Index()
        image_data["constants"] = constants

        template = self.env.get_template("ci-image-readme.tmpl")
        readme_path = os.path.join(
            utils.get_git_top_level(), f"ci-{self.image_name}/Readme.md"
        )

        with open(readme_path) as f:
            ok = f.read() == template.render(image_data)
        return readme_path, ok