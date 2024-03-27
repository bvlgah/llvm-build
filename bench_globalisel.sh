#!/usr/bin/env bash
set -ex
source $(cd $(dirname $0) && pwd)/env.sh

build_dir=${curr_dir}/globalisel
globalisel_cflags="-fglobal-isel"
globalisel_cxxflags=$globalisel_cflags

mkdir -p $build_dir
cmake -S $llvm_test_suite_dir -B $build_dir -G "Ninja" \
      -C ${llvm_test_suite_dir}/cmake/caches/O3.cmake \
      -DCMAKE_C_COMPILER=$cc_path \
      -DCMAKE_CXX_COMPILER=$cxx_path \
      -DCMAKE_C_FLAGS=$globalisel_cflags \
      -DCMAKE_CXX_FLAGS=$globalisel_cxxflags \
      -DCMAKE_EXE_LINKER_FLAGS="$common_linker_flags" \
      -DCMAKE_MODULE_LINKER_FLAGS="$common_linker_flags" \
      -DCMAKE_SHARED_LINKER_FLAGS="$common_linker_flags"
