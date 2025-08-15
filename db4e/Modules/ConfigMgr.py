"""
db4e/Modules/ConfigManager.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

import argparse
import sys


class ConfigMgr:
    def __init__(self, app_version: str):
        parser = argparse.ArgumentParser(description="Db4E command line switches")
        parser.add_argument(
            "-v", "--version", action="store_true", help="Print the db4e version.")
        args = parser.parse_args()

        if args.version:
            print(f'Db4e v{app_version}')
            sys.exit(0)


