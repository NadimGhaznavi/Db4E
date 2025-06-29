"""
lib/Db4eConfig/Db4eConfig.py

This module is responsible for reading the *db4e* settings and parsing
command line arguments.


  This file is part of *db4e*, the *Database 4 Everything* project
  <https://github.com/NadimGhaznavi/db4e>, developed independently
  by Nadim-Daniel Ghaznavi. Copyright (c) 2024-2025 NadimGhaznavi
  <https://github.com/NadimGhaznavi/db4e>.
 
  This program is free software: you can redistribute it and/or 
  modify it under the terms of the GNU General Public License as 
  published by the Free Software Foundation, version 3.
 
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  General Public License for more details.

  You should have received a copy (LICENSE.txt) of the GNU General 
  Public License along with this program. If not, see 
  <http://www.gnu.org/licenses/>.
"""

import yaml
import argparse
import os, sys

YAML_FILE = 'db4e_prod.yml'
YAML_FILE_QA = 'db4e_qa.yml'
        
class Db4eConfig():

    def __init__(self):
        # Read the application configuration file
        conf_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'conf'))
        yaml_file = os.path.join(conf_dir, YAML_FILE)
        self.load(yaml_file)

        # Setup the command line parser
        parser = argparse.ArgumentParser(description='DB4E Configuration')
        
        parser.add_argument('-b', '--backup', action='store_true', help='Perform a db4e backup.')
        parser.add_argument('-e', '--environ', default='prod', help='Run in QA environment with -e qa.')
        parser.add_argument('-m', '--monitor', action='store_true', help='Monitor the P2Pool log.')
        parser.add_argument('-s', '--service', action='store_true', help='Run db4e as a service.')
        parser.add_argument('-w', '--wallet', action='store_true', help='Get the mining wallet balance.')
        parser.add_argument('-v', '--version', action='store_true', help='Print the db4e version.')
        
        
        args = parser.parse_args()

        ### Parse any command line args

        # Print the db4e version and exit
        if args.version:
            version = self.config['db4e']['version']
            print(f'db4e {version}')
            sys.exit(0)

        # This has a default, so its always set.
        self.config['db4e']['environ'] = args.environ
        if args.environ == 'qa':
            # Load the QA environment settings (DB, directories etc)
            self.load(os.path.join(db4e_dir, YAML_FILE_QA))

        # Monitor the P2Pool daemon log files for P2Pool events
        if args.monitor:
            self.config['p2pool']['monitor_log'] = True

        # Return the wallet balance that's in the DB (not your wallet)
        if args.wallet:
            self.config['db4e']['wallet_balance'] = True

        # Run a backup of the DB
        if args.backup:
            self.config['db']['backup_db'] = True

        # Run the db4e service
        if args.service:
            self.config['db4e']['service'] = True
        else:
            self.config['db4e']['service'] = False

    def get(self, key):
        """
        Get a configuration value by key.
        """
        return self.config.get(key, None)
    
    def set(self, key, value):
        """
        Set a configuration value by key.
        """
        self.config[key] = value

    def load(self, yaml_file):
        with open(yaml_file, 'r') as file:
            self.config = yaml.safe_load(file)
            self.config['runtime'] = {}
            self.config['runtime']['yaml_file'] = yaml_file

    
