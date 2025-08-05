"""
db4e/server.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

"""

import os
import time
import signal
import threading
from importlib import metadata

try:
    __package_name__ = metadata.metadata(__package__ or __name__)["Name"]
    __version__ = metadata.version(__package__ or __name__)
except Exception:
    __package_name__ = "Db4E"
    __version__ = "N/A"

from db4e.Modules.Db4eLogger import Db4eLogger
from db4e.Modules.ConfigMgr import Config, ConfigMgr
from db4e.Modules.OpsMgr import OpsMgr
from db4e.Modules.Helper import get_component_value
from db4e.Constants.Defaults import (
    TERM_DEFAULT, COLORTERM_DEFAULT, DB4E_SERVER_DEFAULT)
from db4e.Constants.Fields import (
    DB4E_FIELD, LOG_DIR_FIELD, LOG_FILE_FIELD, VENDOR_DIR_FIELD, TERM_ENVIRON_FIELD, 
    COLORTERM_ENVIRON_FIELD, ENABLE_FIELD, ELEMENT_TYPE_FIELD, XMRIG_FIELD, 
    INSTANCE_FIELD)
from db4e.Constants.Labels import XMRIG_LABEL

POLL_INTERVAL = 5

class Db4eServer:
    """
    Db4E Server
    """
    def __init__(self, ini = Config):
        self.ini = ini

        # Get an ops manager
        self.ops_mgr = OpsMgr(config=ini)

        # Setup logging
        vendor_dir = self.ops_mgr.get_dir(VENDOR_DIR_FIELD)
        logs_dir = ini.config[DB4E_FIELD][LOG_DIR_FIELD]
        log_file = ini.config[DB4E_FIELD][LOG_FILE_FIELD]
        fq_log_file = os.path.join(vendor_dir, DB4E_FIELD, logs_dir, log_file)    
        self.log = Db4eLogger(
            config=ini,
            elem_type=DB4E_SERVER_DEFAULT,
            log_file=fq_log_file
        )

        self.running = threading.Event()
        self.running.set()


    def check_deployments(self):
        self.log.info("Checking deployments:")
        depls = self.ops_mgr.get_deployments()
        for depl in depls:
            if ENABLE_FIELD in depl:
                elem_type = depl[ELEMENT_TYPE_FIELD]
                if elem_type == XMRIG_FIELD:
                    self._handle_xmrig(depl)

    def _handle_xmrig(self, depl):
        enable_flag = depl[ENABLE_FIELD]
        instance = get_component_value(depl, INSTANCE_FIELD)
        self.log.critical(f"Found {XMRIG_LABEL}: instance {instance}, enabled: {enable_flag}")


    def start(self):
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        self.log.info("Starting Db4E Server")
        count = 0
        while self.running.is_set:
            count += 1
            self.log.debug(f"Ticking... {count}...")
            self.check_deployments()
            time.sleep(POLL_INTERVAL)

        self.cleanup()


    def shutdown(self, signum, frame):
        self.log.info(f'Shutdown requested (signal {signum})')
        self.running.clear()

    def cleanup(self):
        self.log.info('Shutdown complete')

def main():
    # Set environment variables for better color support
    os.environ[TERM_ENVIRON_FIELD] = TERM_DEFAULT
    os.environ[COLORTERM_ENVIRON_FIELD] = COLORTERM_DEFAULT

    config_manager = ConfigMgr(__version__)
    config = config_manager.get_config()
    server = Db4eServer(config)
    server.start()
if __name__ == "__main__":
    main()