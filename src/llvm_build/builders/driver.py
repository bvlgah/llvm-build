import logging
import os
import shutil
import subprocess
import sys
from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from pathlib import Path
from typing import Annotated, Any

import yaml
from pydantic import AfterValidator, BaseModel, ConfigDict

from llvm_build.common.adaptors import (
    CompilerOptionDefineProvider,
    ToolchainDefineProvider,
)
from llvm_build.common.base_builders import (
    AbstractBuilder,
    BuilderKind,
    CMakeBuilder,
    TimedBuilder,
)
from llvm_build.common.compiler import (
    AbstractCompilerOption,
    CompilerOption,
)
from llvm_build.common.define_providers import (
    CMakeDefineProviderAggregate,
    CustomCMakeDefineProvider,
)
from llvm_build.common.utils import FileSystemHelper
from llvm_build.toolchain import PosixToolchain, ToolchainKind
from llvm_build.toolchain.gnu import GnuToolchain
from llvm_build.toolchain.llvm import LlvmToolchain


def _doResolvePath(path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    else:
        rootDir = Path(os.path.dirname(__file__)) / ".."
        return (rootDir / path).resolve()


def _resolvePath(path: Path | None) -> Path | None:
    if path is None:
        return None
    return _doResolvePath(path)


class _CompilerOptionConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    cflags: list[str] = []
    cxxflags: list[str] = []
    ldflags: list[str] = []


_NullableProjectRootBasedPath = Annotated[
    Path | None, AfterValidator(_resolvePath)
]
_NonNullableProjectRootBasedPath = Annotated[
    Path, AfterValidator(_doResolvePath)
]


class _ToolchainConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: ToolchainKind
    installDir: _NullableProjectRootBasedPath = None
    targetPrefix: str | None = None
    versionSuffix: str | None = None


class _BuildToolConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: BuilderKind
    customConfigureOptions: dict[str, str] = dict()
    customBuildOptions: dict[str, str] = dict()
    customInstallOptions: dict[str, str] = dict()


class _ProjectConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    description: str = ""
    srcDir: _NonNullableProjectRootBasedPath
    buildDir: _NonNullableProjectRootBasedPath
    installDir: _NullableProjectRootBasedPath = None
    packagePathPrefix: _NullableProjectRootBasedPath = None
    compilerOption: _CompilerOptionConfig | None = None
    buildTool: _BuildToolConfig
    toolchain: _ToolchainConfig


def _assembleCompilerOption(
    projectConfig: _ProjectConfig,
) -> AbstractCompilerOption | None:
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


def _preloadCMakeOptions(
    builder: CMakeBuilder, config: _BuildToolConfig
) -> None:
    if "initialCache" in config.customConfigureOptions:
        cachePath = _doResolvePath(
            Path(config.customConfigureOptions["initialCache"])
        )
        FileSystemHelper.check_file(cachePath)
        builder.setInitialCache(cachePath)
        config.customConfigureOptions.pop("initialCache")


def _assembleCMakeBuilder(
    projectConfig: _ProjectConfig,
    toolchain: PosixToolchain,
    compilerOption: AbstractCompilerOption | None,
) -> CMakeBuilder:
    builder = CMakeBuilder(projectConfig.srcDir, projectConfig.buildDir)
    _preloadCMakeOptions(builder, projectConfig.buildTool)
    defineAggregate = CMakeDefineProviderAggregate()
    defineAggregate.addProvider(ToolchainDefineProvider(toolchain))

    if compilerOption is not None:
        defineAggregate.addProvider(
            CompilerOptionDefineProvider(compilerOption)
        )

    if projectConfig.installDir is not None:
        builder.setInstallDir(projectConfig.installDir)

    if projectConfig.buildTool.customConfigureOptions:
        customDefineProvider = CustomCMakeDefineProvider()
        for (
            key,
            value,
        ) in projectConfig.buildTool.customConfigureOptions.items():
            customDefineProvider.addDefine(key, value)
        defineAggregate.addProvider(customDefineProvider)
    builder.setDefineProvider(defineAggregate)
    return builder


def _find_toolchain_install_dir(config: _ProjectConfig) -> Path:
    compiler_base_name: str
    match config.toolchain.name:
        case ToolchainKind.GNU:
            compiler_base_name = "gcc"
        case ToolchainKind.LLVM:
            compiler_base_name = "clang"
        case _:
            raise RuntimeError(f"unknown toolchain: {config.toolchain.name}")

    # Prepend target prefix (e.g., `aarch64-linux-gnu`) and append version
    # suffix (such as `21`) if specified.
    compiler_name = compiler_base_name
    if config.toolchain.targetPrefix:
        compiler_name = config.toolchain.targetPrefix + "-" + compiler_name
    if config.toolchain.versionSuffix:
        compiler_name = compiler_name + "-" + config.toolchain.versionSuffix

    compiler_path_str = shutil.which(compiler_name)
    if compiler_path_str is None:
        raise RuntimeError(f"{compiler_name} not found")
    compiler_path = Path(compiler_path_str).resolve()
    assert (compiler_path / "..").resolve().name == "bin", (
        f"expect {compiler_name} located in bin directory"
    )
    return (compiler_path / ".." / "..").resolve()


def _assembleToolchain(config: _ProjectConfig) -> PosixToolchain:
    install_dir = (
        _find_toolchain_install_dir(config)
        if config.toolchain.installDir is None
        else config.toolchain.installDir
    )
    match config.toolchain.name:
        case ToolchainKind.GNU:
            return GnuToolchain(
                root_dir=install_dir,
                target_prefix=config.toolchain.targetPrefix,
                version_suffix=config.toolchain.versionSuffix,
            )
        case ToolchainKind.LLVM:
            return LlvmToolchain(
                root_dir=install_dir,
                target_prefix=config.toolchain.targetPrefix,
                version_suffix=config.toolchain.versionSuffix,
            )
        case _:
            raise RuntimeError(f"unknown toolchain: {config.toolchain.name}")


def _assembleBuilder(projectConfig: _ProjectConfig) -> AbstractBuilder:
    toolchain = _assembleToolchain(projectConfig)
    compilerOption = _assembleCompilerOption(projectConfig)
    if projectConfig.buildTool.name == BuilderKind.CMAKE:
        return _assembleCMakeBuilder(projectConfig, toolchain, compilerOption)
    raise RuntimeError(f"unknow build tool: {projectConfig.buildTool.name}")


def _parseArgs(args: Sequence[str]) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "--src-dir",
        required=False,
        type=Path,
        default=None,
        help="Source code directory",
    )
    parser.add_argument(
        "--build-dir",
        required=False,
        type=Path,
        default=None,
        help="The directory under which compiled object files are store",
    )
    parser.add_argument(
        "--install-dir",
        required=False,
        type=Path,
        default=None,
        help="The directory where libraries, "
        "header files and binaries are installed",
    )
    parser.add_argument(
        "--log-file",
        required=False,
        type=Path,
        default=None,
        help="File to store logs of build tools and compilers",
    )
    parser.add_argument(
        "--quiet",
        required=False,
        action="store_true",
        help="Suppress logging to terminal "
        "(log file will still be created if enabled)",
    )
    parser.add_argument(
        "--config",
        required=True,
        type=Path,
        help="File used to specify building configuration for a project",
    )
    parser.add_argument(
        "--package",
        required=False,
        action="store_true",
        default=False,
        help="File used to specify building configuration for a project",
    )
    parser.add_argument(
        "--no-install",
        required=False,
        action="store_true",
        default=False,
        help="Do not install executables, libraries and headers",
    )
    parser.add_argument(
        "--toolchain-install-dir",
        required=False,
        type=Path,
        default=None,
        help="Directory where the toolchain is located",
    )
    return parser.parse_args(args)


def _config_logging() -> None:
    loggingFormat = (
        "[%(asctime)s %(levelname)s "
        "%(module)s.%(name)s.%(funcName)s] %(message)s"
    )
    logging.basicConfig(format=loggingFormat, level=logging.DEBUG)


def _package(projectConfig: _ProjectConfig) -> None:
    logger = logging.getLogger(__file__)
    logger.info("Start packaging")
    if projectConfig.packagePathPrefix is None:
        raise RuntimeError("Unable to package: no package path is specified")
    if projectConfig.installDir is None:
        raise RuntimeError("Unable to package: install directory not specified")
    FileSystemHelper.check_dir(projectConfig.installDir)
    FileSystemHelper.create_dir(projectConfig.packagePathPrefix / "..")
    FileSystemHelper.check_bin_from_env("xz")
    FileSystemHelper.check_bin_from_env("tar")
    filesToPack = os.listdir(projectConfig.installDir)
    packagePath = f"{projectConfig.packagePathPrefix}.tar.xz"
    args = [
        "tar",
        "-C",
        f"{projectConfig.installDir}",
        "-c",
        "-I",
        "xz -9 -T0",
        "-f",
        f"{packagePath}",
    ]
    args.extend(filesToPack)
    logging.getLogger(__file__).info(
        f"The command to package '{packagePath}' is %s%s",
        os.linesep,
        FileSystemHelper.convertCommandToStr(*args),
    )
    subprocess.check_call(args)


def _modifyProjectConfig(config: dict[str, Any], args: Namespace) -> None:
    if args.src_dir is not None:
        config["srcDir"] = args.src_dir
    if args.build_dir is not None:
        config["buildDir"] = args.build_dir
    if args.install_dir is not None:
        config["installDir"] = args.install_dir
    if args.toolchain_install_dir is not None:
        config["toolchain"]["installDir"] = args.toolchain_install_dir


def main() -> None:
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


if __name__ == "__main__":
    main()
