ubuntu_install_package() {
  local sudo_command=$(get_sudo_command)

  ${sudo_command} apt-get update
  ${sudo_command} apt-get install -y $@
}

get_sudo_command() {
  local user_id=$(id -u)
  local sudo_command="sudo"

  if [[ ${user_id} == "0" ]]; then
    sudo_command=""
  fi

  echo ${sudo_command}
}
