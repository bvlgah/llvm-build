#!/usr/bin/env bash
set -ex
currDir=$(cd $(dirname $0) && pwd)
llvmSrcDir=${currDir}/../llvm-project/llvm
llvmBuildDir=${currDir}/lldb_out
export CCACHE_DIR=$llvmBuildDir/ccache

python3 -m build \
  --src-dir $llvmSrcDir \
  --build-dir $llvmBuildDir \
  --enable-project clang \
  --enable-project lldb \
  --cc clang \
  --cxx clang++ \
  --use-lld \
  --use-ccache \
  --build-type release
