#!/usr/bin/env bash
set -ex
root_dir=$(cd $(dirname $0)/../ && pwd)
export PYTHONPATH=$root_dir/builders:$PYTHONPATH
python -m driver $@
