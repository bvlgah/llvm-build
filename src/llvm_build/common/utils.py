import logging
import os
import shutil
from io import StringIO
from pathlib import Path


class LoggerMixin:
    @property
    def logger(self) -> logging.Logger:
        return self.classLogger()

    @classmethod
    def classLogger(cls) -> logging.Logger:
        return logging.getLogger(cls.__name__)


class FileSystemHelper(LoggerMixin):
    @classmethod
    def check_dir(cls, dirPath: Path) -> None:
        if not dirPath.exists():
            raise RuntimeError(f"directory does not exit: {dirPath}")
        if not dirPath.is_dir():
            raise RuntimeError(f"not a directory: {dirPath}")

    @classmethod
    def check_file(cls, filePath: Path) -> None:
        if not filePath.exists():
            raise RuntimeError(f"file does not exit: {filePath}")
        if not filePath.is_file():
            raise RuntimeError(f"not a file: {filePath}")

    @classmethod
    def create_dir(cls, dirPath: Path) -> None:
        dirPath = dirPath.resolve()
        if dirPath.exists():
            if dirPath.is_dir():
                cls.classLogger().warning(
                    f"skip creating directory: '{dirPath}' exists"
                )
                return
            else:
                raise RuntimeError(
                    f"failed creating directory '{dirPath}': an existent regular file"
                )
        dirPath.mkdir(parents=True)

    @classmethod
    def check_bin_from_env(cls, binName: str) -> None:
        if shutil.which(binName) is None:
            raise RuntimeError(f"executable file not found: {binName}")

    @classmethod
    def _addQuoteIfNecessary(cls, option: str) -> str:
        """This function is not necessarily needed, but it improves readability of
        command line options"""
        if " " not in option:
            return option
        return f"'{option}'"

    @classmethod
    def convertCommandToStr(cls, *args: str, indentLevel=4) -> str:
        if len(args) == 0:
            return ""
        if len(args) == 1:
            return cls._addQuoteIfNecessary(args[0])

        strStream = StringIO()
        strStream.write(args[0])
        indent = " " * indentLevel
        for arg in args[1:]:
            strStream.write(" \\")
            strStream.write(os.linesep)
            strStream.write(indent)
            strStream.write(cls._addQuoteIfNecessary(arg))
        return strStream.getvalue()
