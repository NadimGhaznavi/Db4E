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

# The pip installed Python environment
PYTHON="[[PYTHON]]"

# The Db4E directory
INSTALL_DIR="[[INSTALL_DIR]]"

# The actual service
$PYTHON $INSTALL_DIR/bin/db4e -s

