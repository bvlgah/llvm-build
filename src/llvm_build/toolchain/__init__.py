from abc import ABCMeta, abstractmethod
from enum import StrEnum
from pathlib import Path
from typing import override

from llvm_build.common.utils import FileSystemHelper


class PosixToolchain(metaclass=ABCMeta):
    @property
    @abstractmethod
    def cc(self) -> Path:
        pass

    @property
    @abstractmethod
    def cxx(self) -> Path:
        pass

    @property
    @abstractmethod
    def ld(self) -> Path:
        pass

    @property
    @abstractmethod
    def strip(self) -> Path:
        pass

    @property
    @abstractmethod
    def target_prefix(self) -> str | None:
        pass

    @property
    @abstractmethod
    def version_suffix(self) -> str | None:
        pass

    @property
    @abstractmethod
    def kind(self) -> "ToolchainKind":
        pass


class ToolchainKind(StrEnum):
    GNU = "gnu"
    LLVM = "llvm"


class PosixToolchainBase(PosixToolchain):
    _target_prefix: str | None
    _version_suffix: str | None
    _root_dir: Path
    _cc: Path
    _cxx: Path
    _ld: Path
    _strip: Path
    _kind: ToolchainKind

    def __init__(
        self,
        kind: ToolchainKind,
        root_dir: Path,
        bin_dir_name: str | None,
        cc_name: str,
        cxx_name: str,
        ld_name: str,
        strip_name: str,
        target_prefix: str | None = None,
        version_suffix: str | None = None,
    ) -> None:
        FileSystemHelper.check_dir(root_dir)

        self._kind = kind
        self._root_dir = root_dir.absolute()
        self._target_prefix = target_prefix
        self._version_suffix = version_suffix
        if bin_dir_name:
            exe_dir = self._root_dir / bin_dir_name
        else:
            exe_dir = self._root_dir

        self._cc = PosixToolchainBase._get_exe_path(
            exe_dir,
            cc_name,
            self._target_prefix,
            self._version_suffix,
        )
        self._cxx = PosixToolchainBase._get_exe_path(
            exe_dir,
            cxx_name,
            self._target_prefix,
            self._version_suffix,
        )
        self._ld = PosixToolchainBase._get_exe_path(
            exe_dir,
            ld_name,
            self._target_prefix,
            self._version_suffix,
        )
        self._strip = PosixToolchainBase._get_exe_path(
            exe_dir,
            strip_name,
            self._target_prefix,
            self._version_suffix,
        )

        for binPath in (self._cc, self._cxx, self._ld, self._strip):
            FileSystemHelper.check_file(binPath)

    @staticmethod
    def _get_exe_path(
        exe_dir: Path,
        exe_name: str,
        target_prefix: str | None,
        version_suffix: str | None,
    ) -> Path:
        prefix = ""
        if target_prefix:
            prefix = target_prefix + "-"
        suffix = ""
        if version_suffix:
            suffix = "-" + version_suffix
        bin_path = exe_dir / f"{prefix}{exe_name}{suffix}"
        return bin_path.absolute()

    @property
    @override
    def cc(self) -> Path:
        return self._cc

    @property
    @override
    def cxx(self) -> Path:
        return self._cxx

    @property
    @override
    def ld(self) -> Path:
        return self._ld

    @property
    @override
    def strip(self) -> Path:
        return self._strip

    @property
    @override
    def target_prefix(self) -> str | None:
        return self._target_prefix

    @property
    @override
    def version_suffix(self) -> str | None:
        return self._version_suffix

    @property
    @override
    def kind(self) -> ToolchainKind:
        return self._kind

    @staticmethod
    def find_install_dir(exe_path: Path) -> tuple[Path, str | None]:
        FileSystemHelper.check_file(exe_path)
        exe_dir = exe_path.parent

        if exe_dir.name == "bin":
            return exe_dir.parent, "bin"
        else:
            return exe_dir, None
