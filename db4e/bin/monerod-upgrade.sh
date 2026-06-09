#!/bin/bash
#
# bin/monerod-upgrade.sh
#
# Script to run upgrade the Monero blockchain daemon
#
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi 
#    Copyright: (c) 2024-2025 NadimGhaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0
#
#####################################################################

VENV_DIR=$1

if [ -z $VENV_DIR ]; then
    echo "Usage $0 <venv_dir>, exiting..."
    exit 1
fi

INSTALL_DIR=/opt/Db4E
MONEROD_DIR=monerod
BIN_DIR=bin
MONEROD=monerod

MONEROD="$INSTALL_DIR/$MONEROD_DIR/$BIN_DIR/$MONEROD"

VERSION_STR=$($MONEROD --version)
echo $VERSION_STR
