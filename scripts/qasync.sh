#!/bin/bash
set -euo pipefail

SRC=/opt/qa/db4e/db4e/
DEST=/home/dan/venv_db4e/lib/python3.13/site-packages/db4e/

mkdir -p "$DEST"
rsync -avr --delete \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  "$SRC" "$DEST"
