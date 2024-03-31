from argparse import ArgumentParser, Namespace
import logging
import os
from pathlib import Path
import shutil
import sys
from pydantic import BaseModel, ConfigDict
from typing import Any, List, Optional, Sequence
import yaml

from common.adaptors import CompilerOptionDefineProvider, ToolchainDefineProvider
from common.utils import FileSystemHelper

from common.base_builders import AbstractBuilder, BuilderKind, CMakeBuilder, TimedBuilder
from common.compiler import AbstractCompilerOption, AbstractToolchain, CompilerOption
from common.define_providers import CustomCMakeDefineProvider
from toolchain import ToolchainKind
from toolchain.gcc import GCCToolchain
from toolchain.llvm import LLVMToolchain

class _CompilerOptionConfig(BaseModel):
  model_config = ConfigDict(frozen=True)

  cflags: List[str] = []
  cxxflags: List[str] = []
  ldflags: List[str] = []

class _ToolchainConfig(BaseModel):
  model_config = ConfigDict(frozen=True)

  name: ToolchainKind
  installDir: Optional[Path] = None
  targetPrefix: str = ''

class _BuildToolConfig(BaseModel):
  model_config = ConfigDict(frozen=True)

  name: BuilderKind
  customConfigureOptions: List[str] = []
  customBuildOptions: List[str] = []
  customInstallOptions: List[str] = []

class _ProjectConfig(BaseModel):
  model_config = ConfigDict(frozen=True)

  name: str
  description: str = ''
  srcDir: Path
  buildDir: Path
  installDir: Optional[Path] = None
  compilerOption: Optional[_CompilerOptionConfig] = None
  buildTool: _BuildToolConfig
  toolchain: _ToolchainConfig

def _assembleCompilerOption(projectConfig: _ProjectConfig) -> \
    Optional[AbstractCompilerOption]:
  if projectConfig.compilerOption is None:
    return None
  option = CompilerOption()
  for cflag in projectConfig.compilerOption.cflags:
    option.addCFlag(cflag)
  for cxxflag in projectConfig.compilerOption.cxxflags:
    option.addCXXFlag(cxxflag)
  for ldflag in projectConfig.compilerOption.ldflags:
    option.addLDFalg(ldflag)
  return option

def _assembleCMakeBuilder(projectConfig: _ProjectConfig,
    toolchain: AbstractToolchain,
    compilerOption: Optional[AbstractCompilerOption]) -> CMakeBuilder:
  builder = CMakeBuilder(projectConfig.srcDir, projectConfig.buildDir)
  builder.addDefineProvider(ToolchainDefineProvider(toolchain))
  if compilerOption is not None:
    builder.addDefineProvider(CompilerOptionDefineProvider(compilerOption))

  if projectConfig.installDir is not None:
    builder.setInstallDir(projectConfig.installDir)

  if projectConfig.buildTool.customConfigureOptions:
    customDefineProvider = CustomCMakeDefineProvider()
    for define in projectConfig.buildTool.customConfigureOptions:
      customDefineProvider.addDefine(define)
    builder.addDefineProvider(customDefineProvider)
  return builder

def _findCompilerInstallDir(compiler: str) -> Path:
  gcc = shutil.which(compiler)
  if gcc is None:
    raise RuntimeError(f'{compiler} not found')
  gccPath = Path(gcc).resolve()
  assert (gccPath / '..').resolve().name == 'bin', \
      f'expect {compiler} located in bin directory'
  return (gccPath / '..' / '..').resolve()

def _assembleToolchain(projectConfig: _ProjectConfig) -> AbstractToolchain:
  if projectConfig.toolchain.name == ToolchainKind.gcc:
    if projectConfig.toolchain.installDir is None:
      gccName = projectConfig.toolchain.targetPrefix + '-gcc' \
          if projectConfig.toolchain.targetPrefix else 'gcc'
      return GCCToolchain(projectConfig.toolchain.targetPrefix,
          _findCompilerInstallDir(gccName))
    else:
      return GCCToolchain(projectConfig.toolchain.targetPrefix,
          projectConfig.toolchain.installDir)
  if projectConfig.toolchain.name == ToolchainKind.clang:
    if projectConfig.toolchain.installDir is None:
      return LLVMToolchain(_findCompilerInstallDir('clang'))
    else:
      return LLVMToolchain(projectConfig.toolchain.installDir)
  raise RuntimeError('unknown toolchain: f{projectConfig.toolchain.name}')

def _assembleBuilder(projectConfig: _ProjectConfig) -> AbstractBuilder:
  toolchain = _assembleToolchain(projectConfig)
  compilerOption = _assembleCompilerOption(projectConfig)
  if projectConfig.buildTool.name == BuilderKind.cmake:
    return _assembleCMakeBuilder(projectConfig, toolchain, compilerOption)
  raise RuntimeError(f'unknow build tool: {projectConfig.buildTool.name}')

def _parseArgs(args: Sequence[str]) -> Namespace:
  parser = ArgumentParser()
  parser.add_argument('--src-dir', required=False, type=Path, default=None,
      help='Source code directory')
  parser.add_argument('--build-dir', required=False, type=Path, default=None,
      help='The directory under which compiled object files are store')
  parser.add_argument('--install-dir', required=False, type=Path, default=None,
      help='The directory where libraries, '
           'header files and binaries are installed')
  parser.add_argument('--log-file', required=False, type=Path, default=None,
      help='File to store logs of build tools and compilers')
  parser.add_argument('--quiet', required=False, action='store_true',
      help='Suppress logging to terminal '
           '(log file will still be created if enabled)')
  parser.add_argument('--config', required=True, type=Path,
      help='File used to specify building configuration for a project')
  return parser.parse_args(args)

def _resolvePath(path: Path) -> Path:
  if path.is_absolute():
    return path.resolve()
  else:
    rootDir = Path(os.path.dirname(__file__))
    return (rootDir / path).resolve()

def _modifyConfig(projectConfig: Any, args: Namespace) -> None:
  if args.src_dir:
    projectConfig['srcDir'] = _resolvePath(args.src_dir)
  if args.build_dir:
    projectConfig['buildDir'] = _resolvePath(args.build_dir)
  if args.install_dir:
    projectConfig['installDir'] = _resolvePath(args.install_dir)

def _config_logging():
  loggingFormat = '[%(asctime)s %(levelname)s ' \
      '%(module)s.%(name)s.%(funcName)s] %(message)s'
  logging.basicConfig(format=loggingFormat, level=logging.DEBUG)

def _main() -> None:
  _config_logging()
  parsedCmdArgs = _parseArgs(sys.argv[1:])
  FileSystemHelper.check_file(parsedCmdArgs.config)
  with open(parsedCmdArgs.config) as configFile:
    config = yaml.safe_load(configFile)
  _modifyConfig(config, parsedCmdArgs)
  projectConfig = _ProjectConfig(**config)
  builder = TimedBuilder(_assembleBuilder(projectConfig))
  builder.configure()
  builder.build()
  builder.install()

if __name__ == '__main__':
  _main()
