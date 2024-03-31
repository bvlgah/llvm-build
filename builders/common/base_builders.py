import abc
from contextlib import contextmanager
import datetime
from enum import Enum
from io import StringIO
import os
from pathlib import Path
import shutil
import subprocess
from typing import List, Optional

from common.utils import FileSystemHelper, LoggerMixin, StrValueEnum

class BuilderKind(str, Enum):
  cmake = 'cmake'

class AbstractBuilder(abc.ABC, LoggerMixin):
  @abc.abstractmethod
  def configure(self) -> None:
    ...

  @abc.abstractmethod
  def build(self) -> None:
    ...

  @abc.abstractmethod
  def install(self) ->None :
    ...

class TimedBuilder(AbstractBuilder):
  _builder : AbstractBuilder

  @contextmanager
  def _timingContext(self, processName: str):
    startTimestamp = datetime.datetime.now()
    try:
      yield
    finally:
      endTimestamp = datetime.datetime.now()
      timeDiff = endTimestamp - startTimestamp
      self.logger.info("%s took %s seconds",
          processName, timeDiff.total_seconds())

  def __init__(self, builder: AbstractBuilder) -> None:
    self._builder = builder

  def configure(self) -> None:
    with self._timingContext("Configuration"):
        self._builder.configure()

  def build(self) -> None:
    with self._timingContext("Building"):
        self._builder.build()

  def install(self) -> None:
    with self._timingContext("Installation"):
        self._builder.install()

class AbstractCMakeDefineProvider(abc.ABC):
  @abc.abstractmethod
  def getDefines(self) -> List[str]:
    ...

class CMakeGenerator(StrValueEnum):
  '''Enum class representing CMake generators. Currently, there are two enums,
     Default and Ninja. The Default generator is system-dependent.'''
  Default = 'Default'
  Ninja = 'Ninja'

class CMakeBuilder(AbstractBuilder):
  _defineProviders: List[AbstractCMakeDefineProvider]
  _generator: CMakeGenerator
  _targets: List[str]
  _srcDir: Path
  _buildDir: Path
  _installDir: Optional[Path]
  # If set None, path to cmake will be found out from $PATH
  _customCMakePath: Optional[Path]
  _buildTargets: List[str]
  _initialCache: Optional[Path]

  def __init__(self, srcDir: Path, buildDir: Path) -> None:
    super().__init__()
    self._defineProviders = []
    self._generator = CMakeGenerator.Ninja
    self._targets = []
    self._srcDir = srcDir
    self._buildDir = buildDir
    self._installDir = None
    self._customCMakePath = None
    self._buildTargets = []
    self._initialCache = None

  def getSrcDir(self) -> Path:
    return self._srcDir

  def getBuildDir(self) -> Path:
    return self._buildDir

  def getInstallDir(self) -> Optional[Path]:
    return self._installDir

  def setInstallDir(self, installDir: Path) -> None:
    self._installDir = installDir

  def setGenerator(self, generator: CMakeGenerator) -> None:
    self._generator = generator

  def setCustomCMakePath(self, cmakePath: Path) -> None:
    self._customCMakePath = cmakePath

  def setInitialCache(self, cache: Path) -> None:
    self._initialCache = cache

  def addDefineProvider(self, defineProvider: AbstractCMakeDefineProvider) -> None:
    self._defineProviders.append(defineProvider)

  def _findCMake(self) -> Optional[Path]:
    '''Return resolved cmake path or None if no cmake is found'''
    if not self._customCMakePath:
      cmakePath = shutil.which('cmake')
      return None if not cmakePath else Path(cmakePath).resolve()
    if not self._customCMakePath.exists() or \
       not self._customCMakePath.is_file():
      return None
    else:
      return self._customCMakePath.resolve()

  def _findCMakeOrRaise(self) -> Path:
    cmakePath = self._findCMake()
    if cmakePath is None:
      raise RuntimeError('cannot find cmake')
    return cmakePath

  @classmethod
  def _addQuoteIfNecessary(cls, option: str) -> str:
    '''This function is not necessarily needed, but it improves readability of
       command line options'''
    if ' ' not in option:
      return option
    return f"'{option}'"

  @classmethod
  def _convertCommandToStr(cls, *args: str, indentLevel=4) -> str:
    if len(args) == 0:
      return ''
    if len(args) == 1:
      return cls._addQuoteIfNecessary(args[0])

    strStream = StringIO()
    strStream.write(args[0])
    indent = ' ' * indentLevel
    for arg in args[1:]:
      strStream.write(' \\')
      strStream.write(os.linesep)
      strStream.write(indent)
      strStream.write(cls._addQuoteIfNecessary(arg))
    return strStream.getvalue()

  def _doConfig(self) -> None:
    cmakePath = self._findCMakeOrRaise()
    FileSystemHelper.check_dir(self._srcDir)
    FileSystemHelper.create_dir(self._buildDir)
    args: List[str] = [
      str(cmakePath),
      '-S', str(self._srcDir),
      '-B', str(self._buildDir),
    ]
    if self._generator is not CMakeGenerator.Default:
      args.append('-G')
      args.append(self._generator.value)
    if self._initialCache:
      FileSystemHelper.check_file(self._initialCache)
      args.append('-C')
      args.append(str(self._initialCache))

    for provider in self._defineProviders:
      args.extend([f'-D{define}' for define in provider.getDefines()])

    self.logger.info('Configuration command is: %s%s',
        os.linesep, self._convertCommandToStr(*args))

    subprocess.check_call(args)

  def configure(self) -> None:
    self.logger.info('Start configuration')
    self._doConfig()

  def _doBuild(self) -> None:
    cmakePath = self._findCMakeOrRaise()
    args: List[str] = [
      str(cmakePath),
      '--build', str(self._buildDir),
    ]
    if self._buildTargets:
      args.append('--target')
      args.extend(self._buildTargets)
    subprocess.check_call(args)

  def build(self) -> None:
    self.logger.info('Start building')
    self._doBuild()

  def _doInstall(self) -> None:
    cmakePath = self._findCMakeOrRaise()
    FileSystemHelper.check_dir(self._buildDir)
    args: List[str] = [
      str(cmakePath),
      '--install',
      str(self._buildDir),
    ]
    if self._installDir:
      FileSystemHelper.create_dir(self._installDir)
      args.append('--prefix')
      args.append(str(self._installDir))
    subprocess.check_call(args)

  def install(self) -> None:
    self.logger.info('Start installation')
    self._doInstall()
