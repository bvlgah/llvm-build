from pathlib import Path
from typing import final

from llvm_build.toolchain import PosixToolchainBase, ToolchainKind


@final
class LlvmToolchain(PosixToolchainBase):
    def __init__(
        self,
        root_dir: Path,
        bin_dir_name: str | None = "bin",
        target_prefix: str | None = None,
        version_suffix: str | None = None,
    ) -> None:
        super().__init__(
            kind=ToolchainKind.LLVM,
            root_dir=root_dir,
            bin_dir_name=bin_dir_name,
            cc_name="clang",
            cxx_name="clang++",
            ld_name="ld.lld",
            strip_name="llvm-strip",
            target_prefix=target_prefix,
            version_suffix=version_suffix,
        )

    @staticmethod
    def from_exe(exe_path: Path | str) -> "LlvmToolchain":
        root_dir, bin_dir_name = PosixToolchainBase.find_install_dir(
            Path(exe_path),
        )
        return LlvmToolchain(root_dir, bin_dir_name)
