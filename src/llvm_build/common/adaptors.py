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
        cflags: str = " ".join(self._option.getCFlags())
        cxxflags: str = " ".join(self._option.getCXXFlags())
        ldflags: str = " ".join(self._option.getLDFlags())
        defines: dict[str, str] = {
            "CMAKE_C_FLAGS": cflags,
            "CMAKE_CXX_FLAGS": cxxflags,
            "CMAKE_EXE_LINKER_FLAGS": ldflags,
            "CMAKE_MODULE_LINKER_FLAGS": ldflags,
            "CMAKE_SHARED_LINKER_FLAGS": ldflags,
        }
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
