#!/bin/bash
#
# Shell wrapper script to run the `bin/db4e.py` program using the
# db4e Python venv environment.
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
MAIN_SCRIPT="$BIN_DIR/db4e.py"

if [ ! -d "$VENV" ]; then
  which python3 > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "ERROR: You must have python3 installed and in your path, exiting"
    exit 1
  fi
  echo "Python venv environment not found, doing a one-time setup..."
  cd "$DB4E_DIR"
  python3 -m venv venv
  echo "Activating virtual environment and installing packages..."
  source "$VENV/bin/activate"
  pip install --upgrade pip

  REQ_FILE="$DB4E_DIR/conf/requirements.txt"
  if [ -f "$REQ_FILE" ]; then
    pip install -r "$REQ_FILE"
  else
    echo "ERROR: Missing Python venv requirements file ($REQ_FILE)."
    echo "ERROR: Your *db4e* clone is broken. Please try cloning again."
    echo
    echo "git clone git@github.com:NadimGhazavi/db4e"
    echo
    echo "exiting..."
    exit 1
  fi
fi

# Activate and run
source "$VENV/bin/activate"
exec "$PYTHON" "$MAIN_SCRIPT" "$@"