import functools
from pathlib import Path
import shutil
import subprocess
from toolchains import Toolchain
from typing import Optional
import version


def resolve_clang_install_dir() -> Optional[Path]:
  '''Find out the install dir of clang from env $PATH. For example, clang is
     installed under /usr/lib/llvm-19/bin/clang, then /usr/lib/llvm-19 is
     returned. If clang is not found in $PATH, None is returned.'''
  clang_path = shutil.which("clang")
  if clang_path is None:
    return None
  clang_install_dir = Path(clang_path).resolve() / '../../'
  return clang_install_dir.resolve()

class PlainVersion(version.Version):
  def __init__(self, major: str, minor: str, patch: str):
    self._major = major
    self._minor = minor
    self._patch = patch

  def long_version(self) -> str:
    return '.'.join([self._major, self._minor, self._patch])

  def short_version(self) -> str:
    return '.'.join([self._major, self._minor])

  def major_version(self) -> str:
    return self._major

class ManagedToolchain(Toolchain):
  def _findout_version(self) -> version.Version:
    clang_path = self.cc
    if not clang_path.exists() or not clang_path.is_file():
      raise RuntimeError('clang not found or not executable: ${clang_path}')

    # Expect clang print version information as follows,
    #
    # Ubuntu clang version 19.0.0 (++20240322031428+6f44bb771789-1~exp1~20240322151551.1573)
    # Target: x86_64-pc-linux-gnu
    # Thread model: posix
    # InstalledDir: /usr/lib/llvm-19/bin
    printed_version = subprocess.check_output(
        args=[str(clang_path), '--version']).decode()
    version_prefix = 'clang version '
    version_prefix_pos = printed_version.find(version_prefix)
    if version_prefix_pos < 0:
      raise RuntimeError('cannot find version of clang')
    version_start_pos = version_prefix_pos + len(version_prefix)
    version_end_pos = printed_version.find(' ', version_start_pos)
    if version_end_pos < 0:
      raise RuntimeError('cannot find version of clang')
    extracted_version = printed_version[version_start_pos:version_end_pos]
    version_parts = extracted_version.split('.')
    if len(version_parts) != 3:
      raise RuntimeError('unknown clang version: {extracted_version}')

    return PlainVersion(version_parts[0], version_parts[1], version_parts[2])

  @functools.cached_property
  def version(self) -> version.Version:
    return self._findout_version()
