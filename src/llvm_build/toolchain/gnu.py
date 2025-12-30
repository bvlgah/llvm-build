from pathlib import Path
from typing import final

from llvm_build.toolchain import PosixToolchainBase, ToolchainKind


@final
class GnuToolchain(PosixToolchainBase):
    def __init__(
        self,
        root_dir: Path,
        bin_dir_name: str | None = "bin",
        target_prefix: str | None = None,
        version_suffix: str | None = None,
    ) -> None:
        super().__init__(
            kind=ToolchainKind.GNU,
            root_dir=root_dir,
            bin_dir_name=bin_dir_name,
            cc_name="gcc",
            cxx_name="g++",
            ld_name="ld",
            strip_name="strip",
            target_prefix=target_prefix,
            version_suffix=version_suffix,
        )

    @staticmethod
    def from_exe(exe_path: Path | str) -> "GnuToolchain":
        root_dir, bin_dir_name = PosixToolchainBase.find_install_dir(
            Path(exe_path),
        )
        return GnuToolchain(root_dir, bin_dir_name)
