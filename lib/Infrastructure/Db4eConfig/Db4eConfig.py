"""
Infrastructure/Db4eConfig/Db4eConfig.py
"""

import yaml
import argparse
import os

YAML_FILE = '/imports/disk1/github/db4e/conf/db4e.yml'

class Db4eConfig():

    def __init__(self):
        # Read the application configuration file
        self.load(YAML_FILE)

        # Setup the command line parser
        parser = argparse.ArgumentParser(description='DB4E Configuration')
        
        parser.add_argument('-a', '--action', default='None', type=str, help='Do -la to list all actions. ')
        parser.add_argument('-la', '--list_actions', action='store_true', help='List all available actions.')

        args = parser.parse_args()
        if args.list_actions:
            print("Available actions:")
            print("  new_blocks_found_csv     : Generate the 'Blocks Found' CSV files and push them to GitHub.")
            print("  new_p2pool_payment_csv   : Generate the 'P2Pool Payments' CSV files and push them to GitHub.")
            print("  new_shares_found_csv     : Generate the 'Shares Found' CSV files and push it them GitHub.")
            print("  new_shares_found_by_host : Generate the 'Shares Found by Host' CSV files and push them to GitHub.")
            print("  backup_db                : Backup MongoDB and push the backup to GitHub.")
            print("  monitor_p2pool_log       : Start monitoring the P2Pool daemon log.")
            print("  get_wallet_balance       : Get the wallet balance from MongoDb.")
            exit(0)

        # Parse any command line args
        self.config['db4e']['action'] = args.action

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

    
