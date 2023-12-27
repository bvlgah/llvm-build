set -ex
build_deps=('clang' 'lld' 'ninja-build' 'cmake' 'ccache')
user_id=$(id -u)

if [[ ${user_id} == '0' ]]; then
  sudo_command=''
else
  sudo_command='sudo'
fi

${sudo_command} apt-get update
${sudo_command} apt-get install -y ${build_deps[@]}
