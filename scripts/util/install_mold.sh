download_and_install_mold() {
  local version=$1
  local arch=$(uname -m)
  local url_base="https://github.com/wild-linker/wild/releases/download"
  local file_name="wild-linker-${version}-${arch}-unknown-linux-gnu.tar.gz"
  local download_url="${url_base}/${version}/${file_name}"
  local download_path="/tmp/${file_name}"

  echo "Downloading wild linker from ${download_url}..."
  curl -o ${download_path} -L ${download_url}
  mkdir -p /tmp/wild-linker
  # The downloaded archive looks as follows, so one level of path is stripped.
  # wild-linker-0.9.0-x86_64-unknown-linux-gnu/
  # wild-linker-0.9.0-x86_64-unknown-linux-gnu/LICENSE-APACHE
  # wild-linker-0.9.0-x86_64-unknown-linux-gnu/CHANGELOG.md
  # wild-linker-0.9.0-x86_64-unknown-linux-gnu/wild
  # wild-linker-0.9.0-x86_64-unknown-linux-gnu/README.md
  # wild-linker-0.9.0-x86_64-unknown-linux-gnu/LICENSE-MIT
  tar -C /tmp/wild-linker --strip-components=1 -xf ${download_path}
  cp /tmp/wild-linker/wild /usr/bin/wild
  chmod a+x /usr/bin/wild
  # Clang's linking flag `-fuse-ld=wild` needs a binary named `ld.wild`.
  ln -sf /usr/bin/wild /usr/bin/ld.wild
}
