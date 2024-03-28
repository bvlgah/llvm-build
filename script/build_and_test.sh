#/usr/bin/env sh
currDir=$(cd $(dirname $0) && pwd)
llvmSrcDir=${currDir}/../llvm-project/llvm
llvmBuildDir=${currDir}/build_release
CC=clang
CXX=clang++

mkdir -p ${currDir}/build_release
cmake -G Ninja -S ${llvmSrcDir} -B ${llvmBuildDir} \
    -DLLVM_ENABLE_PROJECTS="mlir;clang;polly" \
    -DLLVM_BUILD_EXAMPLES=ON \
    -DLLVM_TARGETS_TO_BUILD="Native;NVPTX;AMDGPU;RISCV;AArch64" \
    -DCMAKE_BUILD_TYPE=Release \
    -DLLVM_ENABLE_ASSERTIONS=ON \
    -DCMAKE_C_COMPILER="$CC" \
    -DCMAKE_CXX_COMPILER="$CXX" \
    -DCMAKE_C_FLAGS="-fPIC" \
    -DCMAKE_CXX_FLAGS="-fPIC" \
    -DLLVM_ENABLE_LLD=ON \
    -DLLVM_CCACHE_BUILD=ON \
    -DMLIR_INCLUDE_INTEGRATION_TESTS=ON \
    -DLLVM_USE_SANITIZER="Address;Undefined" \
    | tee "build.$(date +%Y%m%d_%H%M).log"

cmake --build ${llvmBuildDir} --target check-all
