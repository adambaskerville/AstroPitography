#!/bin/bash

_SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
pushd ${_SCRIPT_DIR} # cd to script directory

set -euxo pipefail

echo "Creating virtualenv"

python -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e .[dev] #--constraint pinned-versions/3.10/lockfile.txt


popd # return to original directory
unset _SCRIPT_DIR
