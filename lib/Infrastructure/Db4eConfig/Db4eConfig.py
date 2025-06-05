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
        
        parser.add_argument('-a', '--action', default='None', type=str, help='Do -la to list all actions.')
        parser.add_argument('-b', '--backup', default='None', type=str, help='Perform a db4e backup.')
        parser.add_argument('-m', '--monitor', default='None', type=str, help='Monitor the P2Pool log.')
        parser.add_argument('-w', '--wallet', default='None', type=str, help='Get the mining wallet balance.')
        parser.add_argument('-r', '--reports', default='None', type=str, help='Run a db4e report.')
        
        
        args = parser.parse_args()

        # Parse any command line args
        if args.reports != 'None':
            self.config['export']['reports'] = args.reports

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

    
