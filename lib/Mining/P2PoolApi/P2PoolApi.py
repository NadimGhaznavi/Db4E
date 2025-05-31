"""
lib/Mining/P2PoolApi/P2PoolApi.py

This module provides an interface to interact with the P2Pool API.
"""

import os, sys

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure',
  lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from Db4eConfig.Db4eConfig import Db4eConfig

# P2Pool Daemon API names
P2POOL_STATS_MOD = 'stats_mod'
P2POOL_NETWORK = 'network'
P2POOL_POOL = 'pool'
P2POOL_BLOCKS = 'blocks'

class P2PoolApi():
    """
    P2PoolApi provides methods to interact with the P2Pool API.
    """

    def __init__(self):
        """
        Initialize the P2PoolApi instance.
        """
        config = Db4eConfig()
        p2pool_dir = config.config['p2pool']['install_dir']
        api_dir = config.config['p2pool']['api_dir']
        self._api_dir = os.path.join(p2pool_dir, api_dir)

        self._stats_mod = None
        self._port = None

    def get_stats_mod(self):
        """
        Fetch information from the P2Pool API.
        """
        api_file = os.path.join(self._api_dir, P2POOL_STATS_MOD)
        if not os.path.exists(api_file):
            raise FileNotFoundError(f"P2Pool API file not found: {api_file}")
        with open(api_file, 'r') as file:
            data = file.read()
        self._stats_mod = data
        print(type(data))
        #print(data['config']['ports']['port'])
       
        return data
    
if __name__ == "__main__":
    # Example usage
    p2pool_api = P2PoolApi()
    stats = p2pool_api.get_stats_mod()
    print("P2Pool Stats Mod:", stats)
        
