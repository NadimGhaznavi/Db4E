# db4e/Modules/ArgumentParser.py
#
#   Database 4 Everything
#   Author: Nadim-Daniel Ghaznavi 
#   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
#   License: GPL 3.0import argparse

import sys
import argparse
from dataclasses import dataclass, field
from typing import Optional

class ArgumentParser:
    def __init__(self, app_version: str):
        self.config = {}
        parser = argparse.ArgumentParser(description='Db4E command line switches')
        parser.add_argument('-b', '--backup', action='store_true', help='Perform a db4e backup.')
        parser.add_argument('-s', '--service', action='store_true', help='Run db4e as a service.')
        parser.add_argument('-v', '--version', action='store_true', help='Print the db4e version.')        
        args = parser.parse_args()
        if args.backup:
            self.config['op'] = 'run_backup'
        elif args.service:
            self.config['op'] = 'run_daemon'
        elif args.version:
            print(f'Db4e v{app_version}')
        else:
            self.config['op'] = 'run_ui'

    def get_config(self):
        return self.config
    
@dataclass
class Config:
    app_version: str
    op: str = "run_ui"
    daemon_mode: bool = False
    daemon_mode_log_file: str = "db4e.log"
    pypi_repository: str = "https://pypi.org/pypi/db4e/json"
    refresh_interval: int = 15
    api_dir: str = "api"
    bin_dir: str = "bin"
    conf_dir: str = "conf"
    desc: str = "Database 4 Everything"
    dev_dir: str = "dev"
    log_dir: str = "logs"
    process: str = "db4e.sh"
    run_dir: str = "run"
    service_file: str = "db4e.service"
    setup_script: str = "db4e-initial-setup.sh"
    service_uninstaller: str = "db4e-uninstall-service.sh"
    service_install_script: str = "db4e-install-service.sh"
    src_dir: str = "src"
    systemd_dir: str = "systemd"
    template_dir: str = "tmpl"
    vendor_dir: str = "vendor"

def get_cli_args(app_version: str) -> Config:
    parser = argparse.ArgumentParser(description="Db4E command line switches")
    parser.add_argument("-b", "--backup", action="store_true", help="Perform a db4e backup.")
    parser.add_argument("-s", "--service", action="store_true", help="Run db4e as a service.")
    parser.add_argument("-v", "--version", action="store_true", help="Print the db4e version.")
    args = parser.parse_args()

    if args.version:
        print(f"Db4E v{app_version}")
        sys.exit(0)

    op = "run_ui"
    if args.backup:
        op = "run_backup"
    elif args.service:
        op = "run_daemon"

    return Config(app_version=app_version, op=op)

