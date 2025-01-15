"""
lib/Infrastructure/Db4eStartup/Db4eStartup.py
"""

# Import supporting modules
import os
import argparse
import configparser

# The directory that this script is in
lib_dir = os.path.dirname(__file__)
# The home of the DB4E configuration file
conf_dir = lib_dir + '/../../../conf/'

# Global variables
ini_file = conf_dir + 'db4e.ini'
default_environment = 'dev'

class Db4eStartup():

  def __init__(self):
    # Setup the expected script arguments
    action_help = '[backup_db|monitor_p2pool_log|new_blocks_found_csv|' + \
      'new_p2pool_payment_csv|new_shares_found_csv|new_shares_found_by_host]'
    parser = argparse.ArgumentParser(description='DB4E Application')
    parser.add_argument('-a', '--action', type=str, default=None, help=action_help)
    parser.add_argument('-d', '--debug', type=int, default=0, help='debug level')
    parser.add_argument('-e', '--environ', type=str, default=default_environment)
    parser.add_argument('-i', '--ini_file', type=str, default=ini_file, help='DB4E configuration file')
    parser.add_argument('-m', '--mode', type=str, default=None, help='visual')
    # Parse arguments
    args = parser.parse_args()
    self._args = args

    # prod, qa or dev
    environ = args.environ
    self._environ = environ

    # Override the environment setting if the DB4E_ENVIRONMENT variable has already been set
    try:
      environ_var = os.environ['DB4E_ENVIRONMENT']
      self._environ = environ_var
    except KeyError:
      os.environ['DB4E_ENVIRONMENT'] = self._environ
      
    # Action 
    self._action = args.action

    # Debug level
    self._debug = args.debug

    # Access the INI file 
    config = configparser.ConfigParser()
    config.read(args.ini_file)

    # Read the INI file settings
    self._p2pool_log = config[environ]['p2pool_log']
    self._db_server = config[environ]['db_server']
    self._db_port = config[environ]['db_port']
    self._db_name = config[environ]['db_name']
    self._blocks_found_csv = config[environ]['blocks_found_csv']
    self._p2pool_payouts_csv = config[environ]['p2pool_payouts_csv']
    self._shares_found_csv = config[environ]['shares_found_csv']
    self._shares_found_by_host_csv = config[environ]['shares_found_by_host_csv']
    self._git_push_script = config[environ]['git_push_script']
    self._backup_db_script = config[environ]['backup_db_script']
    self._db4e_log = config[environ]['db4e_log']

  def action(self):
    return self._action
  
  def backup_db_script(self):
    return self._backup_db_script

  def blocks_found_csv(self):
    return self._blocks_found_csv

  def db_name(self):
    return self._db_name
  
  def db_port(self):
    return self._db_port
  
  def db_server(self):
    return self._db_server

  def db4e_log(self):
    return self._db4e_log

  def debug(self):
    return self._debug
  
  def environ(self):
    return self._environ
  
  def git_push_script(self):
    return self._git_push_script

  def p2pool_log(self):
    return self._p2pool_log
  
  def p2pool_payouts_csv(self):
    return self._p2pool_payouts_csv
  
  def shares_found_csv(self):
    return self._shares_found_csv

  def shares_found_csv_by_host(self):
    return self._shares_found_by_host_csv
