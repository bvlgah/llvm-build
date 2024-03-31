set -ex
build_deps=('clang' 'lld' 'ninja-build' 'cmake' 'ccache'
            'gcc-riscv64-linux-gnu' 'g++-riscv64-linux-gnu' 'tar' 'xz-utils'
            'python3' 'python-is-python3' 'python3-pip' 'python3-venv')
user_id=$(id -u)

if [[ ${user_id} == '0' ]]; then
  sudo_command=''
else
  sudo_command='sudo'
fi

${sudo_command} apt-get update
${sudo_command} apt-get install -y ${build_deps[@]}
