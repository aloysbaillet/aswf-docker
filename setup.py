# Copyright (c) Contributors to the aswf-docker Project. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
from setuptools import setup, find_packages

with open("python/README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="aswfdocker",
    version="0.5.0",
    author="Aloys Baillet",
    author_email="aloys.baillet+github@gmail.com",
    description="ASWF Docker Utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AcademySoftwareFoundation/aswf-docker",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    package_data={"aswfdocker": ["data/*.yaml", "data/*.jinja2"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "bottle==0.12.19",
        "certifi==2021.10.8",
        "charset-normalizer==2.0.6; python_version >= '3'",
        "click==8.0.2",
        "colorama==0.4.4; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "conan==1.41.0",
        "deprecated==1.2.13; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "distro==1.6.0",
        "fasteners==0.16.3",
        "idna==3.2; python_version >= '3'",
        "importlib-resources==5.2.2",
        "jinja2==2.11.3",
        "markupsafe==2.0.1; python_version >= '3.6'",
        "node-semver==0.6.1",
        "patch-ng==1.17.4",
        "pluginbase==1.0.1",
        "pygithub==1.53",
        "pygments==2.10.0; python_version >= '3.5'",
        "pyjwt==1.7.1",
        "pyyaml==5.3.1",
        "requests==2.23.0",
        "urllib3==1.25.9; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4' and python_version < '4'",
        "wrapt==1.12.1",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "aswfdocker=aswfdocker.cli.aswfdocker:cli",
        ],
    },
)
