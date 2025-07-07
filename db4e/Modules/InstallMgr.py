"""
db4e/Modules/InstallMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

import os, shutil
from datetime import datetime, timezone
import getpass
import subprocess

from db4e.Modules.ConfigMgr import Config
from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.Helper import result_row
from db4e.Constants.Fields import (
    BIN_DIR_FIELD, BLOCKCHAIN_DIR_FIELD, CONF_DIR_FIELD, DB4E_FIELD, DB4E_DIR_FIELD, 
    ENABLE_FIELD, ERROR_FIELD, GOOD_FIELD, GROUP_FIELD, INSTALL_DIR_FIELD, LOG_DIR_FIELD, 
    MONEROD_FIELD, P2POOL_FIELD, PROCESS_FIELD, RUN_DIR_FIELD, SETUP_SCRIPT_FIELD, 
    SERVICE_FILE_FIELD, SOCKET_FILE_FIELD, START_SCRIPT_FIELD, SYSTEMD_DIR_FIELD, 
    TEMPLATE_DIR_FIELD, USER_FIELD, USER_WALLET_FIELD, VENDOR_DIR_FIELD, VERSION_FIELD, 
    WARN_FIELD, XMRIG_FIELD
)
from db4e.Constants.SystemdTemplates import (
    DB4E_USER_PLACEHOLDER, DB4E_GROUP_PLACEHOLDER, DB4E_DIR_PLACEHOLDER,
    MONEORD_DIR_PLACEHOLDER, P2POOL_DIR_PLACEHOLDER, XMRIG_DIR_PLACEHOLDER
)
from db4e.Constants.Labels import DB4E_GROUP_LABEL, DB4E_LABEL, DEPLOYMENT_DIR_LABEL, MONERO_WALLET_LABEL
from db4e.Constants.Defaults import (
    DB4E_OLD_GROUP_ENVIRON_DEFAULT, DEPLOYMENT_COL_DEFAULT, SUDO_CMD_DEFAULT, TMP_DIR_DEFAULT
)
# The Mongo collection that houses the deployment records
DEPL_COL = DEPLOYMENT_COL_DEFAULT
DB4E_OLD_GROUP_ENVIRON = DB4E_OLD_GROUP_ENVIRON_DEFAULT
TMP_DIR = TMP_DIR_DEFAULT
SUDO_CMD = SUDO_CMD_DEFAULT

class InstallMgr:
    
    def __init__(self, config: Config):
        self.ini = config
        self.depl_mgr = DeploymentMgr(config)
        self.db = DbMgr(config)

    async def initial_setup(self, form_data: dict) -> dict:
        # Track the progress of the initial install
        results = []
        # Validate the data
        user_wallet = form_data[USER_WALLET_FIELD]
        db4e_group = form_data[GROUP_FIELD]
        vendor_dir = form_data[VENDOR_DIR_FIELD]

        db4e_rec = self.depl_mgr.get_deployment(DB4E_FIELD)

        error_flag = False
        error_flag, results = self._check_form_data(
            user_wallet=user_wallet, db4e_group=db4e_group, vendor_dir=vendor_dir)
        if error_flag:
            return results
        
        results.append(result_row(DB4E_LABEL, GOOD_FIELD, "You filled out the form!"))
        return results
        # Handle the case where a Mongo 'db4e' record already exists e.g. if the user
        # is running Db4E from a fresh installation.
        db4e_rec, results = self._handle_reinstall(
            self, db4e_rec=db4e_rec, user_wallet=user_wallet, 
            vendor_dir=vendor_dir, results=results, db4e_group=db4e_group)

        # Create the vendor directory
        if os.path.exists(vendor_dir):
            results.append(result_row(DEPLOYMENT_DIR_LABEL, WARN_FIELD, f'Found existing deployment directory ({vendor_dir})'))
            timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            try:
                backup_vendor_dir = vendor_dir + '.' + timestamp
                os.rename(vendor_dir, backup_vendor_dir)
                results.append(result_row(DEPLOYMENT_DIR_LABEL, WARN_FIELD, f'Backed up old deployment directory ({backup_vendor_dir})'))
            except PermissionError:
                results.append(result_row(DEPLOYMENT_DIR_LABEL, ERROR_FIELD, f'Failed to backup old deployment directory ({backup_vendor_dir})'))
                return results # Abort the install
        try:
            os.makedirs(vendor_dir)
        except (PermissionError, FileNotFoundError, FileExistsError) as e:
            results.append(result_row(DEPLOYMENT_DIR_LABEL, ERROR_FIELD, f'Failed to create directory ({vendor_dir}\n{e}'))
            return results # Abort the install

        # Additional config settings
        bin_dir              = self.ini.config[DB4E_FIELD][BIN_DIR_FIELD]
        conf_dir             = self.ini.config[DB4E_FIELD][CONF_DIR_FIELD]
        db4e_dir             = self.ini.config[DB4E_FIELD][DB4E_DIR_FIELD]
        db4e_service_file    = self.ini.config[DB4E_FIELD][SERVICE_FILE_FIELD]
        initial_setup_script = self.ini.config[DB4E_FIELD][SETUP_SCRIPT_FIELD]
        log_dir              = self.ini.config[DB4E_FIELD][LOG_DIR_FIELD]
        run_dir              = self.ini.config[DB4E_FIELD][RUN_DIR_FIELD]
        systemd_dir          = self.ini.config[DB4E_FIELD][SYSTEMD_DIR_FIELD]
        templates_dir        = self.ini.config[DB4E_FIELD][TEMPLATE_DIR_FIELD]
        p2pool_binary        = self.ini.config[P2POOL_FIELD][PROCESS_FIELD]
        p2pool_service_file  = self.ini.config[P2POOL_FIELD][SERVICE_FILE_FIELD]
        p2pool_start_script  = self.ini.config[P2POOL_FIELD][START_SCRIPT_FIELD]
        p2pool_socket_file   = self.ini.config[P2POOL_FIELD][SOCKET_FILE_FIELD]
        p2pool_version       = self.ini.config[P2POOL_FIELD][VERSION_FIELD]
        blockchain_dir       = self.ini.config[MONEROD_FIELD][BLOCKCHAIN_DIR_FIELD]
        monerod_binary       = self.ini.config[MONEROD_FIELD][PROCESS_FIELD]
        monerod_service_file = self.ini.config[MONEROD_FIELD][SERVICE_FILE_FIELD]
        monerod_socket_file  = self.ini.config[MONEROD_FIELD][SOCKET_FILE_FIELD]
        monerod_start_script = self.ini.config[MONEROD_FIELD][START_SCRIPT_FIELD]
        monerod_version      = self.ini.config[MONEROD_FIELD][VERSION_FIELD]
        xmrig_binary         = self.ini.config[XMRIG_FIELD][PROCESS_FIELD]
        xmrig_service_file   = self.ini.config[XMRIG_FIELD][SERVICE_FILE_FIELD] 
        xmrig_version        = self.ini.config[XMRIG_FIELD][VERSION_FIELD]

        # The db4e user (the account used to run Db4E)
        db4e_user = getpass.getuser()

        # db4e, P2Pool, Monero daemon and XMRig directories
        db4e_vendor_dir = DB4E_FIELD
        p2pool_dir = P2POOL_FIELD +'-' + str(p2pool_version)
        monerod_dir = MONEROD_FIELD + '-' + str(monerod_version)
        xmrig_dir = XMRIG_FIELD + '-' + str(xmrig_version)

        # Create the vendor directories
        os.mkdir(os.path.join(vendor_dir, blockchain_dir))
        os.mkdir(os.path.join(vendor_dir, db4e_vendor_dir))
        os.mkdir(os.path.join(vendor_dir, db4e_vendor_dir, conf_dir))
        os.mkdir(os.path.join(vendor_dir, p2pool_dir))
        os.mkdir(os.path.join(vendor_dir, p2pool_dir, bin_dir))
        os.mkdir(os.path.join(vendor_dir, p2pool_dir, conf_dir))
        os.mkdir(os.path.join(vendor_dir, p2pool_dir, run_dir))
        os.mkdir(os.path.join(vendor_dir, monerod_dir))
        os.mkdir(os.path.join(vendor_dir, monerod_dir, bin_dir))
        os.mkdir(os.path.join(vendor_dir, monerod_dir, conf_dir))
        os.mkdir(os.path.join(vendor_dir, monerod_dir, run_dir))
        os.mkdir(os.path.join(vendor_dir, monerod_dir, log_dir))
        os.mkdir(os.path.join(vendor_dir, xmrig_dir))
        os.mkdir(os.path.join(vendor_dir, xmrig_dir, bin_dir))
        os.mkdir(os.path.join(vendor_dir, xmrig_dir, conf_dir))

        # The Templates directory
        tmpl_dir = os.path.join(os.path.dirname(__file__), '..', templates_dir)
        # Fully qualifed directories
        fq_db4e_dir = os.path.join(vendor_dir, db4e_vendor_dir)
        fq_p2pool_dir = os.path.join(vendor_dir, p2pool_dir)
        fq_monerod_dir = os.path.join(vendor_dir, monerod_dir)
        fq_xmrig_dir = os.path.join(vendor_dir, xmrig_dir)

        # Templates for the db4e, Monero daemon and P2pool services
        fq_db4e_service_file    = os.path.join(tmpl_dir, DB4E_FIELD, systemd_dir, db4e_service_file)
        fq_p2pool_service_file  = os.path.join(tmpl_dir, p2pool_dir, systemd_dir, p2pool_service_file)
        fq_p2pool_socket_file   = os.path.join(tmpl_dir, p2pool_dir, systemd_dir, p2pool_socket_file)
        fq_monerod_service_file = os.path.join(tmpl_dir, monerod_dir, systemd_dir, monerod_service_file)
        fq_monerod_socket_file  = os.path.join(tmpl_dir, monerod_dir, systemd_dir, monerod_socket_file)
        fq_xmrig_service_file   = os.path.join(tmpl_dir, xmrig_dir, systemd_dir, xmrig_service_file)

        # P2Pool, Monerod daemon, XMRig binaries and start-scripts
        fq_p2pool               = os.path.join(tmpl_dir, p2pool_dir, bin_dir, p2pool_binary)
        fq_p2pool_start_script  = os.path.join(tmpl_dir, p2pool_dir, bin_dir, p2pool_start_script)
        fq_monerod              = os.path.join(tmpl_dir, monerod_dir, bin_dir, monerod_binary)
        fq_monerod_start_script = os.path.join(tmpl_dir, monerod_dir, bin_dir, monerod_start_script)
        fq_xmrig                = os.path.join(tmpl_dir, xmrig_dir, bin_dir, xmrig_binary)

        # Temp directory to house the systemd service files
        tmp_dir = os.path.join(TMP_DIR, DB4E_FIELD)
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        os.mkdir(tmp_dir)

        # Update the db4e service template with deployment values
        placeholders = {
            DB4E_USER_PLACEHOLDER: db4e_user,
            DB4E_GROUP_PLACEHOLDER: db4e_group,
            DB4E_DIR_PLACEHOLDER: fq_db4e_dir,
        }
        with open(fq_db4e_service_file, 'r') as f:
            service_contents = f.read()
            for key, val in placeholders.items():
                service_contents = service_contents.replace(f'[[{key}]]', str(val))
        tmp_service_file = os.path.join(tmp_dir, db4e_service_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

        # Update the P2Pool service templates with deployment values
        placeholders = {
            P2POOL_DIR_PLACEHOLDER: fq_p2pool_dir,
            DB4E_USER_PLACEHOLDER: db4e_user,
            DB4E_GROUP_PLACEHOLDER: db4e_group,
        }
        with open(fq_p2pool_service_file, 'r') as f:
            service_contents = f.read()
            for key, val in placeholders.items():
                service_contents = service_contents.replace(f'[[{key}]]', str(val))
        tmp_service_file = os.path.join(tmp_dir, p2pool_service_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)
        with open(fq_p2pool_socket_file, 'r') as f:
            service_contents = f.read()
            for key, val in placeholders.items():
                service_contents = service_contents.replace(f'[[{key}]]', str(val))
        tmp_service_file = os.path.join(tmp_dir, p2pool_socket_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

        # Update the Monero daemon service templates with deployment values
        placeholders = {
            MONEORD_DIR_PLACEHOLDER: fq_monerod_dir,
            DB4E_USER_PLACEHOLDER: db4e_user,
            DB4E_GROUP_PLACEHOLDER: db4e_group,
        }
        with open(fq_monerod_service_file, 'r') as f:
            service_contents = f.read()
            for key, val in placeholders.items():
                service_contents = service_contents.replace(f'[[{key}]]', str(val))
        tmp_service_file = os.path.join(tmp_dir, monerod_service_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)
        with open(fq_monerod_socket_file, 'r') as f:
            service_contents = f.read()
            for key, val in placeholders.items():
                service_contents = service_contents.replace(f'[[{key}]]', str(val))
        tmp_service_file = os.path.join(tmp_dir, monerod_socket_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

        # Update the XMRig miner service template with deployment values
        placeholders = {
            XMRIG_DIR_PLACEHOLDER: fq_xmrig_dir,
            DB4E_USER_PLACEHOLDER: db4e_user,
            DB4E_GROUP_PLACEHOLDER: db4e_group,
        }
        with open(fq_xmrig_service_file, 'r') as f:
            service_contents = f.read()
            for key, val in placeholders.items():
                service_contents = service_contents.replace(f'[[{key}]]', str(val))
        tmp_service_file = os.path.join(tmp_dir, xmrig_service_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

        # Copy in the Monero daemon, P2Pool and XMRig binaries and startup scripts
        shutil.copy(fq_p2pool, os.path.join(vendor_dir, p2pool_dir, bin_dir))
        shutil.copy(fq_p2pool_start_script, os.path.join(vendor_dir, p2pool_dir, bin_dir))
        shutil.copy(fq_monerod, os.path.join(vendor_dir, monerod_dir, bin_dir))
        shutil.copy(fq_monerod_start_script, os.path.join(vendor_dir, monerod_dir, bin_dir))
        shutil.copy(fq_xmrig, os.path.join(vendor_dir, xmrig_dir, bin_dir))

        # Run the bin/db4e-installer.sh
        db4e_install_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        fq_initial_setup = os.path.join(db4e_install_dir, bin_dir, initial_setup_script)
        try:
            cmd_result = subprocess.run(
                [SUDO_CMD, fq_initial_setup, db4e_dir, db4e_user, db4e_group, vendor_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                input=b"",
                timeout=10)
            stdout = cmd_result.stdout.decode().strip()
            stderr = cmd_result.stderr.decode().strip()

            # Check the return code
            if cmd_result.returncode != 0:
                results.append(result_row(DB4E_LABEL, ERROR_FIELD, f'Service install failed.\n\n{stderr}'))
                return results
            
            installer_output = f'{stdout}'
            results.append(result_row(DB4E_LABEL, GOOD_FIELD, installer_output))
            shutil.rmtree(tmp_dir)

        except Exception as e:
            results.append(result_row(DB4E_LABEL, ERROR_FIELD, f'Fatal error: {e}'))

        # Build the db4e deployment record
        db4e_rec[ENABLE_FIELD] = True
        db4e_rec[GROUP_FIELD] = db4e_group
        db4e_rec[INSTALL_DIR_FIELD] = db4e_install_dir
        db4e_rec[USER_FIELD] = db4e_user
        db4e_rec[VENDOR_DIR_FIELD] = vendor_dir
        # Update the repo deployment record
        self.depl_mgr.update_deployment(db4e_rec)
        return results


    def _check_form_data(self, user_wallet: str, db4e_group: str, vendor_dir: str):
        results = []
        error_flag = False
        if not user_wallet:
            results.append(result_row(MONERO_WALLET_LABEL, ERROR_FIELD, f"Missing {MONERO_WALLET_LABEL}"))
            error_flag = True
        if not db4e_group:
            results.append(result_row(DB4E_GROUP_LABEL, ERROR_FIELD, f"Missing {DB4E_GROUP_LABEL}"))
            error_flag = True
        if not vendor_dir:
            results.append(result_row(DEPLOYMENT_DIR_LABEL, ERROR_FIELD, f"Missing {DEPLOYMENT_DIR_LABEL}"))
            error_flag = True
        if error_flag:
            results.append(result_row (DB4E_LABEL, GOOD_FIELD, f"Click on Db4e Core to try again"))
        return (error_flag, results)



    def _handle_reinstall(self, db4e_rec: dict, user_wallet: str, vendor_dir: str, results: list, db4e_group: str):
        if db4e_rec:
            # The Mongo record for 'db4e' exists: Assume we're doing a reinstall
            results.append(result_row(DB4E_LABEL, WARN_FIELD, 'Db4E core already exists'))
            old_user_wallet = db4e_rec[USER_WALLET_FIELD]
            old_group = db4e_rec[GROUP_FIELD]
            old_vendor_dir = db4e_rec[VENDOR_DIR_FIELD]

            if user_wallet != old_user_wallet:
                results.append(result_row(MONERO_WALLET_LABEL, WARN_FIELD, 'Old Monero wallet record'))
                db4e_rec[USER_WALLET_FIELD] = user_wallet
                # Update the existing record with the wallet from the form
                self.depl_mgr.update_deployment(db4e_rec)
                results.append(result_row(MONERO_WALLET_LABEL, GOOD_FIELD, 'Updated Monero wallet'))
            if db4e_group != old_group:
                # The group from the new install doesn't match what's in Mongo, set a flag for the shell
                # installer to delete the old
                results.append(result_row(DB4E_GROUP_LABEL, WARN_FIELD, f'Found old Db4E group ({old_group}) record, ignoring it'))
            if vendor_dir != old_vendor_dir:
                results.append(result_row(DEPLOYMENT_DIR_LABEL, WARN_FIELD, f'Old deployment directory ({old_vendor_dir}) record'))
        else:
            db4e_rec = self.db.get_new_rec(DB4E_FIELD)
            db4e_rec[USER_WALLET_FIELD] = user_wallet
            self.depl_mgr.add_deployment(db4e_rec)
        return (db4e_rec, results)