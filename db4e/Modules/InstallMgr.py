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
from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.OpsMgr import OpsMgr
from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.Db4E import Db4E
from db4e.Modules.Helper import result_row, get_effective_identity, update_component_values
from db4e.Constants.Fields import (
    DB4E_FIELD, ERROR_FIELD, GOOD_FIELD, INSTALL_DIR_FIELD, TEMPLATE_FIELD,  
    TMP_DIR_ENVIRON_FIELD, ELEMENT_FIELD, WARN_FIELD, XMRIG_FIELD, MONEROD_FIELD, 
    P2POOL_FIELD)
from db4e.Constants.SystemdTemplates import (
    DB4E_USER_PLACEHOLDER, DB4E_GROUP_PLACEHOLDER, DB4E_DIR_PLACEHOLDER,
    INSTALL_DIR_PLACEHOLDER, MONEROD_DIR_PLACEHOLDER, P2POOL_DIR_PLACEHOLDER, 
    PYTHON_PLACEHOLDER, XMRIG_DIR_PLACEHOLDER)
from db4e.Constants.Labels import (
    DB4E_LABEL, VENDOR_DIR_LABEL, 
    MONEROD_LABEL, USER_WALLET_LABEL, P2POOL_LABEL, 
    XMRIG_LABEL)
from db4e.Constants.Defaults import (
    DB4E_OLD_GROUP_ENVIRON_DEFAULT, DEPLOYMENT_COL_DEFAULT, PYTHON_DEFAULT, 
    SUDO_CMD_DEFAULT, TMP_DIR_DEFAULT, BIN_DIR_DEFAULT, DB4E_START_SCRIPT_DEFAULT, 
    DB4E_VERSION_DEFAULT, MONEROD_PROCESS_DEFAULT, MONEROD_VERSION_DEFAULT, 
    MONEROD_START_SCRIPT_DEFAULT, P2POOL_PROCESS_DEFAULT, P2POOL_START_SCRIPT_DEFAULT,
    P2POOL_VERSION_DEFAULT, XMRIG_PROCESS_DEFAULT, LOG_DIR_DEFAULT, SYSTEMD_DIR_DEFAULT,
    XMRIG_VERSION_DEFAULT, CONF_DIR_DEFAULT, RUN_DIR_DEFAULT, BLOCKCHAIN_DIR_DEFAULT,
    DB4E_SERVICE_FILE_DEFAULT, MONEROD_SERVICE_FILE_DEFAULT, P2POOL_SERVICE_FILE_DEFAULT,
    XMRIG_SERVICE_FILE_DEFAULT, MONEROD_SOCKET_SERVICE_DEFAULT, 
    TEMPLATES_DIR_DEFAULT, P2POOL_SERVICE_SOCKET_FILE_DEFAULT, 
    DB4E_INITIAL_SETUP_SCRIPT_DEFAULT)
from db4e.Constants.SystemdTemplates import DB4E_DIR_PLACEHOLDER

# The Mongo collection that houses the deployment records
DEPL_COL = DEPLOYMENT_COL_DEFAULT
DB4E_OLD_GROUP_ENVIRON = DB4E_OLD_GROUP_ENVIRON_DEFAULT
TMP_DIR = TMP_DIR_DEFAULT
SUDO_CMD = SUDO_CMD_DEFAULT

class InstallMgr(Container):
    
    def __init__(self):
        super().__init__()
        self.ops_mgr = OpsMgr()
        self.depl_mgr = DeploymentMgr()
        self.col_name = DEPLOYMENT_COL_DEFAULT
        self.tmp_dir = None

    def initial_setup(self, form_data: dict) -> dict:
        print(f"InstallMgr:initial_setup(): {form_data}")
        # Track the progress of the initial install
        abort_install = False

        # This is the data from the form on the InitialSetup pane
        db4e = form_data[ELEMENT_FIELD]
        db4e.pop_msgs()
        user_wallet = db4e.user_wallet()
        vendor_dir = db4e.vendor_dir()

        print(f"InstallMgr:initial_setup(): user_wallet: {user_wallet}")
        print(f"InstallMgr:initial_setup(): vendor_dir: {vendor_dir}")

        # Check that the user entered their wallet
        db4e, abort_install = self._check_wallet(user_wallet=user_wallet, db4e=db4e)
        if abort_install:
            db4e.msg(DB4E_LABEL, ERROR_FIELD, f"Fatal error, aborting install")
            return db4e
        
        # Check that the user entered a vendor directory
        db4e, abort_install = self._check_vendor_dir(vendor_dir=vendor_dir, db4e=db4e)
        if abort_install:
            db4e.msg(DB4E_LABEL, ERROR_FIELD, f"Fatal error, aborting install")
            return db4e

        # Create the vendor directory on the filesystem
        db4e, abort_install = self._create_vendor_dir(vendor_dir=vendor_dir, db4e=db4e)
        if abort_install:
            db4e.msg(DB4E_LABEL, ERROR_FIELD, f"Fatal error, aborting install")
            return db4e
        

        # We have everything we need to finish the install. Update the record.
        self.depl_mgr.update_deployment(db4e)

        # Create the Db4E vendor directories
        db4e = self._create_db4e_dirs(vendor_dir=vendor_dir, db4e=db4e)

        # Copy in the Db4E start script
        #results += self._copy_db4e_files(vendor_dir=vendor_dir)

        # Generate the Db4E service file (installed by the sudo installer)
        self._generate_db4e_service_file(db4e=db4e)

        # Create the Monero daemon vendor directories
        db4e = self._create_monerod_dirs(vendor_dir=vendor_dir, db4e=db4e)

        # Generate the Monero service files (installed by the sudo installer)
        self._generate_tmp_monerod_service_files(vendor_dir=vendor_dir, db4e=db4e)

        # Copy in the Monero daemon and start script
        db4e = self._copy_monerod_files(vendor_dir=vendor_dir, db4e=db4e)

        # Create the P2Pool daemon vendor directories
        db4e = self._create_p2pool_dirs(vendor_dir=vendor_dir, db4e=db4e)

        # Generate the P2Pool service files (installed by the sudo installer)
        self._generate_tmp_p2pool_service_files(vendor_dir=vendor_dir, db4e=db4e)

        # Copy in the P2Pool daemon and start script
        db4e = self._copy_p2pool_files(vendor_dir=vendor_dir, db4e=db4e)

        # Create the XMRig miner vendor directories
        db4e = self._create_xmrig_dirs(vendor_dir=vendor_dir, db4e=db4e)

        # Generate the XMRig service file (installed by the sudo installer)
        self._generate_tmp_xmrig_service_file(vendor_dir=vendor_dir, db4e=db4e)

        # Copy in the XMRig miner
        db4e = self._copy_xmrig_file(vendor_dir=vendor_dir, db4e=db4e)

        # Run the installer (with sudo)
        db4e = self._run_sudo_installer(
            vendor_dir=vendor_dir, db4e=db4e)

        # Return the updated Db4E deployment object with embded results
        return db4e
        

    def initial_setup_proceed(self, form_data: dict):
        db4e = self.ops_mgr.get_deployment(elem_type=DB4E_FIELD)
        return db4e
        

    def _check_wallet(self, user_wallet:str, db4e: Db4E):
        #print(f"InstallMgr:_check_wallet(): user_wallet: {user_wallet}")
        abort_install = False
        # User did not provide any wallet
        if not user_wallet:
            abort_install = True
            db4e.msg(USER_WALLET_LABEL, ERROR_FIELD, f"{USER_WALLET_LABEL} missing")
            return db4e, abort_install
        
        db4e.user_wallet(user_wallet)
        self.depl_mgr.update_one(db4e)
        db4e.msg(
            USER_WALLET_LABEL, GOOD_FIELD, f"Set the user wallet: {user_wallet[:7]}...")

        return db4e, abort_install


    def _check_vendor_dir(self, vendor_dir: str, db4e: Db4E):
        #print(f"InstallMgr:_vendor_dir(): {vendor_dir}")
        abort_install = False
        if not vendor_dir:
            abort_install = True
            db4e.msg(VENDOR_DIR_LABEL, ERROR_FIELD, f"{VENDOR_DIR_LABEL} missing")
        return db4e, abort_install
        
    # Copy Db4E files
    def _copy_db4e_files(self, vendor_dir):
        results = []
        db4e_src_dir = DB4E_FIELD
        db4e_dest_dir = DB4E_FIELD + '-' + str(DB4E_VERSION_DEFAULT)
        # Template directory
        tmpl_dir = self.depl_mgr.get_dir(TEMPLATE_FIELD)
        # Substitute placeholder in the db4e-service.sh script
        install_dir = self.depl_mgr.get_dir(INSTALL_DIR_FIELD)
        python = self.depl_mgr.get_dir(PYTHON_DEFAULT)
        placeholders = {
            PYTHON_PLACEHOLDER: python,
            INSTALL_DIR_PLACEHOLDER: install_dir}
        fq_src_script =  os.path.join(tmpl_dir, db4e_src_dir, BIN_DIR_DEFAULT, DB4E_START_SCRIPT_DEFAULT)
        fq_dest_script = os.path.join(vendor_dir, db4e_dest_dir, BIN_DIR_DEFAULT, DB4E_START_SCRIPT_DEFAULT)
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
    def _copy_monerod_files(self, vendor_dir, db4e: Db4E):
        monerod_dir = MONEROD_FIELD + '-' + str(MONEROD_VERSION_DEFAULT)
        # Template directory
        tmpl_dir = self.depl_mgr.get_dir(TEMPLATE_FIELD)

        # Copy in the Monero daemon and startup scripts
        fq_dst_bin_dir =  os.path.join(vendor_dir, monerod_dir, BIN_DIR_DEFAULT)
        fq_dst_monerod_dest_script = os.path.join(
            vendor_dir, monerod_dir, BIN_DIR_DEFAULT, MONEROD_START_SCRIPT_DEFAULT)
        fq_src_monerod = os.path.join(tmpl_dir, monerod_dir, BIN_DIR_DEFAULT, MONEROD_PROCESS_DEFAULT)

        shutil.copy(fq_src_monerod, fq_dst_bin_dir)
        db4e.msg(MONEROD_LABEL, GOOD_FIELD,
            f"Installed: {fq_dst_bin_dir}/{MONEROD_PROCESS_DEFAULT}")
        
        fq_src_monerod_start_script = os.path.join(
            tmpl_dir, monerod_dir, BIN_DIR_DEFAULT, MONEROD_START_SCRIPT_DEFAULT)
        shutil.copy(fq_src_monerod_start_script, fq_dst_monerod_dest_script)
        db4e.msg(MONEROD_LABEL, GOOD_FIELD,
            f"Installed: {fq_dst_monerod_dest_script}")

        # Make it executable
        current_permissions = os.stat(fq_dst_monerod_dest_script).st_mode
        new_permissions = current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        os.chmod(fq_dst_monerod_dest_script, new_permissions)
        return db4e

    def _copy_p2pool_files(self, vendor_dir:str , db4e: Db4E) -> Db4E:
        # Template directory
        tmpl_dir = self.depl_mgr.get_dir(TEMPLATE_FIELD)
        # P2Pool directory
        p2pool_version = P2POOL_VERSION_DEFAULT
        p2pool_dir = P2POOL_FIELD +'-' + str(p2pool_version)
        # Copy in the P2Pool daemon and startup script
        fq_src_p2pool = os.path.join(tmpl_dir, p2pool_dir, BIN_DIR_DEFAULT, P2POOL_PROCESS_DEFAULT)
        fq_dst_bin_dir = os.path.join(vendor_dir, p2pool_dir, BIN_DIR_DEFAULT)
        fq_src_p2pool_start_script  = os.path.join(tmpl_dir, p2pool_dir, BIN_DIR_DEFAULT, P2POOL_START_SCRIPT_DEFAULT)
        fq_dst_p2pool_start_script = os.path.join(vendor_dir, p2pool_dir, BIN_DIR_DEFAULT, P2POOL_START_SCRIPT_DEFAULT)
        shutil.copy(fq_src_p2pool, fq_dst_bin_dir)
        db4e.msg(P2POOL_LABEL, GOOD_FIELD,
            f"Installed: {fq_dst_bin_dir}/{P2POOL_PROCESS_DEFAULT}")
        shutil.copy(fq_src_p2pool_start_script, fq_dst_p2pool_start_script)
        # Make it executable
        current_permissions = os.stat(fq_dst_p2pool_start_script).st_mode
        new_permissions = current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        os.chmod(fq_dst_p2pool_start_script, new_permissions)
        db4e.msg(P2POOL_LABEL, GOOD_FIELD, f"Installed: {fq_dst_p2pool_start_script}")
        return db4e

    def _copy_xmrig_file(self, vendor_dir:str , db4e: Db4E) -> Db4E:
        xmrig_binary = XMRIG_PROCESS_DEFAULT
        # XMRig directory
        xmrig_version = XMRIG_VERSION_DEFAULT
        xmrig_dir = XMRIG_FIELD + '-' + str(xmrig_version)
        # Template directory
        tmpl_dir = self.depl_mgr.get_dir(TEMPLATE_FIELD)
        fq_dst_xmrig_bin_dir = os.path.join(vendor_dir, xmrig_dir, BIN_DIR_DEFAULT)
        fq_src_xmrig = os.path.join(tmpl_dir, xmrig_dir, BIN_DIR_DEFAULT, xmrig_binary)
        shutil.copy(fq_src_xmrig, fq_dst_xmrig_bin_dir)
        db4e.msg(XMRIG_LABEL, GOOD_FIELD, f"Installed: {fq_dst_xmrig_bin_dir}/{xmrig_binary}")
        return db4e

    def _create_db4e_dirs(self, vendor_dir: str, db4e: Db4E) -> Db4E:
        #print(f"InstallMgr:_create_db4e_dirs(): vendor_dir {vendor_dir}")
        db4e_with_version = DB4E_FIELD + '-' + str(DB4E_VERSION_DEFAULT)
        fq_db4e_dir = os.path.join(vendor_dir, db4e_with_version)
        # Create the base Db4E directory
        os.makedirs(os.path.join(fq_db4e_dir))
        db4e.msg(DB4E_LABEL, GOOD_FIELD, f"Created directory: {fq_db4e_dir}")
        # Create the sub-directories
        for sub_dir in [LOG_DIR_DEFAULT]:
            os.mkdir(os.path.join(fq_db4e_dir, sub_dir))
            db4e.msg(DB4E_LABEL, GOOD_FIELD, f"Created directory: {fq_db4e_dir}/{sub_dir}")
        # Create a symlink
        os.chdir(vendor_dir)
        os.symlink(
            os.path.join(db4e_with_version),
            os.path.join(DB4E_FIELD))
        # Create a health message, the directories will be logged later...
        db4e.msg(
            DB4E_LABEL, GOOD_FIELD,
            f"Created symlink to directory: {DB4E_FIELD} > {db4e_with_version}")
        return db4e

    def _create_monerod_dirs(self, vendor_dir, db4e):
        monerod_with_version = MONEROD_FIELD + '-' + str(MONEROD_VERSION_DEFAULT)
        fq_monerod_dir = os.path.join(vendor_dir, monerod_with_version)
        fq_blockchain_dir = os.path.join(fq_monerod_dir, BLOCKCHAIN_DIR_DEFAULT)

        # Create the base Monero directory
        os.mkdir(fq_monerod_dir)
        db4e.msg(MONEROD_LABEL, GOOD_FIELD, f"Created directory: {fq_monerod_dir}")

        os.mkdir(fq_blockchain_dir)
        db4e.msg(MONEROD_LABEL, GOOD_FIELD, 
                 f"Created Monero blockchain directory: {fq_monerod_dir}")

        # Create the sub-directories
        for sub_dir in [BIN_DIR_DEFAULT, CONF_DIR_DEFAULT, RUN_DIR_DEFAULT, LOG_DIR_DEFAULT]:
            fq_sub_dir = os.path.join(fq_monerod_dir, sub_dir)
            os.mkdir(fq_sub_dir)
            db4e.msg(MONEROD_LABEL, GOOD_FIELD, f"Created directory: {fq_sub_dir}")

        os.chdir(vendor_dir)
        os.symlink(
            os.path.join(monerod_with_version),
            os.path.join(MONEROD_FIELD))
        # Create a health message, the directories will be logged later...
        db4e.msg(
            MONEROD_LABEL, GOOD_FIELD,
            f"Created symlink to directory: {MONEROD_FIELD} > {monerod_with_version}")
        return db4e

    def _create_p2pool_dirs(self, vendor_dir: str, db4e: Db4E) -> Db4E:
        p2pool_with_version = P2POOL_FIELD + '-' + str(P2POOL_VERSION_DEFAULT)  
        fq_p2pool_dir = os.path.join(vendor_dir, p2pool_with_version)

        # Create the base P2Pool directory
        os.mkdir(os.path.join(fq_p2pool_dir))
        db4e.msg(P2POOL_LABEL, GOOD_FIELD, f"Created directory ({fq_p2pool_dir})")

        # Create the sub directories
        for sub_dir in [BIN_DIR_DEFAULT, CONF_DIR_DEFAULT, RUN_DIR_DEFAULT]:
            fq_sub_dir = os.path.join(fq_p2pool_dir, sub_dir)
            os.mkdir(fq_sub_dir)
            db4e.msg(P2POOL_LABEL, GOOD_FIELD, f"Created directory: {fq_sub_dir}")

        os.chdir(vendor_dir)
        os.symlink(
            os.path.join(p2pool_with_version),
            os.path.join(P2POOL_FIELD))
        db4e.msg(P2POOL_LABEL, GOOD_FIELD,
            f"Created symlink to directory: {P2POOL_FIELD} > {p2pool_with_version}")
        
        return db4e


    def _create_vendor_dir(self, vendor_dir: str, db4e: Db4E):
        #print(f"InstallMgr:_create_vendor_dir(): vendor_dir {vendor_dir}")
        abort_install = False
        if os.path.exists(vendor_dir):
            db4e.msg(VENDOR_DIR_LABEL, WARN_FIELD, 
                f'Found existing deployment directory: {vendor_dir}')
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_vendor_dir = vendor_dir + '.' + timestamp

            try:
                os.rename(vendor_dir, backup_vendor_dir)
                db4e.msg(VENDOR_DIR_LABEL, WARN_FIELD, 
                    f'Backed up old deployment directory: {backup_vendor_dir}')
                
            except (PermissionError, OSError, FileNotFoundError) as e:
                db4e.msg(
                    VENDOR_DIR_LABEL, WARN_FIELD, 
                    f"Failed to backup old deployment directory: {backup_vendor_dir}\n{e}")
                abort_install = True
                return db4e, abort_install # Abort the install

        try:
            os.makedirs(vendor_dir)
            db4e.msg(VENDOR_DIR_LABEL, GOOD_FIELD, f"Created directory: {vendor_dir}")
        except (PermissionError, FileNotFoundError, FileExistsError) as e:
            db4e.msg(
                VENDOR_DIR_LABEL, WARN_FIELD, 
                f'Failed to create directory: {vendor_dir}\n{e}')
            abort_install = True
            return db4e, abort_install

        return db4e, abort_install

    def _create_xmrig_dirs(self, vendor_dir: str, db4e: Db4E) -> Db4E:
        xmrig_with_version = XMRIG_FIELD + '-' + str(XMRIG_VERSION_DEFAULT)
        fq_xmrig_dir = os.path.join(vendor_dir, xmrig_with_version)
        os.mkdir(os.path.join(fq_xmrig_dir))
        db4e.msg(XMRIG_LABEL, GOOD_FIELD, f"Created directory: {fq_xmrig_dir}")
        for sub_dir in [BIN_DIR_DEFAULT, CONF_DIR_DEFAULT]:
            fq_sub_dir = os.path.join(fq_xmrig_dir, sub_dir)
            os.mkdir(fq_sub_dir)
            db4e.msg(XMRIG_LABEL, GOOD_FIELD, f"Created directory: {fq_sub_dir}")
        os.chdir(vendor_dir)
        os.symlink(xmrig_with_version, XMRIG_FIELD)
        db4e.msg(XMRIG_LABEL, GOOD_FIELD,
            f"Created symlink to directory: {XMRIG_FIELD} > {xmrig_with_version}")
        return db4e

    # Update the db4e service template with deployment values
    def _generate_db4e_service_file(self, db4e: Db4E):
        tmp_dir = self._get_tmp_dir()
        tmpl_dir = self.depl_mgr.get_dir(TEMPLATE_FIELD)
        db4e_dir = self.depl_mgr.get_dir(INSTALL_DIR_FIELD)
        fq_db4e_dir = os.path.join(db4e_dir)
        placeholders = {
            DB4E_USER_PLACEHOLDER: db4e.user(),
            DB4E_GROUP_PLACEHOLDER: db4e.group(),
            DB4E_DIR_PLACEHOLDER: fq_db4e_dir,
        }
        fq_db4e_service_file = os.path.join(
            tmpl_dir, DB4E_FIELD, SYSTEMD_DIR_DEFAULT, DB4E_SERVICE_FILE_DEFAULT)
        service_contents = self._replace_placeholders(fq_db4e_service_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, DB4E_SERVICE_FILE_DEFAULT)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

    def _generate_tmp_monerod_service_files(self, vendor_dir: str, db4e: Db4E):
        monerod_with_version = MONEROD_FIELD + '-' + str(MONEROD_VERSION_DEFAULT)
        # Template directory
        tmpl_dir = self.depl_mgr.get_dir(TEMPLATE_FIELD)
        # Temporary directory
        tmp_dir = self._get_tmp_dir()

        # Substitution placeholders in the service template files
        placeholders = {
            MONEROD_DIR_PLACEHOLDER: os.path.join(vendor_dir, MONEROD_FIELD),
            DB4E_USER_PLACEHOLDER: db4e.user(),
            DB4E_GROUP_PLACEHOLDER: db4e.group(),
        }

        # Generate a temporary monerod.systemd for the sudo script to install
        fq_monerod_service_file = os.path.join(
            tmpl_dir, monerod_with_version, SYSTEMD_DIR_DEFAULT, MONEROD_SERVICE_FILE_DEFAULT)
        service_contents = self._replace_placeholders(fq_monerod_service_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, MONEROD_SERVICE_FILE_DEFAULT)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

        # Generate a temporary monerod.socket for the sudo script to install
        fq_monerod_socket_file = os.path.join(tmpl_dir, monerod_with_version, SYSTEMD_DIR_DEFAULT, MONEROD_SOCKET_SERVICE_DEFAULT)
        service_contents = self._replace_placeholders(fq_monerod_socket_file, placeholders)
        tmp_socket_file = os.path.join(tmp_dir, MONEROD_SOCKET_SERVICE_DEFAULT)
        with open(tmp_socket_file, 'w') as f:
            f.write(service_contents)

    def _generate_tmp_p2pool_service_files(self, vendor_dir: str, db4e: Db4E):
        p2pool_with_version  = P2POOL_FIELD + '-' + str(P2POOL_VERSION_DEFAULT)
        # Template directory
        tmpl_dir = self.depl_mgr.get_dir(TEMPLATE_FIELD)
        # Temporary directory
        tmp_dir = self._get_tmp_dir()

        # P2Pool directory
        fq_p2pool_dir = os.path.join(vendor_dir, P2POOL_FIELD)

        # Substitution placeholders in the service template files        # 
        placeholders = {
            P2POOL_DIR_PLACEHOLDER: fq_p2pool_dir,
            DB4E_USER_PLACEHOLDER: db4e.user(),
            DB4E_GROUP_PLACEHOLDER: db4e.group(),
        }

        # Generate a temporary p2pool.service for the sudo script to install
        fq_p2pool_service_file  = os.path.join(
            tmpl_dir, p2pool_with_version, SYSTEMD_DIR_DEFAULT, P2POOL_SERVICE_FILE_DEFAULT)
        service_contents = self._replace_placeholders(fq_p2pool_service_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, P2POOL_SERVICE_FILE_DEFAULT)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

        # Generate a temporary p2pool.socket 
        fq_p2pool_socket_file   = os.path.join(
            tmpl_dir, p2pool_with_version, SYSTEMD_DIR_DEFAULT, P2POOL_SERVICE_SOCKET_FILE_DEFAULT)
        service_contents = self._replace_placeholders(fq_p2pool_socket_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, P2POOL_SERVICE_SOCKET_FILE_DEFAULT)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

    def _generate_tmp_xmrig_service_file(self, vendor_dir, db4e: Db4E) -> None:
        xmrig_with_version = XMRIG_FIELD + '-' + str(XMRIG_VERSION_DEFAULT)
        # Template directory
        tmpl_dir = self.depl_mgr.get_dir(TEMPLATE_FIELD)
        # Temporary directory
        tmp_dir = self._get_tmp_dir()
        # XMRig directory
        fq_xmrig_dir = os.path.join(vendor_dir, XMRIG_FIELD)
        placeholders = {
            XMRIG_DIR_PLACEHOLDER: fq_xmrig_dir,
            DB4E_USER_PLACEHOLDER: db4e.user(),
            DB4E_GROUP_PLACEHOLDER: db4e.group(),
        }
        fq_xmrig_service_file   = os.path.join(
            tmpl_dir, xmrig_with_version, SYSTEMD_DIR_DEFAULT, XMRIG_SERVICE_FILE_DEFAULT)
        service_contents = self._replace_placeholders(fq_xmrig_service_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, XMRIG_SERVICE_FILE_DEFAULT)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

    def _get_templates_dir(self):
        # Helper function
        templates_dir = TEMPLATES_DIR_DEFAULT
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

    def _run_sudo_installer(self, vendor_dir: str, db4e: Db4E) -> Db4E:
        #print(f"InstallMgr:_run_sudo_installer()")
        # Temporary directory
        tmp_dir = self._get_tmp_dir()
        db4e_install_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        # Additional config settings
        # Set the location of the temp dir in an environment variable
        env_setting = f"{TMP_DIR_ENVIRON_FIELD}={self.tmp_dir}"
        # Run the bin/db4e-installer.sh
        fq_initial_setup = os.path.join(db4e_install_dir, BIN_DIR_DEFAULT, DB4E_INITIAL_SETUP_SCRIPT_DEFAULT)
        try:
            cmd_result = subprocess.run(
                [ 
                    SUDO_CMD, "env", env_setting, fq_initial_setup, DB4E_FIELD, 
                    db4e.user(), db4e.group(), vendor_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                input=b"",
                timeout=10)
            stdout = cmd_result.stdout.decode().strip()
            stderr = cmd_result.stderr.decode().strip()

            # Check the return code
            if cmd_result.returncode != 0:
                db4e.msg(DB4E_LABEL, ERROR_FIELD, f'Service install failed.\n\n{stderr}')
                shutil.rmtree(tmp_dir)
                return db4e
            
            installer_output = f'{stdout}'
            for line in installer_output.split('\n'):
                db4e.msg(DB4E_LABEL, GOOD_FIELD, line)
            shutil.rmtree(tmp_dir)

        except Exception as e:
            db4e.msg(DB4E_LABEL, ERROR_FIELD, f'Fatal error: {e}')

        return db4e
    


