#/usr/bin/env sh
currDir=$(cd $(dirname $0) && pwd)
llvmSrcDir=${currDir}/../llvm-project/llvm
llvmBuildDir=${currDir}/out
CC=clang
CXX=clang++

export PYTHONPATH=$currDir
export CCACHE_DIR=$llvmBuildDir/ccache

python3 -m build \
  --src-dir $llvmSrcDir \
  --build-dir $llvmBuildDir \
  --enable-project mlir \
  --enable-project clang \
  --enable-project polly \
  --build-target Native \
  --build-target NVPTX \
  --build-target AMDGPU \
  --build-target RISCV \
  --build-target AArch64 \
  --build-type release \
  --enable-assertions \
  --cc clang \
  --cxx clang++ \
  --use-lld \
  --use-ccache
