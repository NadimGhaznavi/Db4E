#!/bin/bash
#
# Shell wrapper script to run the `bin/db4e.py -s` program using 
# the db4e Python venv environment.
#
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi 
#    Copyright: (c) 2024-2025 NadimGhaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0
#
#####################################################################

# Assume this file lives in $DB4E_INSTALL_DIR/bin/
BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB4E_DIR="$BIN_DIR/.."

VENV="$DB4E_DIR/venv"
PYTHON="$VENV/bin/python"
MAIN_SCRIPT="$BIN_DIR/db4e.py -s "

$MAIN_SCRIPT
