from enum import Enum


class CMakeBuildType(Enum):
    DEBUG = "Debug"
    RELEASE = "Release"
    RELEASE_WITH_DEBUG_INFO = "RelWithDebInfo"
    MIN_SIZE_RELEASE = "MinSizeRel"
