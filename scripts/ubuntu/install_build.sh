#!/usr/bin/env bash
set -ex

curr_dir=$(cd $(dirname $0) && pwd)
build_deps=("clang" "lld" "ninja-build" "cmake" "ccache" "tar" "xz-utils"
            "python3" "python-is-python3" "python3-pip" "python3-venv" "unzip"
            "git" "libc++-dev" "libpfm4-dev" "libclang-rt-dev" "curl")

. ${curr_dir}/apt_install.sh
. ${curr_dir}/../util/install_mold.sh

ubuntu_install_package ${build_deps[@]}
download_and_install_mold 0.9.0
