"""
db4e/Modules/ConfigManager.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

import os, sys
import argparse

from db4e.Modules.Helper import result_row, get_component_value, update_component_values
from db4e.Constants.Defaults import (
    API_DIR_DEFAULT, BACKUP_DIR_DEFAULT, BACKUP_SCRIPT_DEFAULT, BIN_DIR_DEFAULT,
    BLOCKCHAIN_DIR_DEFAULT, CONF_DIR_DEFAULT, DB4E_DIR_DEFAULT,
    DB4E_INSTALL_SERVICE_DEFAULT, DB4E_LOG_FILE_DEFAULT, DB4E_PROCESS_DEFAULT,
    DB4E_REFRESH_DEFAULT, DB4E_SERVICE_FILE_DEFAULT, DB4E_START_SCRIPT_DEFAULT,
    DB4E_UNINSTALL_SCRIPT_DEFAULT, DB4E_VERSION_DEFAULT, DB_NAME_DEFAULT,
    DB_PORT_DEFAULT, DB_RETRY_TIMEOUT_DEFAULT, DB_SERVER_DEFAULT,
    DEPLOYMENT_COL_DEFAULT, DEV_DIR_DEFAULT, INITIAL_SETUP_DEFAULT,
    LOG_COLLECTION_DEFAULT, LOG_DIR_DEFAULT, LOG_RETENTION_DAYS_DEFAULT,
    MAX_BACKUPS_DEFAULT, METRICS_COLLECTION_DEFAULT, MINING_COL_DEFAULT,
    MONEROD_CONFIG_DEFAULT, MONEROD_LOG_FILE_DEFAULT, MONEROD_PROCESS_DEFAULT,
    MONEROD_SERVICE_DEFAULT, MONEROD_SOCKET_SERVICE_DEFAULT,
    MONEROD_START_SCRIPT_DEFAULT, MONEROD_STDIN_PIPE_DEFAULT,
    MONEROD_VERSION_DEFAULT, P2POOL_CONFIG_DEFAULT, P2POOL_LOG_FILE_DEFAULT,
    P2POOL_PROCESS_DEFAULT, P2POOL_SERVICE_FILE_DEFAULT,
    P2POOL_SERVICE_SOCKET_FILE_DEFAULT, P2POOL_START_SCRIPT_DEFAULT,
    P2POOL_STDIN_PIPE_DEFAULT, P2POOL_VERSION_DEFAULT, PYPI_REPO_DEFAULT,
    RUN_DIR_DEFAULT, SRC_DIR_DEFAULT, SYSTEMD_DIR_DEFAULT, TEMPLATES_DIR_DEFAULT,
    VENDOR_DIR_DEFAULT, XMRIG_CONF_DIR_DEFAULT, XMRIG_CONFIG_DEFAULT,
    XMRIG_PERMISSIONS_DEFAULT, XMRIG_PROCESS_DEFAULT, XMRIG_SERVICE_FILE_DEFAULT,
    XMRIG_VERSION_DEFAULT, TEMPLATES_COLLECTION_DEFAULT
)

from db4e.Constants.Fields import (
    API_DIR_FIELD, APP_VERSION_FIELD, BACKUP_DIR_FIELD, BACKUP_SCRIPT_FIELD,
    BIN_DIR_FIELD, BLOCKCHAIN_DIR_FIELD, CONF_DIR_FIELD, CONFIG_FIELD,
    DB4E_DIR_FIELD, DB4E_FIELD, DB4E_REFRESH_FIELD, DESC_FIELD,
    DEPLOYMENT_COL_FIELD, DEV_DIR_FIELD, DB_FIELD, DB_NAME_FIELD, GOOD_FIELD,
    INSTALL_DIR_FIELD, INITIAL_SETUP_FIELD, INSTANCE_FIELD, IP_ADDR_FIELD,
    LOG_COLLECTION_FIELD, LOG_DIR_FIELD, LOG_FILE_FIELD, LOG_RETENTION_DAYS_FIELD,
    MAX_BACKUPS_FIELD, METRICS_COLLECTION_FIELD, MINING_COL_FIELD, MONEROD_FIELD,
    NAME_FIELD, NUM_THREADS_FIELD, OP_FIELD, P2POOL_FIELD, PARENT_ID_FIELD,
    PERMISSIONS_FIELD, PORT_FIELD, PROCESS_FIELD, PYPI_REPO_FIELD,
    RETRY_TIMEOUT_FIELD, RUN_BACKUP_FIELD, RUN_DIR_FIELD, RUN_SERVICE_FIELD,
    RUN_UI_FIELD, SERVER_FIELD, SERVICE_FILE_FIELD, SERVICE_INSTALL_SCRIPT_FIELD,
    SERVICE_LOG_FILE_FIELD, SERVICE_UNINSTALL_SCRIPT_FIELD, SOCKET_FILE_FIELD,
    SRC_DIR_FIELD, START_SCRIPT_FIELD, STRATUM_PORT_FIELD, STDIN_PIPE_FIELD,
    SYSTEMD_DIR_FIELD, TEMPLATE_DIR_FIELD, VENDOR_DIR_FIELD, VERSION_FIELD,
    WARN_FIELD, XMRIG_FIELD, TEMPLATES_COLLECTION_FIELD, HEALTH_MSGS_FIELD
)
from db4e.Constants.Labels import (
    DB4E_LONG_LABEL, MONEROD_LABEL, P2POOL_LABEL, XMRIG_LABEL)

class ConfigMgr:
    def __init__(self, app_version: str):
        parser = argparse.ArgumentParser(description="Db4E command line switches")
        parser.add_argument(
            "-b", "--backup", action="store_true", help="Perform a db4e backup.")
        parser.add_argument(
            "-s", "--service", action="store_true", help="Run db4e as a service.")
        parser.add_argument(
            "-v", "--version", action="store_true", help="Print the db4e version.")
        args = parser.parse_args()

        ini = Config(app_version=app_version)
        if args.backup:
            ini.config[DB4E_FIELD][OP_FIELD] = RUN_BACKUP_FIELD

        elif args.service:
            ini.config[DB4E_FIELD][OP_FIELD] = RUN_SERVICE_FIELD

        elif args.version:
            print(f'Db4e v{app_version}')
            sys.exit(0)
        else:
            ini.config[DB4E_FIELD][OP_FIELD] = RUN_UI_FIELD
        self.ini = ini

    def del_config(self, config_file: str):
        results = []
        try:
            os.remove(config_file)
            results.append(result_row(
                XMRIG_LABEL, GOOD_FIELD,
                f"Removed old configration file: {config_file}"
            ))
        except OSError as e:
            result_row.append(result_row(
                XMRIG_LABEL, WARN_FIELD,
                f"Unable to remove {config_file} {e} "
            ))
        return results

    def gen_xmrig_config(self, rec: dict, depl_mgr):
        # Generate a XMRig configuration file
        results = []
        instance = get_component_value(rec, INSTANCE_FIELD)
        num_threads = get_component_value(rec, NUM_THREADS_FIELD)
        p2pool_id = get_component_value(rec, PARENT_ID_FIELD)
        #print(f"ConfigMgr:gen_xmrig_config(): p2pool_id: {p2pool_id}")

        conf_dir        = self.ini.config[DB4E_FIELD][CONF_DIR_FIELD]
        tmpl_dir        = self.ini.config[DB4E_FIELD][TEMPLATE_DIR_FIELD]
        config          = self.ini.config[XMRIG_FIELD][CONFIG_FIELD]
        version         = self.ini.config[XMRIG_FIELD][VERSION_FIELD]

        xmrig_dir = XMRIG_FIELD + '-' + str(version)
        db4e_rec = depl_mgr.get_deployment(elem_type=DB4E_FIELD)
        db4e_dir = get_component_value(db4e_rec, INSTALL_DIR_FIELD)
        vendor_dir = get_component_value(db4e_rec, VENDOR_DIR_FIELD)

        tmpl_config = os.path.join(db4e_dir, tmpl_dir, xmrig_dir, conf_dir, config)
        fq_config = os.path.join(vendor_dir, xmrig_dir, conf_dir, instance + '.json')

        # The XMRig deploymet has references to the upstream P2Pool deployment
        p2pool_rec = depl_mgr.get_deployment_by_id(p2pool_id)
        #print(f"ConfigMgr:gen_xmrig_config(): p2pool_rec: {p2pool_rec}")
        p2pool_ip = get_component_value(p2pool_rec, IP_ADDR_FIELD)
        stratum_port = get_component_value(p2pool_rec, STRATUM_PORT_FIELD)
        url_entry = p2pool_ip + ':' + str(stratum_port)

        # Populate the config templace placeholders
        placeholders = {
            'MINER_NAME': instance,
            'NUM_THREADS': ','.join(['-1'] * int(num_threads)),
            'URL': url_entry
        }
        with open(tmpl_config, 'r') as f:
            config_contents = f.read()
            for key, val in placeholders.items():
                config_contents = config_contents.replace(f'[[{key}]]', str(val))
        with open(fq_config, 'w') as f:
            f.write(config_contents)
        rec = update_component_values(rec=rec, updates={CONFIG_FIELD: fq_config})
        return rec

    def get_config(self):
        return self.ini
    
class Config:
    def __init__(self, app_version: str):
        self.config = {
            DB4E_FIELD: {
                APP_VERSION_FIELD: app_version,
                OP_FIELD: RUN_UI_FIELD,
                API_DIR_FIELD: API_DIR_DEFAULT,
                BIN_DIR_FIELD: BIN_DIR_DEFAULT,
                CONF_DIR_FIELD: CONF_DIR_DEFAULT,
                DB_NAME_FIELD: DB_NAME_DEFAULT,
                DB4E_DIR_FIELD: DB4E_DIR_DEFAULT,
                DB4E_REFRESH_FIELD: DB4E_REFRESH_DEFAULT,
                DESC_FIELD: DB4E_LONG_LABEL,
                DEV_DIR_FIELD: DEV_DIR_DEFAULT,
                INITIAL_SETUP_FIELD: INITIAL_SETUP_DEFAULT,
                LOG_DIR_FIELD: LOG_DIR_DEFAULT,
                PROCESS_FIELD: DB4E_PROCESS_DEFAULT,
                PYPI_REPO_FIELD: PYPI_REPO_DEFAULT,
                RUN_DIR_FIELD: RUN_DIR_DEFAULT,
                SERVICE_FILE_FIELD: DB4E_SERVICE_FILE_DEFAULT,
                SERVICE_INSTALL_SCRIPT_FIELD: DB4E_INSTALL_SERVICE_DEFAULT,
                SERVICE_LOG_FILE_FIELD: DB4E_LOG_FILE_DEFAULT,
                SERVICE_UNINSTALL_SCRIPT_FIELD: DB4E_UNINSTALL_SCRIPT_DEFAULT,
                SRC_DIR_FIELD: SRC_DIR_DEFAULT,
                START_SCRIPT_FIELD: DB4E_START_SCRIPT_DEFAULT,
                SYSTEMD_DIR_FIELD: SYSTEMD_DIR_DEFAULT,
                TEMPLATE_DIR_FIELD: TEMPLATES_DIR_DEFAULT,
                VENDOR_DIR_FIELD: VENDOR_DIR_DEFAULT,
                VERSION_FIELD: DB4E_VERSION_DEFAULT,
            },
            DB_FIELD: {
                BACKUP_DIR_FIELD: BACKUP_DIR_DEFAULT,
                BACKUP_SCRIPT_FIELD:BACKUP_SCRIPT_DEFAULT,
                DB_NAME_FIELD: DB_NAME_DEFAULT,
                DEPLOYMENT_COL_FIELD: DEPLOYMENT_COL_DEFAULT,
                LOG_COLLECTION_FIELD: LOG_COLLECTION_DEFAULT,
                LOG_RETENTION_DAYS_FIELD: LOG_RETENTION_DAYS_DEFAULT,
                MAX_BACKUPS_FIELD: MAX_BACKUPS_DEFAULT,
                METRICS_COLLECTION_FIELD: METRICS_COLLECTION_DEFAULT,
                MINING_COL_FIELD: MINING_COL_DEFAULT,
                NAME_FIELD: DB_NAME_DEFAULT,
                PORT_FIELD: DB_PORT_DEFAULT,
                RETRY_TIMEOUT_FIELD: DB_RETRY_TIMEOUT_DEFAULT,
                SERVER_FIELD: DB_SERVER_DEFAULT,
                TEMPLATES_COLLECTION_FIELD: TEMPLATES_COLLECTION_DEFAULT,

            },
            MONEROD_FIELD: {
                BLOCKCHAIN_DIR_FIELD: BLOCKCHAIN_DIR_DEFAULT,
                CONFIG_FIELD: MONEROD_CONFIG_DEFAULT,
                DESC_FIELD: MONEROD_LABEL,
                LOG_FILE_FIELD: MONEROD_LOG_FILE_DEFAULT,
                PROCESS_FIELD: MONEROD_PROCESS_DEFAULT,
                SERVICE_FILE_FIELD: MONEROD_SERVICE_DEFAULT,
                SOCKET_FILE_FIELD: MONEROD_SOCKET_SERVICE_DEFAULT,
                STDIN_PIPE_FIELD: MONEROD_STDIN_PIPE_DEFAULT,
                START_SCRIPT_FIELD: MONEROD_START_SCRIPT_DEFAULT,
                VERSION_FIELD: MONEROD_VERSION_DEFAULT,
            },
            P2POOL_FIELD: {
                CONFIG_FIELD: P2POOL_CONFIG_DEFAULT,
                DESC_FIELD: P2POOL_LABEL,
                LOG_FILE_FIELD: P2POOL_LOG_FILE_DEFAULT,
                PROCESS_FIELD: P2POOL_PROCESS_DEFAULT,
                SERVICE_FILE_FIELD: P2POOL_SERVICE_FILE_DEFAULT,
                SOCKET_FILE_FIELD: P2POOL_SERVICE_SOCKET_FILE_DEFAULT,
                START_SCRIPT_FIELD: P2POOL_START_SCRIPT_DEFAULT,
                STDIN_PIPE_FIELD: P2POOL_STDIN_PIPE_DEFAULT,
                VERSION_FIELD: P2POOL_VERSION_DEFAULT,                
            },
            XMRIG_FIELD: {
                DESC_FIELD: XMRIG_LABEL,
                CONF_DIR_FIELD: XMRIG_CONF_DIR_DEFAULT,
                CONFIG_FIELD: XMRIG_CONFIG_DEFAULT, 
                PERMISSIONS_FIELD: XMRIG_PERMISSIONS_DEFAULT,
                PROCESS_FIELD: XMRIG_PROCESS_DEFAULT, 
                SERVICE_FILE_FIELD: XMRIG_SERVICE_FILE_DEFAULT, 
                VERSION_FIELD: XMRIG_VERSION_DEFAULT
            }
        }


