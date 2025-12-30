import abc


class AbstractCompilerOption(abc.ABC):
    @abc.abstractmethod
    def getCFlags(self) -> list[str]: ...

    @abc.abstractmethod
    def getCXXFlags(self) -> list[str]: ...

    @abc.abstractmethod
    def getLDFlags(self) -> list[str]: ...


class CompilerOption(AbstractCompilerOption):
    _cflags: list[str]
    _cxxflags: list[str]
    _ldflags: list[str]

    def __init__(self) -> None:
        super().__init__()
        self._cflags = []
        self._cxxflags = []
        self._ldflags = []

    def addCFlag(self, cflag: str) -> None:
        self._cflags.append(cflag)

    def addCXXFlag(self, cxxflag: str) -> None:
        self._cxxflags.append(cxxflag)

    def addLDFalg(self, ldflag: str) -> None:
        self._ldflags.append(ldflag)

    def getCFlags(self) -> list[str]:
        return self._cflags.copy()

    def getCXXFlags(self) -> list[str]:
        return self._cxxflags.copy()

    def getLDFlags(self) -> list[str]:
        return self._ldflags.copy()


class CompilerOptionAggregate(AbstractCompilerOption):
    _options: list[AbstractCompilerOption]

    def __init__(self) -> None:
        super().__init__()
        self._options = []

    def addCompilerOptions(self, option: AbstractCompilerOption) -> None:
        self._options.append(option)

    def getCFlags(self) -> list[str]:
        cflags = []
        for option in self._options:
            cflags.extend(option.getCFlags())
        return cflags

    def getCXXFlags(self) -> list[str]:
        cxxflags = []
        for option in self._options:
            cxxflags.extend(option.getCXXFlags())
        return cxxflags

    def getLDFlags(self) -> list[str]:
        ldflags = []
        for option in self._options:
            ldflags.extend(option.getLDFlags())
        return ldflags
