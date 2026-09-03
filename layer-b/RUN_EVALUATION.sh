#!/bin/sh
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "$SCRIPT_DIR/wisomega-eval" run --pack cases-shadow-v1 --out "$SCRIPT_DIR/out"
