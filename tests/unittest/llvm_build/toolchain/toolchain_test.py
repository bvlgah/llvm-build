import shutil
import subprocess
from pathlib import Path
from typing import override
from unittest import TestCase

from llvm_build.toolchain import PosixToolchain
from llvm_build.toolchain.gnu import GnuToolchain
from llvm_build.toolchain.llvm import LlvmToolchain


class PosixToolchainTestCase(TestCase):
    _gnu: PosixToolchain | None = None
    _llvm: PosixToolchain | None = None

    @override
    def setUp(self) -> None:
        gcc_path = shutil.which("gcc")
        if gcc_path:
            self._gnu = GnuToolchain.from_exe(gcc_path)
        clang_path = shutil.which("clang")
        if clang_path:
            self._llvm = LlvmToolchain.from_exe(clang_path)

    def _run_exe(self, exe: Path, *args: str) -> None:
        cmd = (str(exe),)
        subprocess.check_call(cmd + args)

    def test_gcc_toolchain(self) -> None:
        if self._gnu is None:
            self.skipTest("GNU toolchain not found")

        for exe in (self._gnu.cc, self._gnu.cxx, self._gnu.ld, self._gnu.strip):
            self._run_exe(exe, "--version")

    def test_llvm_toolchain_20(self) -> None:
        if self._llvm is None:
            self.skipTest("LLVM toolchain not found")

        for exe in (
            self._llvm.cc,
            self._llvm.cxx,
            self._llvm.ld,
            self._llvm.strip,
        ):
            self._run_exe(exe, "--version")
