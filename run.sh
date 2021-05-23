#!/bin/bash
set -euxo pipefail

source $HOME/.poetry/env
cd "${0%/*}"

POETRY_PATH=$(poetry env info -p)
POETRY_BIN="$POETRY_PATH/bin"
SCRIPT="$POETRY_BIN/start"

eval $SCRIPT
