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

from db4e.Modules.Db4eLogger import Db4eLogger
from db4e.Modules.ConfigMgr import Config, ConfigMgr
from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.OpsMgr import OpsMgr
from db4e.Constants.Defaults import (
    TERM_DEFAULT, COLORTERM_DEFAULT, DB4E_SERVER_DEFAULT)
from db4e.Constants.Fields import (
    DB4E_FIELD, LOG_DIR_FIELD, LOG_FILE_FIELD, VENDOR_DIR_FIELD, TERM_ENVIRON_FIELD, 
    COLORTERM_ENVIRON_FIELD)



class Db4eServer:
    """
    Db4E Server
    """
    def __init__(self, ini = Config):
        self.ini = ini
        self.ops_mgr = OpsMgr(config=ini)
        vendor_dir = self.ops_mgr.get_dir(VENDOR_DIR_FIELD)
        logs_dir = ini.config[DB4E_FIELD][LOG_DIR_FIELD]

        log_file = ini.config[DB4E_FIELD][LOG_FILE_FIELD]
        fq_log_file = os.path.join(vendor_dir, DB4E_FIELD, logs_dir, log_file)    

        self.log = Db4eLogger(
            config=ini,
            elem_type=DB4E_SERVER_DEFAULT,
            log_file=fq_log_file
        )

    def start(self):
        self.log.info("Starting Db4E Server")
        while True:
            time.sleep(10)
            self.log.info("Ticking...")


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