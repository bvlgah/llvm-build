ubuntu_install_package() {
  local user_id=$(id -u)
  local sudo_command="sudo"

  if [[ ${user_id} == "0" ]]; then
    sudo_command=""
  fi

  ${sudo_command} apt-get update
  ${sudo_command} apt-get install -y $@
}
