set -ex

curr_dir=$(cd $(dirname $0) && pwd)
test_deps=('tcl' 'tk-dev')

. $curr_dir/apt_install.sh

ubuntu_install_package ${test_deps[@]}
