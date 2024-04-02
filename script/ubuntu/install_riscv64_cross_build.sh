set -ex

curr_dir=$(cd $(dirname $0) && pwd)
build_deps=('ninja-build' 'cmake' 'tar' 'xz-utils' 'ccache'
            'gcc-riscv64-linux-gnu' 'g++-riscv64-linux-gnu'
            'python3' 'python-is-python3' 'python3-pip' 'python3-venv')

. $curr_dir/apt_install.sh

ubuntu_install_package ${build_deps[@]}
