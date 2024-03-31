from enum import Enum

class ToolchainKind(str, Enum):
  gcc = 'gcc'
  clang = 'clang'
