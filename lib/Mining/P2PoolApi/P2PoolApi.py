"""
lib/Mining/P2PoolApi/P2PoolApi.py

This module provides an interface to interact with the P2Pool API.
"""

import os, sys
import json

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
P2POOL_POOL_STATS = 'pool/stats'
P2POOL_NETWORK_STATS = 'network/stats'

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

        self._height = None
        self._sidechain_height = None
        self._miners = None
        self._hashrate = None # In MH/s

    def _get_api_data(self, api_elem):
        api_file = os.path.join(self._api_dir, api_elem)
        if not os.path.exists(api_file):
            raise FileNotFoundError(f"P2Pool API file not found: {api_file}")
        with open(api_file, 'r') as file:
            data = file.read()
        return json.loads(data)

    def _get_network_stats(self):
        """
        Fetch network statistics from the P2Pool API.
        """
        network_stats = self._get_api_data(P2POOL_NETWORK_STATS)
        print(f"Network stats:\n{network_stats}")

    def _get_pool_stats(self):
        """
        Fetch network statistics from the P2Pool API.
        """
        pool_stats = self._get_api_data(P2POOL_POOL_STATS)
        self._sidechain_height = pool_stats['pool_statistics']['sidechainHeight']
        print(f"Pool stats:\n{pool_stats}")

    def _get_stats_mod(self):
        """
        Fetch information from the P2Pool API.
        """
        stats_mod = self._get_api_data(P2POOL_STATS_MOD)
        self._height = stats_mod['network']['height']
        self._miners = stats_mod['pool']['miners']
        self._hashrate = round(stats_mod['pool']['hashrate']/1000000, 3)
        print(f"Stats mod:\n{stats_mod}")
   
    def hashrate(self):
        """
        Get the current hashrate of the P2Pool network in MH/s.
        """
        if self._hashrate is None:
            self.refresh()
        return self._hashrate

    def height(self):
        """
        Get the current height of the P2Pool network.
        """
        if self._height is None:
            self.refresh()
        return self._height
    
    def miners(self):
        """
        Get the list of miners in the P2Pool network.
        """
        if self._miners is None:
            self.refresh()
        return self._miners

    def refresh(self):
        """
        Refresh the P2Pool API data.
        """
        try:
            self._get_stats_mod()
        except FileNotFoundError as e:
            print(f"Error refreshing P2Pool API: {e}")
        except json.JSONDecodeError as e:
            print(f"Error parsing P2Pool API data: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        try:
            self._get_network_stats()
        except FileNotFoundError as e:
            print(f"Error refreshing P2Pool API: {e}")
        except json.JSONDecodeError as e:
            print(f"Error parsing P2Pool API data: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        try:
            self._get_pool_stats()
        except FileNotFoundError as e:
            print(f"Error refreshing P2Pool API: {e}")
        except json.JSONDecodeError as e:
            print(f"Error parsing P2Pool API data: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


    def sidechain_height(self):
        """
        Get the current sidechain height of the P2Pool network.
        """
        if self._sidechain_height is None:
            self.refresh()
        return self._sidechain_height

if __name__ == "__main__":
    # Example usage
    p2pool_api = P2PoolApi()
    print("P2Pool API Data:")
    print(f"  Mainchain Height   : {p2pool_api.height()}")
    print(f"  Miners             : {p2pool_api.miners()}")
    print(f"  Sidechain Hashrate : {p2pool_api.hashrate()} MH/s")
    print(f"  Sidechain Height   : {p2pool_api.sidechain_height()}")
    print("-" * 35)
    