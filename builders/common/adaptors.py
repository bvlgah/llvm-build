from typing import Dict

from common.base_builders import AbstractCMakeDefineProvider
from common.compiler import AbstractCompilerOption, AbstractToolchain
from common.utils import FileSystemHelper

class CompilerOptionDefineProvider(AbstractCMakeDefineProvider):
  _option: AbstractCompilerOption

  def __init__(self, option: AbstractCompilerOption) -> None:
    super().__init__()
    self._option = option

  def getDefines(self) -> Dict[str, str]:
    cflags: str = ' '.join(self._option.getCFlags())
    cxxflags: str = ' '.join(self._option.getCXXFlags())
    ldflags:str  = ' '.join(self._option.getLDFlags())
    defines: Dict[str, str] = {
      'CMAKE_C_FLAGS': cflags,
      'CMAKE_CXX_FLAGS': cxxflags,
      'CMAKE_EXE_LINKER_FLAGS': ldflags,
      'CMAKE_MODULE_LINKER_FLAGS': ldflags,
      'CMAKE_SHARED_LINKER_FLAGS': ldflags,
    }
    return defines

class ToolchainDefineProvider(AbstractCMakeDefineProvider):
  '''Only define CMAKE_C_COMPILER and CMAKE_CXX_COMPILER'''
  _toolchain: AbstractToolchain

  def __init__(self, toolchain: AbstractToolchain) -> None:
    super().__init__()
    self._toolchain = toolchain

  def getDefines(self) -> Dict[str, str]:
    FileSystemHelper.check_file(self._toolchain.cc())
    FileSystemHelper.check_file(self._toolchain.cxx())
    defines: Dict[str, str] = {
      'CMAKE_C_COMPILER': str(self._toolchain.cc()),
      'CMAKE_CXX_COMPILER': str(self._toolchain.cxx()),
    }
    return defines
