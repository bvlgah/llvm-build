#!/bin/env bash
set -ex
cmake -G Ninja -S ../llvm-project/runtimes -B runtime_out_debug \
  -DLLVM_ENABLE_RUNTIMES="libcxx;libcxxabi;libunwind" \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_C_COMPILER=clang-18 \
  -DCMAKE_CXX_COMPILER=clang++-18 \
  -DLLVM_USE_LINKER=lld-18
ninja -C runtime_out_debug cxx cxxabi unwind
