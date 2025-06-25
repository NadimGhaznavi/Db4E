#!/bin/bash
#
# Shell wrapper script to run the `bin/db4e-metrics.py` program using 
# the db4e Python venv environment.
#
#####################################################################


#####################################################################
#
#  This file is part of *db4e*, the *Database 4 Everything* project
#  <https://github.com/NadimGhaznavi/db4e>, developed independently
#  by Nadim-Daniel Ghaznavi. Copyright (c) 2024-2025 NadimGhaznavi
#  <https://github.com/NadimGhaznavi/db4e>.
# 
#  This program is free software: you can redistribute it and/or 
#  modify it under the terms of the GNU General Public License as 
#  published by the Free Software Foundation, version 3.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  You should have received a copy (LICENSE.txt) of the GNU General 
#  Public License along with this program. If not, see 
#  <http://www.gnu.org/licenses/>.
#
#####################################################################

# Assume this file lives in $DB4E_INSTALL_DIR/bin/
BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB4E_DIR="$BIN_DIR/.."

VENV="$DB4E_DIR/venv"
PYTHON="$VENV/bin/python"
MAIN_SCRIPT="$BIN_DIR/db4e-metrics.py"

# Make sure the initial setup for db4e has been executed
if [ ! -d $VENV ]; then
    echo "ERROR: Run db4e-os.sh to do the initial db4e setup"
    exit 1
fi

# Activate and run
source "$VENV/bin/activate"
exec "$PYTHON" "$MAIN_SCRIPT" "$@"