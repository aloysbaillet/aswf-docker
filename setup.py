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
    install_requires=[],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "aswfdocker=aswfdocker.cli.aswfdocker:cli",
        ],
    },
)
