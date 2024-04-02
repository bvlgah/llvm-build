set -ex

curr_dir=$(cd $(dirname $0) && pwd)
test_deps=('tcl' 'tk-dev' 'python3' 'python-is-python3' 'python3-venv'
           'python3-pip' 'cmake' 'ninja-build')

. $curr_dir/apt_install.sh

ubuntu_install_package ${test_deps[@]}