import abc
from pathlib import Path
from typing import List

class AbstractCompilerOption(abc.ABC):
  @abc.abstractmethod
  def getCFlags(self) -> List[str]:
    ...

  @abc.abstractmethod
  def getCXXFlags(self) -> List[str]:
    ...

  @abc.abstractmethod
  def getLDFlags(self) -> List[str]:
    ...

class CompilerOption(AbstractCompilerOption):
  _cflags: List[str]
  _cxxflags: List[str]
  _ldflags: List[str]

  def __init__(self) -> None:
    super().__init__()
    self._cflags = []
    self._cxxflags = []
    self._ldflags = []

  def addCFlag(self, cflag: str) -> None:
    self._cflags.append(cflag)

  def addCXXFlag(self, cxxflag: str) -> None:
    self._cxxflags.append(cxxflag)

  def addLDFalg(self, ldflag: str) -> None:
    self._ldflags.append(ldflag)

  def getCFlags(self) -> List[str]:
    return self._cflags.copy()

  def getCXXFlags(self) -> List[str]:
    return self._cxxflags.copy()

  def getLDFlags(self) -> List[str]:
    return self._ldflags.copy()

class AbstractToolchain(abc.ABC):
  @abc.abstractmethod
  def cc(self) -> Path:
    ...

  @abc.abstractmethod
  def cxx(self) -> Path:
    ...

  @abc.abstractmethod
  def ld(self) -> Path:
    ...

  @abc.abstractmethod
  def strip(self) -> Path:
    ...

class CompilerOptionAggregate(AbstractCompilerOption):
  _options: List[AbstractCompilerOption]

  def __init__(self) -> None:
    super().__init__()
    self._options = []

  def addCompilerOptions(self, option: AbstractCompilerOption) -> None:
    self._options.append(option)

  def getCFlags(self) -> List[str]:
    cflags = []
    for option in self._options:
      cflags.extend(option.getCFlags())
    return cflags

  def getCXXFlags(self) -> List[str]:
    cxxflags = []
    for option in self._options:
      cxxflags.extend(option.getCXXFlags())
    return cxxflags

  def getLDFlags(self) -> List[str]:
    ldflags = []
    for option in self._options:
      ldflags.extend(option.getLDFlags())
    return ldflags
