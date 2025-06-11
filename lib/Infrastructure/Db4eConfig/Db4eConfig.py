"""
Infrastructure/Db4eConfig/Db4eConfig.py
"""

import yaml
import argparse
import os

YAML_FILE = 'conf/db4e_prod.yml'
YAML_FILE_QA = 'conf/db4e_qa.yml'
        
class Db4eConfig():

    def __init__(self):
        # Read the application configuration file
        db4e_dir = os.path.join(os.path.dirname(__file__), '../../../')
        yaml_file = os.path.join(db4e_dir, YAML_FILE_QA)
        self.load(yaml_file)


        # Setup the command line parser
        parser = argparse.ArgumentParser(description='DB4E Configuration')
        
        parser.add_argument('-b', '--backup', action='store_true', help='Perform a db4e backup.')
        parser.add_argument('-e', '--environ', default='prod', help='Run in QA environment with -e qa.')
        parser.add_argument('-m', '--monitor', action='store_true', help='Monitor the P2Pool log.')
        parser.add_argument('-w', '--wallet', action='store_true', help='Get the mining wallet balance.')
        parser.add_argument('-l', '--log_level', default='info', type=str, help='Set the log level (debug, info, warning, error or critical')
        parser.add_argument('-r', '--reports', default='None', type=str, help='Run a db4e report.')
        
        
        args = parser.parse_args()

        ### Parse any command line args

        # This has a default, so its always set
        self.config['db4e']['log_level'] = args.log_level

        # This has a default, so its always set.
        self.config['db4e']['environ'] = args.environ
        if args.environ == 'qa':
            # Load the QA environment settings (DB, directories etc)
            self.load(os.path.join(db4e_dir, YAML_FILE_QA))
        
        # Run one or more reprts with a reports definition file in conf/reports
        if args.reports != 'None':
            self.config['db4e']['reports'] = args.reports
        
        # Monitor the P2Pool daemon log files for P2Pool events
        if args.monitor:
            self.config['p2pool']['monitor_log'] = True

        # Return the wallet balance that's in the DB (not your wallet)
        if args.wallet:
            self.config['db4e']['wallet_balance'] = True

        # Run a backup of the DB
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

    
