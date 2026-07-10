#!/usr/bin/env bash
set -ex

curr_dir=$(cd $(dirname $0) && pwd)

. ${curr_dir}/apt_install.sh
. ${curr_dir}/../util/install_mold.sh

# Install LLVM Ubuntu/Debain packages. See
# https://apt.llvm.org.
ubuntu_install_package curl lsb-release software-properties-common gnupg
curl -o /tmp/llvm.sh -L https://apt.llvm.org/llvm.sh
chmod a+x /tmp/llvm.sh
$(get_sudo_command) /tmp/llvm.sh 21

# Install packages required to build C++ projects with CMake and Ninja.
build_deps=("tar" "xz-utils" "git" "unzip"
            "ninja-build" "cmake" "ccache"
            "python3" "python-is-python3" "python3-pip" "python3-venv"
            "clang-21" "lld-21" "libc++-21-dev" "libpfm4-dev"
            "libclang-rt-21-dev" "libunwind-21-dev")
ubuntu_install_package ${build_deps[@]}
download_and_install_mold 0.9.0
