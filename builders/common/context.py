import abc
from typing import Any

from common.compiler import AbstractToolchain

class AbstractBuildingContext(abc.ABC):
  @abc.abstractmethod
  def addArgumentParsing(self, *arg, **kwargs) -> None:
    ...

  @abc.abstractmethod
  def getArgumentValue(self, key: str) -> Any:
    ...

  @abc.abstractmethod
  def registerToolchainFactory(self, name: str, toolchain: AbstractToolchain) -> None:
    ...
