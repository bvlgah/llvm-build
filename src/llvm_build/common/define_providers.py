from llvm_build.common.base_builders import AbstractCMakeDefineProvider
from llvm_build.common.cmake import CMakeBuildType


class CMakeDefineProviderAggregate(AbstractCMakeDefineProvider):
    _providers: list[AbstractCMakeDefineProvider]

    def __init__(self) -> None:
        super().__init__()
        self._providers = []

    def addProvider(self, provider: AbstractCMakeDefineProvider) -> None:
        self._providers.append(provider)

    @staticmethod
    def _concatDefine(key: str, oldValue: str, newValue) -> str:
        connector: str
        if key in (
            "CMAKE_C_FLAGS",
            "CMAKE_CXX_FLAGS",
            "CMAKE_EXE_LINKER_FLAGS",
            "CMAKE_MODULE_LINKER_FLAGS",
            "CMAKE_SHARED_LINKER_FLAGS",
        ):
            connector = " "
        else:
            connector = ";"
        return oldValue + connector + newValue

    def getDefines(self) -> dict[str, str]:
        defines: dict[str, str] = dict()
        for provider in self._providers:
            for key, value in provider.getDefines().items():
                if key in defines:
                    defines[key] = self._concatDefine(key, defines[key], value)
                else:
                    defines[key] = value
        return defines


class CMakeBuildTypeProvider(AbstractCMakeDefineProvider):
    _buildType: CMakeBuildType

    def __init__(self, buildType=CMakeBuildType.RELEASE) -> None:
        super().__init__()
        self._buildType = buildType

    def getDefines(self) -> dict[str, str]:
        return {"CMAKE_BUILD_TYPE": self._buildType.value}


class CustomCMakeDefineProvider(AbstractCMakeDefineProvider):
    _defines: dict[str, str]

    def __init__(self) -> None:
        super().__init__()
        self._defines = dict()

    def addDefine(self, key: str, value: str) -> None:
        self._defines[key] = value

    def getDefines(self) -> dict[str, str]:
        return self._defines.copy()
