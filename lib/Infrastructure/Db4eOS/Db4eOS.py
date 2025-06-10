"""
lib/Infrastructure/Db4eOS/Db4eOS.py
"""
import os, sys
import subprocess
import psutil

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure',
  lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

# DB4E modules
from Db4eConfig.Db4eConfig import Db4eConfig
from Db4eLogger.Db4eLogger import Db4eLogger

class Db4eOs:
    def __init__(self):
        # Possibly store paths, config state, environment, etc.
        ini = Db4eConfig()
        self._parts = {
            'db4e': {
                'install_dir' : ini['db4e']['install_dir'],
                'process'     : ini['db4e']['process'],
                'systemd'     : None,
            },
            'p2pool': {
                'install_dir' : ini['p2pool']['install_dir'],
                'process'     : ini['p2pool']['process'],
                'config'      : ini['p2pool']['config'],
            },
            'monerod': {
                'install_dir' : ini['monerod']['install_dir'],
                'process'     : ini['monerod']['process'],
                'config'      : ini['monerod']['config'],
                'systemd'     : None,
            },
            'xmrig': {
                'install_dir' : ini['xmrig']['install_dir'],
                'process'     : ini['xmrig']['process'],
                'config'      : ini['xmrig']['config'],
                'systemd'     : None,
            },
            'repo': {
                'install_dir' : ini['xmrig']['install_dir']
            }
        }
        self.probe_env()


    def probe_env(self):
        pass


    def get_pid(self, proc_name):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc_name in proc.info['name']:
                return proc.info['pid']
        return None        

    def get_info(self, component):
        """
        Return status/info string for a given component.
        E.g., check if process is running, version, uptime, etc.
        """
        pass

    def is_installed(self, component):
        """
        Determine if a given component is installed (e.g., binary exists).
        """
        pass

    def install_component(self, component):
        """
        Trigger installation procedure for missing component.
        Could use apt, source builds, or pull from repo.
        """
        pass

    def configure_component(self, component, config_data):
        """
        Write configuration files or set environment variables.
        """
        pass

    def start_component(self, component):
        """
        Start a given component daemon or process.
        """
        pass

    def stop_component(self, component):
        """
        Stop the running process cleanly.
        """
        pass
