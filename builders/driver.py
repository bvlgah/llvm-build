from argparse import ArgumentParser, Namespace
import logging
import os
from pathlib import Path
import shutil
import subprocess
import sys
from pydantic import AfterValidator, BaseModel, ConfigDict
from typing import Annotated, Any, Dict, List, Optional, Sequence
import yaml

from common.adaptors import CompilerOptionDefineProvider, ToolchainDefineProvider
from common.utils import FileSystemHelper

from common.base_builders import AbstractBuilder, BuilderKind, CMakeBuilder, TimedBuilder
from common.compiler import AbstractCompilerOption, AbstractToolchain, CompilerOption
from common.define_providers import CMakeDefineProviderAggregate, CustomCMakeDefineProvider
from toolchain import ToolchainKind
from toolchain.gcc import GCCToolchain
from toolchain.llvm import LLVMToolchain

def _doResolvePath(path: Path) -> Path:
  if path.is_absolute():
    return path.resolve()
  else:
    rootDir = Path(os.path.dirname(__file__)) / '..'
    return (rootDir / path).resolve()

def _resolvePath(path: Optional[Path]) -> Optional[Path]:
  if path is None:
    return None
  return _doResolvePath(path)

class _CompilerOptionConfig(BaseModel):
  model_config = ConfigDict(frozen=True)

  cflags: List[str] = []
  cxxflags: List[str] = []
  ldflags: List[str] = []

_NullableProjectRootBasedPath = Annotated[Optional[Path],
    AfterValidator(_resolvePath)]
_NonNullableProjectRootBasedPath = Annotated[Path,
    AfterValidator(_doResolvePath)]

class _ToolchainConfig(BaseModel):
  model_config = ConfigDict(frozen=True)

  name: ToolchainKind
  installDir: _NullableProjectRootBasedPath = None
  targetPrefix: str = ''

class _BuildToolConfig(BaseModel):
  model_config = ConfigDict(frozen=True)

  name: BuilderKind
  customConfigureOptions: Dict[str, str] = dict()
  customBuildOptions: Dict[str, str] = dict()
  customInstallOptions: Dict[str, str] = dict()

class _ProjectConfig(BaseModel):
  model_config = ConfigDict(frozen=True)

  name: str
  description: str = ''
  srcDir: _NonNullableProjectRootBasedPath
  buildDir: _NonNullableProjectRootBasedPath
  installDir: _NullableProjectRootBasedPath = None
  packagePathPrefix: _NullableProjectRootBasedPath = None
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

def _preloadCMakeOptions(builder: CMakeBuilder, config: _BuildToolConfig):
  if 'initialCache' in config.customConfigureOptions:
    cachePath = _doResolvePath(
        Path(config.customConfigureOptions['initialCache']))
    FileSystemHelper.check_file(cachePath)
    builder.setInitialCache(cachePath)
    config.customConfigureOptions.pop('initialCache')

def _assembleCMakeBuilder(projectConfig: _ProjectConfig,
    toolchain: AbstractToolchain,
    compilerOption: Optional[AbstractCompilerOption]) -> CMakeBuilder:
  builder = CMakeBuilder(projectConfig.srcDir, projectConfig.buildDir)
  _preloadCMakeOptions(builder, projectConfig.buildTool)
  defineAggregate = CMakeDefineProviderAggregate()
  defineAggregate.addProvider(ToolchainDefineProvider(toolchain))

  if compilerOption is not None:
    defineAggregate.addProvider(CompilerOptionDefineProvider(compilerOption))

  if projectConfig.installDir is not None:
    builder.setInstallDir(projectConfig.installDir)

  if projectConfig.buildTool.customConfigureOptions:
    customDefineProvider = CustomCMakeDefineProvider()
    for (key, value) in projectConfig.buildTool.customConfigureOptions.items():
      customDefineProvider.addDefine(key, value)
    defineAggregate.addProvider(customDefineProvider)
  builder.setDefineProvider(defineAggregate)
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
  parser.add_argument('--package', required=False, action='store_true',
      default=False,
      help='File used to specify building configuration for a project')
  parser.add_argument('--no-install', required=False, action='store_true',
      default=False, help='Do not install executables, libraries and headers')
  parser.add_argument('--toolchain-install-dir', required=False, type=Path,
      default=None, help='Directory where the toolchain is located')
  return parser.parse_args(args)

def _config_logging():
  loggingFormat = '[%(asctime)s %(levelname)s ' \
      '%(module)s.%(name)s.%(funcName)s] %(message)s'
  logging.basicConfig(format=loggingFormat, level=logging.DEBUG)

def _package(projectConfig: _ProjectConfig) -> None:
  logger = logging.getLogger(__file__)
  logger.info('Start packaging')
  if projectConfig.packagePathPrefix is None:
    raise RuntimeError('Unable to package: no package path is specified')
  if projectConfig.installDir is None:
    raise RuntimeError('Unable to package: install directory not specified')
  FileSystemHelper.check_dir(projectConfig.installDir)
  FileSystemHelper.create_dir(projectConfig.packagePathPrefix / '..')
  FileSystemHelper.check_bin_from_env('xz')
  FileSystemHelper.check_bin_from_env('tar')
  filesToPack = os.listdir(projectConfig.installDir)
  packagePath = f'{projectConfig.packagePathPrefix}.tar.xz'
  args = [
    'tar', '-C', f'{projectConfig.installDir}',
    '-c', '-I', 'xz -9 -T0', '-f', f'{packagePath}',
  ]
  args.extend(filesToPack)
  logging.getLogger(__file__).info(
      f"The command to package '{packagePath}' is %s%s", os.linesep,
      FileSystemHelper.convertCommandToStr(*args))
  subprocess.check_call(args)

def _modifyProjectConfig(config: Dict[str, Any],
                         args: Namespace) -> None:
  if args.src_dir is not None:
    config['srcDir'] = args.src_dir
  if args.build_dir is not None:
    config['buildDir'] = args.build_dir
  if args.install_dir is not None:
    config['installDir'] = args.install_dir
  if args.toolchain_install_dir is not None:
    config['toolchain']['installDir'] = args.toolchain_install_dir

def _main() -> None:
  _config_logging()
  parsedCmdArgs = _parseArgs(sys.argv[1:])
  FileSystemHelper.check_file(parsedCmdArgs.config)
  with open(parsedCmdArgs.config) as configFile:
    config = yaml.safe_load(configFile)
  _modifyProjectConfig(config, parsedCmdArgs)
  projectConfig = _ProjectConfig(**config)
  builder = TimedBuilder(_assembleBuilder(projectConfig))
  builder.configure()
  builder.build()
  if not parsedCmdArgs.no_install:
    builder.install()
  if parsedCmdArgs.package:
    _package(projectConfig)

if __name__ == '__main__':
  _main()
