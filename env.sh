#!/usr/bin/env bash
set -ex
curr_dir=$(cd $(dirname $0) && pwd)
llvm_test_suite_dir="${curr_dir}/../llvm-test-suite"
cc_path="${CC:-$(which clang)}"
cxx_path="${CXX:-$(which clang++)}"
lld_path="${LD:-$(which ld.lld)}"
common_linker_flags="-fuse-ld=lld"
common_c_flags="-gline-tables-only"
common_cxx_flags="$common_c_flags"
