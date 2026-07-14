# LLVM Builder

This repository hosts Python code to build LLVM using CMake and ninja.

## How to use `llvm-build` to build LLVM?

While it is supposed to use `llvm-build` on all platforms supporting LLVM,
Cmake, and Ninja, we only have tested it on Ubuntu 24.04 and 26.04 (see
[build-and-test-llvm](https://gitlab.com/compiler2462701/llvm-build/-/blob/5fa5549a202ee5a21d4e1fabc9727b85778e1e78/.gitlab-ci.yml#L36-77)).
Therefore, it is preferrable to use it on these systems. The following
paragraphs gives the instructions of using `llvm-build` on the supported Ubuntu
verions.

First off, you need to clone either [our LLVM repo](https://gitlab.com/compiler2462701/llvm.git)
or [upstream LLVM](https://github.com/llvm/llvm-project). For example, using our
downstream version,

```bash
# First, create a directory, if necessary, and go into it.
# Clone our downstream version of LLVM.
$ git clone https://gitlab.com/compiler2462701/llvm.git llvm-project
# Clone this repo.
$ git clone https://gitlab.com/compiler2462701/llvm-build.git llvm-build
```

Secondly, install `uv` and create a virtual Python environment, given that you
have already had appropriate Python versions (3.12+).

```bash
$ cd llvm-build
$ pip3 install uv
$ python3 -m venv --prompty rlis .env
```

Moreover, install `llvm-build` into the virtual environment with the option `-e`
([editable mode](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-e)).

```bash
$ . .env/bin/activate
$ (rlis) uv pip install -e .
```

Finally, install the dependencies reuqired for the building and invoke
`llvm-build`.

```bash
# Install the compilation toolchain, including `clang`, `cmake`, and `ninja`.
$ (rlis) ./scripts/ubuntu/install_build.sh
# Assume you are currently in the root source directory of `llvm-build`, and
# that of LLVM is `../llvm-project`. Besides, you need to adjust
# `${LLVM_BUILD_DIR}` and `${LLVM_INSTALL_DIR}` accordingly, which represent
# the build and install directories respectively.
$ (rlis) llvm-build \
    --config config/inst-sched/llvm-debug.yaml \
    --src-dir ../llvm-project/llvm \
    --build-dir "${LLVM_BUILD_DIR}" \
    --install-dir "${LLVM_INSTALL_DIR}"
```

On success, LLVM should have been built under `${LLVM_BUILD_DIR}` and installed
to `${LLVM_INSTALL_DIR}`.
