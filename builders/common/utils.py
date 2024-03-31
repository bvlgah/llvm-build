from enum import Enum
import logging
from pathlib import Path
from typing import Sequence

class LoggerMixin:
  @property
  def logger(self) -> logging.Logger:
    return self.classLogger()

  @classmethod
  def classLogger(cls) -> logging.Logger:
    return logging.getLogger(cls.__name__)

class StrValueEnum(Enum):

  @classmethod
  def values(cls) -> Sequence[str]:
    return [ e.value for e in cls ]

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
      raise RuntimeError(f'file does not exit: {filePath}')
    if not filePath.is_file():
      raise RuntimeError(f'not a file: {filePath}')

  @classmethod
  def create_dir(cls, dirPath: Path) -> None:
    if dirPath.exists():
      if dirPath.is_dir():
        cls.classLogger().warning(
            f"skip creating directory: '{dirPath}' exists")
        return
      else:
        raise RuntimeError(
            f"failed creating directory '{dirPath}': an existent regular file")
    dirPath.mkdir(parents=True)
