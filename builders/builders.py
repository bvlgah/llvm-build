from argparse import ArgumentParser
import gzip
from pathlib import Path
import shutil
import subprocess
import sys
from typing import List, Mapping, Optional, Sequence

from common.cmake import CMakeBuildType
from common.llvm import LLVMProject, LLVMRuntime, LLVMSanitizer, LLVMTarget
from common.utils import StrValueEnum, LoggerMixin

class BuildType(StrValueEnum):
  DEBUG = 'debug'
  REALSE = 'release'

class LLVMBuildOptions(LoggerMixin):
  srcDir: Path = Path('.')
  buildDir: Path = Path('.')
  buildType: BuildType = BuildType.REALSE
  enableAssertions: Optional[bool] = None
  enableProjects: Sequence[LLVMProject] = ()
  enableRuntimes: Sequence[LLVMRuntime] = ()
  buildTargets: Sequence[LLVMTarget] = ()
  useLLD: Optional[bool] = None
  useCcache: Optional[bool] = None
  useSanitizer: Optional[LLVMSanitizer] = None
  buildExamples: Optional[bool] = None
  cc: Optional[str] = None
  cxx: Optional[str] = None

  @classmethod
  def parse(cls, args: Sequence[str]) -> 'LLVMBuildOptions':
    parser = cls._create_parser()
    ns = parser.parse_args(args)
    options = LLVMBuildOptions()
    options.srcDir = ns.srcDir
    options.buildDir = ns.buildDir
    options.buildType = BuildType(ns.buildType)
    options.enableAssertions = ns.enableAssertions
    options.enableProjects = [ LLVMProject(proj) for proj in ns.enableProjects ]
    options.enableRuntimes = [ LLVMRuntime(r) for r in ns.enableRuntimes ]
    options.buildTargets = [ LLVMTarget(t) for t in ns.buildTargets ]
    options.useLLD = ns.useLLD
    options.useCcache = ns.useCcache
    if not ns.useSanitizer is None:
      options.useSanitizer = LLVMSanitizer(ns.useSanitizer)
    options.buildExamples = ns.buildExamples
    options.cc = ns.cc
    options.cxx = ns.cxx
    return options

  @classmethod
  def _create_parser(cls) -> ArgumentParser:
    parser = ArgumentParser()
    # Mult-value options
    parser.add_argument('--build-target', dest='buildTargets', action='append',
      default=[], choices=LLVMTarget.values(), help='LLVM targets to build')
    parser.add_argument('--enable-project', dest='enableProjects', default=[],
      action='append', choices=LLVMProject.values(),
      help='LLVM projects to enable')
    parser.add_argument('--enable-runtime', dest='enableRuntimes', default=[],
      action='append', choices=LLVMRuntime.values(),
      help='LLVM projects to build')
    # Single-value options
    parser.add_argument('--build-type', dest='buildType',
      choices=BuildType.values(), help='build type')
    parser.add_argument('--use-sanitizer', dest='useSanitizer',
      choices=LLVMSanitizer.values(), help='use a sanitizer')
    parser.add_argument('--src-dir', dest='srcDir', required=True, type=Path,
      help='LLVM source directory')
    parser.add_argument('--build-dir', dest='buildDir', required=True,
      type=Path, help='LLVM source directory')
    # Flags
    parser.add_argument('--enable-assertions', dest='enableAssertions',
      action='store_true', help='Enable assertions in LLVM source code',
      default=None)
    parser.add_argument('--use-lld', dest='useLLD', action='store_true',
      help='use LLD as linker, make sure LLD is installed in your $PATH',
      default=None)
    parser.add_argument('--use-ccache', dest='useCcache', action='store_true',
      help='use Ccache, make sure Ccache is installed in your $PATH',
      default=None)
    parser.add_argument('--build-examples', dest='buildExamples',
      action='store_true', help='build LLVM examples', default=None)
    parser.add_argument('--cc', dest='cc', default=None,
      choices=('cc', 'gcc', 'clang'), help='C compiler to use')
    parser.add_argument('--cxx', dest='cxx', default=None,
      choices=('c++', 'g++', 'clang++'), help='C++ compiler to use')
    return parser

def _check_build_tool(toolName: str) -> Path:
  toolPath = shutil.which(toolName)
  if toolPath is None:
    raise RuntimeError(f"build tool '{toolName}' does not exist")
  return Path(toolPath)

def _to_cmake_bool(value: bool) -> str:
  return 'ON' if value else 'OFF'

class LLVMCMakeBuilder(LoggerMixin):
  _build_type_mapping: Mapping = {
    BuildType.DEBUG : CMakeBuildType.DEBUG,
    BuildType.REALSE : CMakeBuildType.RELEASE
  }

  def __init__(self, opts: LLVMBuildOptions):
    self._opts = opts

  def build(self):
    cmakePath = _check_build_tool('cmake')
    ninjaPath = _check_build_tool('ninja')
    self._config_with_cmake(cmakePath)
    self._build_with_ninja(ninjaPath)

  def _to_cmake_build_type(self) -> str:
    return self._build_type_mapping[self._opts.buildType].value

  def _create_build_dir(self, buildDir: Path):
    if buildDir.exists():
      if buildDir.is_dir():
        self.logger.warning(f"build directory '{buildDir}' exists")
        return
      else:
        raise RuntimeError(
          f"path '{buildDir}' exists, but it is a directory")
    buildDir.mkdir(parents=True)

  def _check_src_dir(self, srcDir: Path):
    if not srcDir.exists():
      raise RuntimeError(f"source directory '{srcDir}' does not exist")
    if not srcDir.is_dir():
      raise RuntimeError(f"expect '{srcDir}' is the root directory of LLVM, " \
          'but it is not a directory')

  def _config_with_cmake(self, cmakePath: Path):
    buildDir = self._opts.buildDir.absolute() / self._opts.buildType.value
    srcDir = self._opts.srcDir.absolute()
    self._check_src_dir(srcDir)
    self._create_build_dir(buildDir)
    args: List[str] = [
      '-S', str(srcDir),
      '-B', str(buildDir),
      '-G', 'Ninja',
      f'-DCMAKE_BUILD_TYPE={self._to_cmake_build_type()}',
    ]
    if not self._opts.enableAssertions is None:
      args.append(
        '-DLLVM_ENABLE_ASSERTIONS=' \
        f'{_to_cmake_bool(self._opts.enableAssertions)}')
    cmakeListSep = ';'
    if self._opts.enableProjects:
      projects = str.join(cmakeListSep,
        [ p.value for p in self._opts.enableProjects ])
      args.append(f'-DLLVM_ENABLE_PROJECTS={projects}')
    if self._opts.enableRuntimes:
      runtimes = str.join(cmakeListSep,
        [ r.value for r in self._opts.enableRuntimes ])
      args.append(f'-DLLVM_ENABLE_RUNTIMES={runtimes}')
    if self._opts.buildTargets:
      targets = str.join(cmakeListSep,
        [ t.value for t in self._opts.buildTargets ])
      args.append(f'-DLLVM_TARGETS_TO_BUILD={targets}')
    if not self._opts.useLLD is None:
      args.append(f'-DLLVM_ENABLE_LLD={_to_cmake_bool(self._opts.useLLD)}')
    if not self._opts.useCcache is None:
      args.append(f'-DLLVM_CCACHE_BUILD={_to_cmake_bool(self._opts.useCcache)}')
    if self._opts.useSanitizer:
      args.append(f'-DLLVM_USE_SANITIZER={self._opts.useSanitizer.value}')
    if not self._opts.buildExamples is None:
      args.append(
        f'-DLLVM_BUILD_EXAMPLES={_to_cmake_bool(self._opts.buildExamples)}')
    if not self._opts.cc is None:
      args.append(f'-DCMAKE_C_COMPILER={self._opts.cc}')
    if not self._opts.cxx is None:
      args.append(f'-DCMAKE_CXX_COMPILER={self._opts.cxx}')
    self._write_command_to_file(cmakePath, args, buildDir / 'llvm_config.sh')
    self._launch_binary_and_log(cmakePath, args, buildDir / 'llvm_config.log')

  def _keep_regular_file_if_existent(self, filePath: Path, compressed=False):
    if not filePath.exists():
      return
    if not filePath.is_file():
      raise RuntimeError(f'{filePath}: not a regular file')
    self._rename_file_with_timestamp(filePath, compressed)

  def _rename_file_with_timestamp(self, filePath: Path, compressed: bool):
    unixTimestampStr = str(int(filePath.stat().st_ctime))

    def generate_file_name():
      newSuffix = '.gz' if compressed else ''
      newFileName = filePath.stem + '_' + unixTimestampStr + filePath.suffix + \
        newSuffix;
      yield filePath.parent / newFileName
      count = 1
      while True:
        newFileName = filePath.stem + '_' + unixTimestampStr + f'_{count}' + \
          filePath.suffix + newSuffix
        yield filePath.parent / newFileName

    for newFilePath in generate_file_name():
      if newFilePath.exists():
        continue
      if not compressed:
        filePath.rename(newFilePath)
      else:
        with filePath.open('rb') as uncompressedFile:
          with gzip.open(newFilePath, 'wb') as compressedFile:
            shutil.copyfileobj(uncompressedFile, compressedFile)
        filePath.unlink()
      break

  def _write_command_to_file(self, binFile: Path, args: List[str], shFile: Path):
    indent = 4
    self._keep_regular_file_if_existent(shFile)
    with shFile.open('w') as f:
      f.write(f'{binFile} \\\n')
      for arg in args[:-1]:
        f.write(' ' * indent)
        f.write(f'"{arg}" \\\n')
      if len(args) > 0:
        f.write(' ' * indent)
        f.write(args[-1])

  def _build_with_ninja(self, ninjaPath: Path):
    buildDir = self._opts.buildDir.absolute() / self._opts.buildType.value
    args = ['-C', str(buildDir)]
    self._write_command_to_file(ninjaPath, args, buildDir / 'llvm_build.sh')
    self._launch_binary_and_log(ninjaPath, args, buildDir / 'llvm_build.log')

  def _launch_binary_and_log(
    self, binFile: Path, args: List[str], logFile: Path):
    self._keep_regular_file_if_existent(logFile, True)
    with logFile.open('w') as outErrorFile:
      proc = subprocess.run(args=[ binFile ] + args, stdout=outErrorFile,
        stderr=outErrorFile)
    if proc.returncode != 0:
      with logFile.open('r') as outErrorFile:
        shutil.copyfileobj(outErrorFile, sys.stderr)
      proc.check_returncode()
