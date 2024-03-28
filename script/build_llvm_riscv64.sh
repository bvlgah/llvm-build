#!/bin/env bash
set -ex
curr_dir=$(cd $(dirname $0) && pwd)
src_dir=${curr_dir}/../llvm-project/llvm
build_dir=${curr_dir}/build_llvm_riscv64_release
riscv64_target="riscv64-unknown-linux-gnu"
riscv64_sysroot="/usr/riscv64-linux-gnu"
riscv64_cc="riscv64-linux-gnu-gcc"
riscv64_cxx="riscv64-linux-gnu-g++"

cmake -G Ninja -S $src_dir \
  -B $build_dir \
  -DCMAKE_SYSTEM_NAME=Linux \
  -DCMAKE_CROSSCOMPILING=True \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=${riscv64_cc} \
  -DCMAKE_CXX_COMPILER=${riscv64_cxx} \
  -DLLVM_ENABLE_PROJECTS="lld;clang" \
  -DLLVM_TARGETS_TO_BUILD=RISCV \
  -DLLVM_HOST_TRIPLE=${riscv64_target}

ninja -C $build_dir clang lld
