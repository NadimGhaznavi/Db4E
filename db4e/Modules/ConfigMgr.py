"""
db4e/Modules/ConfigManager.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0
"""

import sys
import argparse

class ConfigMgr:
    def __init__(self, app_version: str):
        parser = argparse.ArgumentParser(description="Db4E command line switches")
        parser.add_argument("-b", "--backup", action="store_true", help="Perform a db4e backup.")
        parser.add_argument("-s", "--service", action="store_true", help="Run db4e as a service.")
        parser.add_argument("-v", "--version", action="store_true", help="Print the db4e version.")
        args = parser.parse_args()

        ini = Config(app_version=app_version)
        if args.backup:
            ini.config['db4e']['op'] = 'run_backup'
        elif args.service:
            ini.config['db4e']['op'] = 'run_daemon'
        elif args.version:
            print(f'Db4e v{app_version}')
            sys.exit(0)
        else:
            ini.config['db4e']['op'] = 'run_ui'
        self.ini = ini

    def get_config(self):
        return self.ini
    
class Config:
    def __init__(self, app_version: str):
        self.config = {
            'db4e': {
                'app_version': app_version,
                'op': "run_ui",
                'api_dir': "api",
                'bin_dir': "bin",
                'conf_dir': "conf",
                'desc': "Database 4 Everything",
                'dev_dir': "dev",
                'log_dir': "logs",
                'process': "db4e.sh",
                'pypi_repository': "https://pypi.org/pypi/db4e/json",
                'refresh_interval': 15,
                'run_dir': "run",
                'service_file': "db4e.service", 
                'setup_script': "db4e-initial-setup.sh",
                'service_install_script': "db4e-install-service.sh",
                'service_log_file': "db4e.log",
                'service_uninstaller': "db4e-uninstall-service.sh",
                'src_dir': "src",
                'systemd_dir': "systemd",
                'template_dir': "tmpl",
                'vendor_dir': "vendor",
            },
            'db': {
                'backup_dir': 'backups',
                'backup_script':'db4e-backup.sh',
                'collection': 'mining',
                'depl_collection': 'depl',
                'log_collection': 'logging',
                # How many days of data to keep in the logging collection
                'log_retention_days': 7,
                'max_backups': 7,
                'metrics_collection': 'metrics',
                'name': 'db4e',
                'port': 27017,
                'retry_timeout': 15,
                'server': 'localhost',
            }
        }


