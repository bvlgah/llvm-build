from enum import Enum
import logging
from typing import Sequence

class LoggerMixin:
  @property
  def logger(self) -> logging.Logger:
    return logging.getLogger(self.__class__.__name__)

class StrValueEnum(Enum):

  @classmethod
  def values(cls) -> Sequence[str]:
    return [ e.value for e in cls ]
