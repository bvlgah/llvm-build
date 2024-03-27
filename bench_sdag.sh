#!/usr/bin/env bash
set -ex
source $(cd $(dirname $0) && pwd)/env.sh

build_dir=${curr_dir}/sdag
sdag_c_flags="-fno-global-isel $common_c_flags"
sdag_cxx_flags=$sdag_c_flags

mkdir -p $build_dir
cmake -S $llvm_test_suite_dir -B $build_dir -G "Ninja" \
      -C ${llvm_test_suite_dir}/cmake/caches/O3.cmake \
      -DCMAKE_C_COMPILER=$cc_path \
      -DCMAKE_CXX_COMPILER=$cxx_path \
      -DCMAKE_C_FLAGS="$sdag_c_flags" \
      -DCMAKE_CXX_FLAGS="$sdag_cxx_flags" \
      -DCMAKE_EXE_LINKER_FLAGS="$common_linker_flags" \
      -DCMAKE_MODULE_LINKER_FLAGS="$common_linker_flags" \
      -DCMAKE_SHARED_LINKER_FLAGS="$common_linker_flags"
