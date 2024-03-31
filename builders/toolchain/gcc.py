from pathlib import Path
from common.compiler import AbstractToolchain
from common.utils import FileSystemHelper


class GCCToolchain(AbstractToolchain):
  _hostPrefix: str
  _installDir: Path
  _ccPath: Path
  _cxxPath: Path
  _ldPath: Path
  _stripPath: Path

  def __init__(self, hostPrefix: str, installDir: Path) -> None:
    self._installDir = installDir.resolve()
    self._hostPrefix = hostPrefix
    FileSystemHelper.check_dir(self._installDir)
    self._ccPath = self._installDir / 'bin' / \
        self._appendHostPrefixIfNeccessary('gcc')
    self._cxxPath = self._installDir / 'bin' / \
        self._appendHostPrefixIfNeccessary('g++')
    self._ldPath = self._installDir / 'bin' / \
        self._appendHostPrefixIfNeccessary('ld')
    self._stripPath = self._installDir / 'bin' / \
        self._appendHostPrefixIfNeccessary('strip')
    for binPath in (self._ccPath, self._cxxPath, self._ldPath, self._stripPath):
      FileSystemHelper.check_file(binPath)

  def _appendHostPrefixIfNeccessary(self, binName: str) -> str:
    if not self._hostPrefix:
      return binName
    else:
      return f'{self._hostPrefix}-{binName}'

  def cc(self) -> Path:
    return self._ccPath

  def cxx(self) -> Path:
    return self._cxxPath

  def ld(self) -> Path:
    return self._ldPath

  def strip(self) -> Path:
    return self._stripPath
