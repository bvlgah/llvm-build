#/usr/bin/env sh
currDir=$(cd $(dirname $0) && pwd)
llvmSrcDir=${currDir}/../llvm-project/llvm
llvmBuildDir=${currDir}/out
CC=clang
CXX=clang++

export PYTHONPATH=$currDir
# export CCACHE_DIR=$llvmBuildDir/ccache

python3 -m build \
  --src-dir $llvmSrcDir \
  --build-dir $llvmBuildDir \
  --enable-project clang \
  --build-target Native \
  --build-target RISCV \
  --build-type release \
  --cc $CC \
  --cxx $CXX \
  --use-lld \
  --use-ccache
