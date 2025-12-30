import abc
from typing import Any

from llvm_build.toolchain import PosixToolchain


class AbstractBuildingContext(abc.ABC):
    @abc.abstractmethod
    def addArgumentParsing(self, *arg, **kwargs) -> None: ...

    @abc.abstractmethod
    def getArgumentValue(self, key: str) -> Any: ...

    @abc.abstractmethod
    def registerToolchainFactory(
        self,
        name: str,
        toolchain: PosixToolchain,
    ) -> None: ...
