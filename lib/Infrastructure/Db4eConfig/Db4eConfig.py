"""
Infrastructure/Db4eConfig/Db4eConfig.py
"""

import yaml
import argparse

YAML_FILE = '/imports/disk1/github/db4e/conf/db4e.yml'

class Db4eConfig():

    def __init__(self):
        # Read the application configuration file
        self.load(YAML_FILE)

        # Setup the command line parser
        parser = argparse.ArgumentParser(description='DB4E Configuration')
        
        parser.add_argument('-b', '--backup', action='store_true', help='Perform a db4e backup.')
        parser.add_argument('-m', '--monitor', action='store_true', help='Monitor the P2Pool log.')
        parser.add_argument('-w', '--wallet', action='store_true', help='Get the mining wallet balance.')
        parser.add_argument('-r', '--reports', default='None', type=str, help='Run a db4e report.')
        
        
        args = parser.parse_args()

        # Parse any command line args
        if args.reports != 'None':
            self.config['export']['reports'] = args.reports
        
        if args.monitor:
            self.config['p2pool']['monitor_log'] = True

        if args.wallet:
            self.config['db4e']['wallet_balance'] = True

        if args.backup:
            self.config['db']['backup_db'] = True

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

    
