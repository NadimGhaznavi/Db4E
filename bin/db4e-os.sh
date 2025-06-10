#!/bin/bash
#
# Wrapper for db4e-os.py 

# Assume this file lives in $DB4E_INSTALL_DIR/bin/
BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB4E_DIR="$BIN_DIR/.."

VENV="$DB4E_DIR/venv"
PYTHON="$VENV/bin/python"
MAIN_SCRIPT="$BIN_DIR/db4e-os.py"

# Activate and run
source "$VENV/bin/activate"
exec "$PYTHON" "$MAIN_SCRIPT" "$@"