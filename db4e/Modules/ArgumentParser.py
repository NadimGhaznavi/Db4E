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
    api_dir = 'api'
    bin_dir = 'bin'
    conf_dir = 'conf'
    daemon_mode = False
    daemon_mode_log_file = 'db4e.log'
    desc = "Database 4 Everything"
    dev_dir = 'dev'
    log_dir = 'logs'
    op: str = 'run_ui'
    process = 'db4e.sh'
    pypi_repository: str = "https://pypi.org/pypi/db4e/json"
    refresh_interval = 15
    run_dir = 'run'
    service_file = 'db4e.service'
    setup_script = 'db4e-initial-setup.sh'
    service_uninstaller = 'db4e-uninstall-service.sh'
    service_install_script = 'db4e-install-service.sh'
    src_dir = 'src'
    systemd_dir = 'systemd'
    template_dir = 'tmpl'
    vendor_dir = 'vendor'

def create_config_from_args(app_version: str) -> Config:
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

    return Config(app_version=app_version, op=op, daemon_mode=(op == "run_daemon"))

