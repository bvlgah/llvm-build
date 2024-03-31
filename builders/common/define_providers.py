from typing import List

from common.base_builders import AbstractCMakeDefineProvider
from common.cmake import CMakeBuildType

class CMakeDefineProviderAggregate(AbstractCMakeDefineProvider):
  _providers : List[AbstractCMakeDefineProvider]

  def __init__(self) -> None:
    super().__init__()
    self._providers = []

  def addProvider(self, provider: AbstractCMakeDefineProvider) -> None:
    self._providers.append(provider)

  def getDefines(self) -> List[str]:
    defines: List[str] = []
    for provider in self._providers:
      defines.extend(provider.getDefines())
    return defines

class CMakeBuildTypeProvider(AbstractCMakeDefineProvider):
  _buildType: CMakeBuildType

  def __init__(self, buildType=CMakeBuildType.RELEASE) -> None:
    super().__init__()
    self._buildType = buildType

  def getDefines(self) -> List[str]:
    return [ f'-DCMAKE_BUILD_TYPE={self._buildType}' ]

class CustomCMakeDefineProvider(AbstractCMakeDefineProvider):
  _defines: List[str]

  def __init__(self) -> None:
    super().__init__()
    self._defines = []

  def addDefine(self, define: str) -> None:
    self._defines.append(define)

  def getDefines(self) -> List[str]:
    return self._defines.copy()
