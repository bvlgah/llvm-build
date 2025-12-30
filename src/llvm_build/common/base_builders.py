import abc
import datetime
import os
import shutil
import subprocess
from contextlib import contextmanager
from enum import StrEnum
from pathlib import Path

from llvm_build.common.utils import FileSystemHelper, LoggerMixin


class BuilderKind(StrEnum):
    CMAKE = "cmake"


class AbstractBuilder(abc.ABC, LoggerMixin):
    @abc.abstractmethod
    def configure(self) -> None: ...

    @abc.abstractmethod
    def build(self) -> None: ...

    @abc.abstractmethod
    def install(self) -> None: ...


class TimedBuilder(AbstractBuilder):
    _builder: AbstractBuilder

    @contextmanager
    def _timingContext(self, processName: str):
        startTimestamp = datetime.datetime.now()
        try:
            yield
        finally:
            endTimestamp = datetime.datetime.now()
            timeDiff = endTimestamp - startTimestamp
            self.logger.info(
                "%s took %s seconds", processName, timeDiff.total_seconds()
            )

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
    def getDefines(self) -> dict[str, str]: ...


class CMakeGenerator(StrEnum):
    """Enum class representing CMake generators. Currently, there are two enums,
    Default and Ninja. The Default generator is system-dependent."""

    DDEFAULT = "Default"
    NINJA = "Ninja"


class CMakeBuilder(AbstractBuilder):
    _defineProvider: AbstractCMakeDefineProvider | None
    _generator: CMakeGenerator
    _targets: list[str]
    _srcDir: Path
    _buildDir: Path
    _installDir: Path | None
    # If set None, path to cmake will be found out from $PATH
    _customCMakePath: Path | None
    _buildTargets: list[str]
    _initialCache: Path | None

    def __init__(self, srcDir: Path, buildDir: Path) -> None:
        super().__init__()
        self._defineProvider = None
        self._generator = CMakeGenerator.NINJA
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

    def getInstallDir(self) -> Path | None:
        return self._installDir

    def setInstallDir(self, installDir: Path) -> None:
        self._installDir = installDir

    def setGenerator(self, generator: CMakeGenerator) -> None:
        self._generator = generator

    def setCustomCMakePath(self, cmakePath: Path) -> None:
        self._customCMakePath = cmakePath

    def setInitialCache(self, cache: Path) -> None:
        self._initialCache = cache

    def setDefineProvider(
        self, defineProvider: AbstractCMakeDefineProvider
    ) -> None:
        self._defineProvider = defineProvider

    def _findCMake(self) -> Path | None:
        """Return resolved cmake path or None if no cmake is found"""
        if not self._customCMakePath:
            cmakePath = shutil.which("cmake")
            return None if not cmakePath else Path(cmakePath).resolve()
        if (
            not self._customCMakePath.exists()
            or not self._customCMakePath.is_file()
        ):
            return None
        else:
            return self._customCMakePath.resolve()

    def _findCMakeOrRaise(self) -> Path:
        cmakePath = self._findCMake()
        if cmakePath is None:
            raise RuntimeError("cannot find cmake")
        return cmakePath

    def _doConfig(self) -> None:
        cmakePath = self._findCMakeOrRaise()
        FileSystemHelper.check_dir(self._srcDir)
        FileSystemHelper.create_dir(self._buildDir)
        args: list[str] = [
            str(cmakePath),
            "-S",
            str(self._srcDir),
            "-B",
            str(self._buildDir),
        ]
        if self._generator is not CMakeGenerator.DDEFAULT:
            args.append("-G")
            args.append(self._generator.value)
        if self._initialCache:
            FileSystemHelper.check_file(self._initialCache)
            args.append("-C")
            args.append(str(self._initialCache))

        if self._defineProvider is not None:
            for key, value in self._defineProvider.getDefines().items():
                args.append(f"-D{key}={value}")

        self.logger.info(
            "Configuration command is: %s%s",
            os.linesep,
            FileSystemHelper.convertCommandToStr(*args),
        )

        subprocess.check_call(args)

    def configure(self) -> None:
        self.logger.info("Start configuration")
        self._doConfig()

    def _doBuild(self) -> None:
        cmakePath = self._findCMakeOrRaise()
        args: list[str] = [
            str(cmakePath),
            "--build",
            str(self._buildDir),
        ]
        if self._buildTargets:
            args.append("--target")
            args.extend(self._buildTargets)
        subprocess.check_call(args)

    def build(self) -> None:
        self.logger.info("Start building")
        self._doBuild()

    def _doInstall(self) -> None:
        cmakePath = self._findCMakeOrRaise()
        FileSystemHelper.check_dir(self._buildDir)
        args: list[str] = [
            str(cmakePath),
            "--install",
            str(self._buildDir),
        ]
        if self._installDir:
            FileSystemHelper.create_dir(self._installDir)
            args.append("--prefix")
            args.append(str(self._installDir))
        subprocess.check_call(args)

    def install(self) -> None:
        self.logger.info("Start installation")
        self._doInstall()
