from abc import ABCMeta, abstractmethod
from typing import Any

from llvm_build.toolchain import PosixToolchain


class AbstractBuildingContext(metaclass=ABCMeta):
    @abstractmethod
    def add_argument_parsing(self, *arg: str, **kwargs: str) -> None: ...

    @abstractmethod
    def get_argument_value(self, key: str) -> Any: ...

    @abstractmethod
    def register_toolchain_factory(
        self,
        name: str,
        toolchain: PosixToolchain,
    ) -> None: ...
