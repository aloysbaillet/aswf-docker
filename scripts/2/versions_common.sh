#!/usr/bin/env bash
# Copyright (c) Contributors to the aswf-docker Project. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

set -ex

export DTS_VERSION=9
export CCACHE_VERSION=3.7.9
export CLANG_VERSION=10.0.1
export NINJA_VERSION=1.10.0
export SONAR_VERSION=3.3.0.1492
export PKGS_COMMON_CMAKE_VERSION=3.12.4 # Only used to build common packages

if [[ $CLANG_MAJOR_VERSION == 10 ]]; then
    export CLANG_VERSION=10.0.1
elif [[ $CLANG_MAJOR_VERSION == 11 ]]; then
    export CLANG_VERSION=11.0.0
fi