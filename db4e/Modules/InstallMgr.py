"""
db4e/Modules/InstallMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

import os, shutil
from datetime import datetime, timezone
import tempfile
import subprocess
import stat

from rich.pretty import Pretty
from textual.containers import Container

from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Modules.ConfigMgr import Config
from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.OpsMgr import OpsMgr
from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.Helper import result_row, get_effective_identity, update_component_values
from db4e.Constants.Fields import (
    BIN_DIR_FIELD, BLOCKCHAIN_DIR_FIELD, ELEMENT_TYPE_FIELD, CONF_DIR_FIELD,
    DB4E_DIR_FIELD, DB4E_FIELD, ENABLE_FIELD, ERROR_FIELD, GOOD_FIELD,
    GROUP_FIELD, INSTALL_DIR_FIELD, INITIAL_SETUP_FIELD, LOG_DIR_FIELD,
    MONEROD_FIELD, P2POOL_FIELD, PROCESS_FIELD, RUN_DIR_FIELD,
    SERVICE_FILE_FIELD, SOCKET_FILE_FIELD, START_SCRIPT_FIELD,
    SYSTEMD_DIR_FIELD, TEMPLATE_DIR_FIELD, TEMPLATE_FIELD, HEALTH_MSGS_FIELD, 
    TMP_DIR_ENVIRON_FIELD, USER_FIELD, USER_WALLET_FIELD, 
    VENDOR_DIR_FIELD, VERSION_FIELD, WARN_FIELD, XMRIG_FIELD, 
)
from db4e.Constants.SystemdTemplates import (
    DB4E_USER_PLACEHOLDER, DB4E_GROUP_PLACEHOLDER, DB4E_DIR_PLACEHOLDER,
    INSTALL_DIR_PLACEHOLDER, MONEROD_DIR_PLACEHOLDER, P2POOL_DIR_PLACEHOLDER, 
    PYTHON_PLACEHOLDER, XMRIG_DIR_PLACEHOLDER)
from db4e.Constants.Labels import (
    DB4E_GROUP_LABEL, DB4E_LABEL, DB4E_USER_LABEL, VENDOR_DIR_LABEL, 
    INSTALL_DIR_LABEL, MONEROD_LABEL, USER_WALLET_LABEL, P2POOL_LABEL, 
    XMRIG_LABEL)
from db4e.Constants.Defaults import (
    DB4E_OLD_GROUP_ENVIRON_DEFAULT, DEPLOYMENT_COL_DEFAULT, PYTHON_DEFAULT, 
    SUDO_CMD_DEFAULT, TMP_DIR_DEFAULT)
from db4e.Constants.SystemdTemplates import DB4E_DIR_PLACEHOLDER

# The Mongo collection that houses the deployment records
DEPL_COL = DEPLOYMENT_COL_DEFAULT
DB4E_OLD_GROUP_ENVIRON = DB4E_OLD_GROUP_ENVIRON_DEFAULT
TMP_DIR = TMP_DIR_DEFAULT
SUDO_CMD = SUDO_CMD_DEFAULT

class InstallMgr(Container):
    
    def __init__(self, config: Config):
        super().__init__()
        self.ini = config
        self.ops_mgr = OpsMgr(config=config)
        self.depl_mgr = DeploymentMgr(config=config)
        self.col_name = DEPLOYMENT_COL_DEFAULT
        self.tmp_dir = None

    def initial_setup(self, form_data: dict) -> dict:
        # Track the progress of the initial install
        abort_install = False

        # This is the data from the form on the InitialSetup pane
        user_wallet = form_data[USER_WALLET_FIELD]
        vendor_dir = form_data[VENDOR_DIR_FIELD]

        #print(f"InstallMgr:initial_setup(): wallet: {user_wallet}, vendor_dir: {vendor_dir}")

        #rec = self.depl_mgr.get_deployment(elem_type=DB4E_FIELD)
        rec = self.ops_mgr.get_deployment(elem_type=DB4E_FIELD)
        rec[HEALTH_MSGS_FIELD] = [result_row(
            DB4E_LABEL, GOOD_FIELD, 
            f"Retrieved {DB4E_LABEL} deployment record"
        )]

        # Check that the user entered their wallet
        rec, abort_install = self._check_wallet(user_wallet=user_wallet, rec=rec)
        if abort_install:
            rec[HEALTH_MSGS_FIELD].append(result_row(
                DB4E_LABEL, ERROR_FIELD,
                f"Fatal error, aborting install"))
            return rec
        
        # Check that the user entered a vendor directory
        rec, abort_install = self._check_vendor_dir(vendor_dir=vendor_dir, rec=rec)
        if abort_install:
            rec[HEALTH_MSGS_FIELD].append(result_row(
                DB4E_LABEL, ERROR_FIELD,
                f"Fatal error, aborting install"))
            return rec

        # Create the vendor directory on the filesystem
        results, abort_install = self._create_vendor_dir(
            vendor_dir=vendor_dir
        )
        if abort_install:
            rec[HEALTH_MSGS_FIELD] += results
            rec[HEALTH_MSGS_FIELD].append(result_row(
                DB4E_LABEL, ERROR_FIELD,
                f"Fatal error, aborting install"))
            return rec
        
        # Update the Mongo record
        rec = self._create_vendor_dir_rec(vendor_dir=vendor_dir, rec=rec)

        # Create the Db4E vendor directories
        results += self._create_db4e_dirs(vendor_dir=vendor_dir)

        # Copy in the Db4E start script
        results += self._copy_db4e_files(vendor_dir=vendor_dir)

        # Generate the Db4E service file (installed by the sudo installer)
        self._generate_db4e_service_file(vendor_dir=vendor_dir)

        # Create the Monero daemon vendor directories
        results += self._create_monerod_dirs(vendor_dir=vendor_dir)

        # Generate the Monero service files (installed by the sudo installer)
        self._generate_tmp_monerod_service_files(vendor_dir=vendor_dir)

        # Copy in the Monero daemon and start script
        results += self._copy_monerod_files(vendor_dir=vendor_dir)

        # Create the P2Pool daemon vendor directories
        results += self._create_p2pool_dirs(vendor_dir=vendor_dir)

        # Generate the P2Pool service files (installed by the sudo installer)
        self._generate_p2pool_service_files(vendor_dir=vendor_dir)

        # Copy in the P2Pool daemon and start script
        results += self._copy_p2pool_files(vendor_dir=vendor_dir)

        # Create the XMRig miner vendor directories
        results += self._create_xmrig_dirs(vendor_dir=vendor_dir)

        # Generate the XMRig service file (installed by the sudo installer)
        self._generate_xmrig_service_file(vendor_dir=vendor_dir)

        # Copy in the XMRig miner
        results += self._copy_xmrig_file(vendor_dir=vendor_dir)

        # Run the installer (with sudo)
        results += self._run_sudo_installer(
            vendor_dir=vendor_dir, db4e_rec=rec)

        # Return the results
        rec[HEALTH_MSGS_FIELD] += results
        return rec
        

    def initial_setup_proceed(self, form_data: dict):
        rec = self.ops_mgr.get_deployment(elem_type=DB4E_FIELD)
        #print(f"InstallMgr:initial_setup_proceed(): {rec}")
        return rec
        

    def _check_wallet(self, user_wallet:str, rec: dict):
        #print(f"InstallMgr:_check_wallet(): user_wallet: {user_wallet}")
        abort_install = False
        # User did not provide any wallet
        if not user_wallet:
            abort_install = True
            rec[HEALTH_MSGS_FIELD].append(result_row(
                USER_WALLET_LABEL, ERROR_FIELD,
                f"{USER_WALLET_LABEL} missing"))
            return rec, abort_install
        
        rec = update_component_values(rec=rec, updates={USER_WALLET_FIELD: user_wallet})
        query = {ELEMENT_TYPE_FIELD: DB4E_FIELD}
        self.depl_mgr.update_one(query, rec)
        rec[HEALTH_MSGS_FIELD].append(result_row(
            USER_WALLET_LABEL, GOOD_FIELD,
            f"Set the user wallet: {user_wallet[:7]}..."))

        return rec, abort_install        


    def _check_vendor_dir(self, vendor_dir: str, rec: dict):
        #print(f"InstallMgr:_vendor_dir(): {vendor_dir}")
        abort_install = False
        if not vendor_dir:
            abort_install = True
            rec[HEALTH_MSGS_FIELD].append(result_row(
                VENDOR_DIR_LABEL, ERROR_FIELD,
                f"{VENDOR_DIR_LABEL} missing"))
        return rec, abort_install
        
    # Copy Db4E files
    def _copy_db4e_files(self, vendor_dir):
        results = []
        bin_dir              = self.ini.config[DB4E_FIELD][BIN_DIR_FIELD]
        db4e_start_script = self.ini.config[DB4E_FIELD][START_SCRIPT_FIELD]
        db4e_version      = self.ini.config[DB4E_FIELD][VERSION_FIELD]
        db4e_src_dir = DB4E_FIELD
        db4e_dest_dir = DB4E_FIELD + '-' + str(db4e_version)
        # Template directory
        tmpl_dir = self.ops_mgr.get_dir(TEMPLATE_FIELD)
        # Substitute placeholder in the db4e-service.sh script
        install_dir = self.ops_mgr.get_dir(INSTALL_DIR_FIELD)
        python = self.ops_mgr.get_dir(PYTHON_DEFAULT)
        placeholders = {
            PYTHON_PLACEHOLDER: python,
            INSTALL_DIR_PLACEHOLDER: install_dir}
        fq_src_script =  os.path.join(tmpl_dir, db4e_src_dir, bin_dir, db4e_start_script)
        fq_dest_script = os.path.join(vendor_dir, db4e_dest_dir, bin_dir, db4e_start_script)
        script_contents = self._replace_placeholders(fq_src_script, placeholders)
        with open(fq_dest_script, 'w') as f:
            f.write(script_contents)        
        # Make it executable
        current_permissions = os.stat(fq_dest_script).st_mode
        new_permissions = current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        os.chmod(fq_dest_script, new_permissions)
        results.append(result_row(
            DB4E_LABEL, GOOD_FIELD,
            f"Installed: {fq_dest_script}"))
        return results
        
    # Copy monerod files
    def _copy_monerod_files(self, vendor_dir):
        results = []
        bin_dir              = self.ini.config[DB4E_FIELD][BIN_DIR_FIELD]
        monerod_binary       = self.ini.config[MONEROD_FIELD][PROCESS_FIELD]
        monerod_start_script = self.ini.config[MONEROD_FIELD][START_SCRIPT_FIELD]
        monerod_version      = self.ini.config[MONEROD_FIELD][VERSION_FIELD]
        monerod_dir = MONEROD_FIELD + '-' + str(monerod_version)
        # Template directory
        tmpl_dir = self.ops_mgr.get_dir(TEMPLATE_FIELD)
        # Copy in the Monero daemon and startup scripts
        fq_dst_bin_dir =  os.path.join(vendor_dir, monerod_dir, bin_dir)
        fq_dst_monerod_dest_script = os.path.join(
            vendor_dir, monerod_dir, bin_dir, monerod_start_script)
        fq_src_monerod = os.path.join(tmpl_dir, monerod_dir, bin_dir, monerod_binary)

        shutil.copy(fq_src_monerod, fq_dst_bin_dir)
        results.append(result_row(
            MONEROD_LABEL, GOOD_FIELD,
            f"Installed: {fq_dst_bin_dir}/{monerod_binary}"))
        fq_src_monerod_start_script = os.path.join(
            tmpl_dir, monerod_dir, bin_dir, monerod_start_script)

        shutil.copy(fq_src_monerod_start_script, fq_dst_monerod_dest_script)
        results.append(result_row(
            MONEROD_LABEL, GOOD_FIELD,
            f"Installed: {fq_dst_monerod_dest_script}"))

        # Make it executable
        current_permissions = os.stat(fq_dst_monerod_dest_script).st_mode
        new_permissions = current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        os.chmod(fq_dst_monerod_dest_script, new_permissions)
        return results

    def _copy_p2pool_files(self, vendor_dir):
        results = []
        bin_dir = self.ini.config[DB4E_FIELD][BIN_DIR_FIELD]
        p2pool_binary = self.ini.config[P2POOL_FIELD][PROCESS_FIELD]
        p2pool_start_script  = self.ini.config[P2POOL_FIELD][START_SCRIPT_FIELD]
        # Template directory
        tmpl_dir = self.ops_mgr.get_dir(TEMPLATE_FIELD)
        # P2Pool directory
        p2pool_version = self.ini.config[P2POOL_FIELD][VERSION_FIELD]
        p2pool_dir = P2POOL_FIELD +'-' + str(p2pool_version)
        # Copy in the P2Pool daemon and startup script
        fq_src_p2pool = os.path.join(tmpl_dir, p2pool_dir, bin_dir, p2pool_binary)
        fq_dst_bin_dir = os.path.join(vendor_dir, p2pool_dir, bin_dir)
        fq_src_p2pool_start_script  = os.path.join(tmpl_dir, p2pool_dir, bin_dir, p2pool_start_script)
        fq_dst_p2pool_start_script = os.path.join(vendor_dir, p2pool_dir, bin_dir, p2pool_start_script)
        shutil.copy(fq_src_p2pool, fq_dst_bin_dir)
        results.append(result_row(
            P2POOL_LABEL, GOOD_FIELD,
            f"Installed: {fq_dst_bin_dir}/{p2pool_binary}"))
        shutil.copy(fq_src_p2pool_start_script, fq_dst_p2pool_start_script)
        # Make it executable
        current_permissions = os.stat(fq_dst_p2pool_start_script).st_mode
        new_permissions = current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        os.chmod(fq_dst_p2pool_start_script, new_permissions)
        results.append(result_row(
            P2POOL_LABEL, GOOD_FIELD,
            f"Installed: {fq_dst_p2pool_start_script}"))
        return results

    def _copy_xmrig_file(self, vendor_dir):
        results = []
        bin_dir = self.ini.config[DB4E_FIELD][BIN_DIR_FIELD]
        xmrig_binary = self.ini.config[XMRIG_FIELD][PROCESS_FIELD]
        # XMRig directory
        xmrig_version = self.ini.config[XMRIG_FIELD][VERSION_FIELD]
        xmrig_dir = XMRIG_FIELD + '-' + str(xmrig_version)
        # Template directory
        tmpl_dir = self.ops_mgr.get_dir(TEMPLATE_FIELD)
        fq_dst_xmrig_bin_dir = os.path.join(vendor_dir, xmrig_dir, bin_dir)
        fq_src_xmrig = os.path.join(tmpl_dir, xmrig_dir, bin_dir, xmrig_binary)
        shutil.copy(fq_src_xmrig, fq_dst_xmrig_bin_dir)
        results.append(result_row(
            XMRIG_LABEL, GOOD_FIELD,
            f"Installed: {fq_dst_xmrig_bin_dir}/{xmrig_binary}"))
        return results

    def _create_db4e_dirs(self, vendor_dir):
        #print(f"InstallMgr:_create_db4e_dirs(): vendor_dir {vendor_dir}")
        results = []
        bin_dir = self.ini.config[DB4E_FIELD][BIN_DIR_FIELD]
        log_dir = self.ini.config[DB4E_FIELD][LOG_DIR_FIELD]
        db4e_version = self.ini.config[DB4E_FIELD][VERSION_FIELD]
        db4e_with_version = DB4E_FIELD + '-' + str(db4e_version)
        fq_db4e_dir = os.path.join(vendor_dir, db4e_with_version)
        # Create the base Db4E directory
        os.makedirs(os.path.join(fq_db4e_dir))
        results.append(result_row(
            DB4E_LABEL, GOOD_FIELD,
            f"Created directory: {fq_db4e_dir}"))
        # Create the sub-directories
        for sub_dir in [bin_dir, log_dir]:
            os.mkdir(os.path.join(fq_db4e_dir, sub_dir))
        # Create a symlink
        os.chdir(vendor_dir)
        os.symlink(
            os.path.join(db4e_with_version),
            os.path.join(DB4E_FIELD))
        # Create a health message, the directories will be logged later...
        results.append(result_row(
            DB4E_LABEL, GOOD_FIELD,
            f"Created symlink to directory: {DB4E_FIELD} > {db4e_with_version}"))
        return results

    def _create_monerod_dirs(self, vendor_dir):
        results = []
        bin_dir = self.ini.config[DB4E_FIELD][BIN_DIR_FIELD]
        conf_dir = self.ini.config[DB4E_FIELD][CONF_DIR_FIELD]
        log_dir = self.ini.config[DB4E_FIELD][LOG_DIR_FIELD]
        run_dir = self.ini.config[DB4E_FIELD][RUN_DIR_FIELD]
        blockchain_dir = self.ini.config[MONEROD_FIELD][BLOCKCHAIN_DIR_FIELD]
        monerod_version = self.ini.config[MONEROD_FIELD][VERSION_FIELD]
        monerod_with_version = MONEROD_FIELD + '-' + str(monerod_version)
        fq_monerod_dir = os.path.join(vendor_dir, monerod_with_version)

        # Create the base Monero directory
        os.mkdir(os.path.join(fq_monerod_dir))
        results.append(result_row(
            MONEROD_LABEL, GOOD_FIELD,
            f"Created directory: {fq_monerod_dir}"))

        os.mkdir(os.path.join(vendor_dir, blockchain_dir))
        results.append(result_row(
            MONEROD_LABEL, GOOD_FIELD,
            f"Created Monero blockchain directory: {fq_monerod_dir}"))

        # Create the sub-directories
        for sub_dir in [bin_dir, conf_dir, run_dir, log_dir]:
            fq_sub_dir = os.path.join(fq_monerod_dir, sub_dir)
            os.mkdir(fq_sub_dir)
            results.append(result_row(
                MONEROD_LABEL, GOOD_FIELD,
                f"Created directory: {fq_sub_dir}"))

        os.chdir(vendor_dir)
        os.symlink(
            os.path.join(monerod_with_version),
            os.path.join(MONEROD_FIELD))
        # Create a health message, the directories will be logged later...
        results.append(result_row(
            MONEROD_LABEL, GOOD_FIELD,
            f"Created symlink to directory: {MONEROD_FIELD} > {monerod_with_version}"))
        return results

    def _create_p2pool_dirs(self, vendor_dir):
        results = []
        bin_dir = self.ini.config[DB4E_FIELD][BIN_DIR_FIELD]
        conf_dir = self.ini.config[DB4E_FIELD][CONF_DIR_FIELD]
        run_dir = self.ini.config[DB4E_FIELD][RUN_DIR_FIELD]
        p2pool_version = self.ini.config[P2POOL_FIELD][VERSION_FIELD]
        p2pool_with_version = P2POOL_FIELD + '-' + str(p2pool_version)  
        fq_p2pool_dir = os.path.join(vendor_dir, p2pool_with_version)

        # Create the base P2Pool directory
        os.mkdir(os.path.join(fq_p2pool_dir))
        results.append(result_row(
            P2POOL_LABEL, GOOD_FIELD,
            f"Created directory ({fq_p2pool_dir})"
        ))
        # Create the sub directories
        for sub_dir in [bin_dir, conf_dir, run_dir]:
            fq_sub_dir = os.path.join(fq_p2pool_dir, sub_dir)
            os.mkdir(fq_sub_dir)
            results.append(result_row(
                P2POOL_LABEL, GOOD_FIELD,
                f"Created directory: {fq_sub_dir}"))
        os.chdir(vendor_dir)
        os.symlink(
            os.path.join(p2pool_with_version),
            os.path.join(P2POOL_FIELD))
        results.append(result_row(
            P2POOL_LABEL, GOOD_FIELD,
            f"Created symlink to directory: {P2POOL_FIELD} > {p2pool_with_version}"))
        
        return results


    def _create_vendor_dir(self, vendor_dir):
        #print(f"InstallMgr:_create_vendor_dir(): vendor_dir {vendor_dir}")
        abort_install = False
        results = []
        if os.path.exists(vendor_dir):
            results.append(result_row(
                VENDOR_DIR_LABEL, WARN_FIELD, 
                f'Found existing deployment directory: {vendor_dir}'))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            backup_vendor_dir = vendor_dir + '.' + timestamp
            try:
                os.rename(vendor_dir, backup_vendor_dir)
                results.append(result_row(
                    VENDOR_DIR_LABEL, WARN_FIELD, 
                    f'Backed up old deployment directory: {backup_vendor_dir}'))
            except (PermissionError, OSError, FileNotFoundError) as e:
                results.append(result_row(
                    VENDOR_DIR_LABEL, WARN_FIELD, 
                    'Failed to backup old deployment directory: ' +
                    f'{backup_vendor_dir}\n{e}'))
                abort_install = True
                return results, abort_install # Abort the install

        try:
            os.makedirs(vendor_dir)
            results.append(result_row(
                VENDOR_DIR_LABEL, GOOD_FIELD, 
                f"Created directory: {vendor_dir}"))        
        except (PermissionError, FileNotFoundError, FileExistsError) as e:
            results.append(result_row(
                VENDOR_DIR_LABEL, WARN_FIELD, 
                f'Failed to create directory: {vendor_dir}\n{e}'))
            abort_install = True
            return results, abort_install

        return results, abort_install

    def _create_vendor_dir_rec(self, vendor_dir, rec):
        rec = update_component_values(rec=rec, updates={VENDOR_DIR_FIELD: vendor_dir})
        query = {ELEMENT_TYPE_FIELD: DB4E_FIELD}
        self.depl_mgr.update_one(query, rec)
        rec[HEALTH_MSGS_FIELD].append(result_row(
            VENDOR_DIR_LABEL, GOOD_FIELD, 
            f"Set the {VENDOR_DIR_LABEL}: {vendor_dir}"))
        return rec


    def _create_xmrig_dirs(self, vendor_dir):
        results = []
        bin_dir = self.ini.config[DB4E_FIELD][BIN_DIR_FIELD]
        conf_dir = self.ini.config[DB4E_FIELD][CONF_DIR_FIELD]
        xmrig_version = self.ini.config[XMRIG_FIELD][VERSION_FIELD]
        xmrig_with_version = XMRIG_FIELD + '-' + str(xmrig_version)
        fq_xmrig_dir = os.path.join(vendor_dir, xmrig_with_version)
        os.mkdir(os.path.join(fq_xmrig_dir))
        results.append(result_row(
            XMRIG_LABEL, GOOD_FIELD,
            f"Created directory: {fq_xmrig_dir}"))
        for sub_dir in [bin_dir, conf_dir]:
            fq_sub_dir = os.path.join(fq_xmrig_dir, sub_dir)
            os.mkdir(fq_sub_dir)
            results.append(result_row(
                XMRIG_LABEL, GOOD_FIELD,
                f"Created directory: {fq_sub_dir}"))
        os.chdir(vendor_dir)
        os.symlink(xmrig_with_version, XMRIG_FIELD)
        results.append(result_row(
            XMRIG_LABEL, GOOD_FIELD,
            f"Created symlink to directory: {XMRIG_FIELD} > {xmrig_with_version}"))
        return results

    # Update the db4e service template with deployment values
    def _generate_db4e_service_file(self, vendor_dir):
        effective_id = get_effective_identity()
        user = effective_id[USER_FIELD]
        group = effective_id[GROUP_FIELD]
        systemd_dir = self.ini.config[DB4E_FIELD][SYSTEMD_DIR_FIELD]
        db4e_service_file = self.ini.config[DB4E_FIELD][SERVICE_FILE_FIELD]
        tmpl_dir = self.ops_mgr.get_dir(TEMPLATE_FIELD)
        tmp_dir = self._get_tmp_dir()
        fq_db4e_dir = os.path.join(vendor_dir, DB4E_FIELD)
        placeholders = {
            DB4E_USER_PLACEHOLDER: user,
            DB4E_GROUP_PLACEHOLDER: group,
            DB4E_DIR_PLACEHOLDER: fq_db4e_dir,
        }
        fq_db4e_service_file = os.path.join(tmpl_dir, DB4E_FIELD, systemd_dir, db4e_service_file)
        service_contents = self._replace_placeholders(fq_db4e_service_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, db4e_service_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

    def _generate_tmp_monerod_service_files(self, vendor_dir):
        monerod_dir          = MONEROD_FIELD
        systemd_dir          = self.ini.config[DB4E_FIELD][SYSTEMD_DIR_FIELD]
        monerod_service_file = self.ini.config[MONEROD_FIELD][SERVICE_FILE_FIELD]
        monerod_socket_file  = self.ini.config[MONEROD_FIELD][SOCKET_FILE_FIELD]
        monerod_version      = self.ini.config[MONEROD_FIELD][VERSION_FIELD]
        monerod_with_version = MONEROD_FIELD + '-' + str(monerod_version)
        # Use the effective UID/GID for the Db4E user/group
        effective_id = get_effective_identity()
        user = effective_id[USER_FIELD]
        group = effective_id[GROUP_FIELD]
        # Template directory
        tmpl_dir = self.ops_mgr.get_dir(TEMPLATE_FIELD)
        # Temporary directory
        tmp_dir = self._get_tmp_dir()
        # Substitution placeholders in the service template files
        placeholders = {
            MONEROD_DIR_PLACEHOLDER: os.path.join(vendor_dir, monerod_dir),
            DB4E_USER_PLACEHOLDER: user,
            DB4E_GROUP_PLACEHOLDER: group,
        }
        fq_monerod_service_file = os.path.join(tmpl_dir, monerod_with_version, systemd_dir, monerod_service_file)
        service_contents = self._replace_placeholders(fq_monerod_service_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, monerod_service_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)
        fq_monerod_socket_file = os.path.join(
            tmpl_dir, monerod_with_version, systemd_dir, monerod_socket_file)
        service_contents = self._replace_placeholders(fq_monerod_socket_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, monerod_socket_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

    def _generate_p2pool_service_files(self, vendor_dir):
        systemd_dir          = self.ini.config[DB4E_FIELD][SYSTEMD_DIR_FIELD]
        p2pool_service_file  = self.ini.config[P2POOL_FIELD][SERVICE_FILE_FIELD]
        p2pool_socket_file   = self.ini.config[P2POOL_FIELD][SOCKET_FILE_FIELD]
        p2pool_version       = self.ini.config[P2POOL_FIELD][VERSION_FIELD]
        p2pool_with_version  = P2POOL_FIELD + '-' + str(p2pool_version)
        # Use the effective UID/GID for the Db4E user/group
        effective_id = get_effective_identity()
        user = effective_id[USER_FIELD]
        group = effective_id[GROUP_FIELD]
        # Template directory
        tmpl_dir = self.ops_mgr.get_dir(TEMPLATE_FIELD)
        # Temporary directory
        tmp_dir = self._get_tmp_dir()
        # P2Pool directory
        fq_p2pool_dir = os.path.join(vendor_dir, P2POOL_FIELD)
        # 
        placeholders = {
            P2POOL_DIR_PLACEHOLDER: fq_p2pool_dir,
            DB4E_USER_PLACEHOLDER: user,
            DB4E_GROUP_PLACEHOLDER: group,
        }
        fq_p2pool_service_file  = os.path.join(
            tmpl_dir, p2pool_with_version, systemd_dir, p2pool_service_file)
        service_contents = self._replace_placeholders(fq_p2pool_service_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, p2pool_service_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)
        fq_p2pool_socket_file   = os.path.join(
            tmpl_dir, p2pool_with_version, systemd_dir, p2pool_socket_file)
        service_contents = self._replace_placeholders(fq_p2pool_socket_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, p2pool_socket_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

    def _generate_xmrig_service_file(self, vendor_dir):
        systemd_dir        = self.ini.config[DB4E_FIELD][SYSTEMD_DIR_FIELD]
        xmrig_service_file = self.ini.config[XMRIG_FIELD][SERVICE_FILE_FIELD]
        xmrig_version      = self.ini.config[XMRIG_FIELD][VERSION_FIELD]
        xmrig_with_version = XMRIG_FIELD + '-' + str(xmrig_version)
        # Use the effective UID/GID for the Db4E user/group
        effective_id = get_effective_identity()
        user = effective_id[USER_FIELD]
        group = effective_id[GROUP_FIELD]
        # Template directory
        tmpl_dir = self.ops_mgr.get_dir(TEMPLATE_FIELD)
        # Temporary directory
        tmp_dir = self._get_tmp_dir()
        # XMRig directory
        fq_xmrig_dir = os.path.join(vendor_dir, XMRIG_FIELD)
        placeholders = {
            XMRIG_DIR_PLACEHOLDER: fq_xmrig_dir,
            DB4E_USER_PLACEHOLDER: user,
            DB4E_GROUP_PLACEHOLDER: group,
        }
        fq_xmrig_service_file   = os.path.join(
            tmpl_dir, xmrig_with_version, systemd_dir, xmrig_service_file)
        service_contents = self._replace_placeholders(fq_xmrig_service_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, xmrig_service_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

    def _get_templates_dir(self):
        # Helper function
        templates_dir = self.ini.config[DB4E_FIELD][TEMPLATE_DIR_FIELD]
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', templates_dir))
    
    def _get_tmp_dir(self):
        # Helper function
        if not self.tmp_dir:
            tmp_obj = tempfile.TemporaryDirectory()
            self.tmp_dir = tmp_obj.name  # Store path string
            self._tmp_obj = tmp_obj      # Keep a reference to the object
        return self.tmp_dir

    def _replace_placeholders(self, path: str, placeholders: dict) -> str:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Template file ({path}) not found")
        with open(path, 'r') as f:
            content = f.read()
        for key, val in placeholders.items():
            content = content.replace(f'[[{key}]]', str(val))
        return content

    def _run_sudo_installer(self, vendor_dir, db4e_rec):
        #print(f"InstallMgr:_run_sudo_installer()")
        results = []
        bin_dir = self.ini.config[DB4E_FIELD][BIN_DIR_FIELD]
        # Use the effective UID/GID for the Db4E user/group
        effective_id = get_effective_identity()
        user = effective_id[USER_FIELD]
        group = effective_id[GROUP_FIELD]
        # Temporary directory
        tmp_dir = self._get_tmp_dir()
        db4e_install_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        # Additional config settings
        db4e_dir             = self.ini.config[DB4E_FIELD][DB4E_DIR_FIELD]
        initial_setup_script = self.ini.config[DB4E_FIELD][INITIAL_SETUP_FIELD]
        # Set the location of the temp dir in an environment variable
        env_setting = f"{TMP_DIR_ENVIRON_FIELD}={self.tmp_dir}"
        # Run the bin/db4e-installer.sh
        fq_initial_setup = os.path.join(db4e_install_dir, bin_dir, initial_setup_script)
        try:
            cmd_result = subprocess.run(
                [SUDO_CMD, "env", env_setting, fq_initial_setup, db4e_dir, user, group, vendor_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                input=b"",
                timeout=10)
            stdout = cmd_result.stdout.decode().strip()
            stderr = cmd_result.stderr.decode().strip()

            # Check the return code
            if cmd_result.returncode != 0:
                results.append(result_row(DB4E_LABEL, ERROR_FIELD, f'Service install failed.\n\n{stderr}'))
                shutil.rmtree(tmp_dir)
                return results
            
            installer_output = f'{stdout}'
            for line in installer_output.split('\n'):
                results.append(result_row(DB4E_LABEL, GOOD_FIELD, line))
            shutil.rmtree(tmp_dir)

        except Exception as e:
            results.append(result_row(DB4E_LABEL, ERROR_FIELD, f'Fatal error: {e}'))

        # Build the db4e deployment record
        db4e_rec[ENABLE_FIELD] = True
        # Update the repo deployment record
        self.ops_mgr.update_deployment(db4e_rec)
        return results
    


