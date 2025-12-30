from enum import StrEnum


class LLVMProject(StrEnum):
    CLANG = "clang"
    CLANG_TOOLS_EXTRA = "clang-tools-extra"
    CROSS_PROJECT_TESTS = "cross-project-tests"
    FLANG = "flang"
    LIBC = "libc"
    LIBCLC = "libclc"
    LLD = "lld"
    LLDB = "lldb"
    MLIR = "mlir"
    OPENMP = "openmp"
    POLLY = "polly"
    PSTL = "pstl"

    ALL = "all"


class LLVMRuntime(StrEnum):
    COMPILER_RT = "compiler-rt"
    LIBC = "libc"
    LIBCXX = "libcxx"
    LIBCXXABI = "libcxxabi"
    LIBUNWIND = "libunwind"
    OPENMP = "openmp"


class LLVMTarget(StrEnum):
    AARCH64 = "AArch64"
    AMDGPU = "AMDGPU"
    ARM = "ARM"
    AVR = "AVR"
    BPF = "BPF"
    HEXAGON = "Hexagon"
    LANAI = "Lanai"
    MIPS = "Mips"
    MSP430 = "MSP430"
    NVPTX = "NVPTX"
    POWERPC = "PowerPC"
    RISCV = "RISCV"
    SPARC = "Sparc"
    SYSTEMZ = "SystemZ"
    WEBASSEMBLY = "WebAssembly"
    X86 = "X86"
    XCore = "XCore"

    ALL = "all"
    Native = "Native"


class LLVMSanitizer(StrEnum):
    ADDRESS = "Address"
    HWADDRESS = "HWAddress"
    MEMORY = "Memory"
    MEMORY_WITH_ORIGINS = "MemoryWithOrigins"
    UNDEFINED = "Undefined"
    THREAD = "Thread"
    DATA_FLOW = "DataFlow"
    ADDRESS_UNDEFINED = "Address;Undefined"
    LEAKS = "Leaks"
