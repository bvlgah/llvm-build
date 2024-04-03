#!/usr/bin/env bash
set -ex

curr_dir=$(cd $(dirname $0) && pwd)
build_deps=('clang' 'lld' 'ninja-build' 'cmake' 'ccache' 'tar' 'xz-utils'
            'python3' 'python-is-python3' 'python3-pip' 'python3-venv')

. $curr_dir/apt_install.sh

ubuntu_install_package ${build_deps[@]}
