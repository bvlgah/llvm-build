#!/bin/env bash
set -ex
cmake -G Ninja -S ../llvm-project/runtimes -B runtime_out_release \
  -DLLVM_ENABLE_RUNTIMES="libcxx;libcxxabi;libunwind;compiler-rt" \
  -DLLVM_TARGETS_TO_BUILD="RISCV" \
  -DCMAKE_BUILD_TYPE=Realse \
  -DCMAKE_C_COMPILER=clang \
  -DCMAKE_CXX_COMPILER=clang++ \
  -DLLVM_USE_LINKER=lld \
  -DCMAKE_C_FLAGS="-fuse-ld=lld -fdata-sections -ffunction-sections -Wl,--icf=all -Wl,--gc-sections" \
  -DCMAKE_CXX_FLAGS="-fuse-ld=lld -fdata-sections -ffunction-sections -Wl,--icf=all -Wl,--gc-sections"
ninja -C runtime_out_release cxx cxxabi unwind
