from llvm_build.common.base_builders import AbstractCMakeDefineProvider
from llvm_build.common.compiler import AbstractCompilerOption
from llvm_build.common.utils import FileSystemHelper
from llvm_build.toolchain import PosixToolchain


class CompilerOptionDefineProvider(AbstractCMakeDefineProvider):
    _option: AbstractCompilerOption

    def __init__(self, option: AbstractCompilerOption) -> None:
        super().__init__()
        self._option = option

    def getDefines(self) -> dict[str, str]:
        defines: dict[str, str] = dict()
        cflags = self._option.getCFlags()
        if cflags:
            defines["CMAKE_C_FLAGS"] = " ".join(cflags)
        cxxflags = self._option.getCXXFlags()
        if cxxflags:
            defines["CMAKE_CXX_FLAGS"] = " ".join(cxxflags)
        ldflags = self._option.getLDFlags()
        if ldflags:
            value = " ".join(ldflags)
            defines["CMAKE_EXE_LINKER_FLAGS"] = value
            defines["CMAKE_MODULE_LINKER_FLAGS"] = value
            defines["CMAKE_SHARED_LINKER_FLAGS"] = value
        return defines


class ToolchainDefineProvider(AbstractCMakeDefineProvider):
    """Only define CMAKE_C_COMPILER and CMAKE_CXX_COMPILER"""

    _toolchain: PosixToolchain

    def __init__(self, toolchain: PosixToolchain) -> None:
        super().__init__()
        self._toolchain = toolchain

    def getDefines(self) -> dict[str, str]:
        FileSystemHelper.check_file(self._toolchain.cc)
        FileSystemHelper.check_file(self._toolchain.cxx)
        defines: dict[str, str] = {
            "CMAKE_C_COMPILER": str(self._toolchain.cc),
            "CMAKE_CXX_COMPILER": str(self._toolchain.cxx),
        }
        return defines
