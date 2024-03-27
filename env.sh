#!/usr/bin/env bash
set -ex
curr_dir=$(cd $(dirname $0) && pwd)
llvm_test_suite_dir="${curr_dir}/../llvm-test-suite"
cc_path=/opt/clang/clang/bin/clang
cxx_path=/opt/clang/clang/bin/clang++
lld_path=/opt/clang/clang/bin/ld.lld
common_linker_flags="-fuse-ld=lld"
