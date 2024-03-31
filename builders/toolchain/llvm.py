from pathlib import Path
from common.compiler import AbstractToolchain
from common.utils import FileSystemHelper

class LLVMToolchain(AbstractToolchain):
  _installDir: Path
  _ccPath: Path
  _cxxPath: Path
  _ldPath: Path
  _stripPath: Path

  def __init__(self, installDir: Path) -> None:
    self._installDir = installDir.resolve()
    FileSystemHelper.check_dir(self._installDir)
    self._ccPath = self._installDir / 'bin' / 'clang'
    self._cxxPath = self._installDir / 'bin' / 'clang++'
    self._ldPath = self._installDir / 'bin' / 'ld.lld'
    self._stripPath = self._installDir / 'bin' / 'llvm-strip'
    for binPath in (self._ccPath, self._cxxPath, self._ldPath, self._stripPath):
      FileSystemHelper.check_file(binPath)

  def cc(self) -> Path:
    return self._ccPath

  def cxx(self) -> Path:
    return self._cxxPath

  def ld(self) -> Path:
    return self._ldPath

  def strip(self) -> Path:
    return self._stripPath
