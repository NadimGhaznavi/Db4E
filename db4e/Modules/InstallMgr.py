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

from textual.containers import Container

from db4e.Modules.Db4E import Db4E
from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.DbCache import DbCache
from db4e.Modules.DeplMgr import DeplMgr
from db4e.Modules.HealthCache import HealthCache
from db4e.Modules.Helper import result_row
from db4e.Modules.InternalP2Pool import InternalP2Pool

from db4e.Constants.DDir import DDir
from db4e.Constants.DStatus import DStatus
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DDef import DDef
from db4e.Constants.DElem import DElem
from db4e.Constants.DPlaceholder import DPlaceholder
from db4e.Constants.DField import DField
from db4e.Constants.DFile import DFile


# The Mongo collection that houses the deployment records
DEPL_COL = DDef.DEPLOYMENT_COL
DB4E_OLD_GROUP_ENVIRON = DDef.DB4E_OLD_GROUP_ENVIRON
TMP_DIR = DDef.TMP_DIR
SUDO_CMD = DDef.SUDO_CMD

class InstallMgr(Container):
    
    def __init__(self, db: DbMgr, db_cache: DbCache):
        super().__init__()
        self.db_cache = db_cache
        self.depl_mgr = DeplMgr(db=db, db_cache=db_cache)
        self.col_name = DDef.DEPLOYMENT_COL
        self.tmp_dir = None

    def initial_setup(self, form_data: dict) -> dict:
        # Track the progress of the initial install
        abort_install = False

        # This is the data from the form on the InitialSetup pane
        db4e = form_data[DField.ELEMENT]
        
        db4e.pop_msgs()
        user_wallet = db4e.user_wallet()
        vendor_dir = db4e.vendor_dir()

        # Check that the user entered their wallet
        db4e, abort_install = self._check_wallet(user_wallet=user_wallet, db4e=db4e)
        if abort_install:
            db4e.msg(DLabel.DB4E, DStatus.ERROR, f"Fatal error, aborting install")
            return db4e
        
        # Check that the user entered a vendor directory
        db4e, abort_install = self._check_vendor_dir(vendor_dir=vendor_dir, db4e=db4e)
        if abort_install:
            db4e.msg(DLabel.DB4E, DStatus.ERROR, f"Fatal error, aborting install")
            return db4e

        # Create the vendor directory on the filesystem
        db4e, abort_install = self._create_vendor_dir(vendor_dir=vendor_dir, db4e=db4e)
        if abort_install:
            db4e.msg(DLabel.DB4E, DStatus.ERROR, f"Fatal error, aborting install")
            db4e.vendor_dir("") # Reset the vendor dir to null
            self.db_cache.update_one(db4e)
            return db4e
        

        # We have everything we need to finish the install. Update the record.
        self.db_cache.update_one(db4e)

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

        # Deploy internal P2Pool instances to gather metrics
        db4e = self._deploy_internal_p2pools(vendor_dir=vendor_dir, db4e=db4e)

        # Run the installer (with sudo)
        db4e = self._run_sudo_installer(
            vendor_dir=vendor_dir, db4e=db4e)

        # Return the updated Db4E deployment object with embded results
        return db4e
        

    def initial_setup_proceed(self, form_data: dict):
        db4e = self.depl_mgr.get_deployment(elem_type=DElem.DB4E)
        return db4e
        

    def _check_wallet(self, user_wallet:str, db4e: Db4E):
        #print(f"InstallMgr:_check_wallet(): user_wallet: {user_wallet}")
        abort_install = False
        # User did not provide any wallet
        if not user_wallet:
            abort_install = True
            db4e.msg(DLabel.USER_WALLET, DStatus.ERROR, f"{DLabel.USER_WALLET} missing")
            return db4e, abort_install
        
        db4e.user_wallet(user_wallet)
        self.db_cache.update_one(db4e)
        db4e.msg(
            DLabel.USER_WALLET, DStatus.GOOD, f"Set the user wallet: {user_wallet[:7]}...")

        return db4e, abort_install


    def _check_vendor_dir(self, vendor_dir: str, db4e: Db4E):
        #print(f"InstallMgr:_vendor_dir(): {vendor_dir}")
        abort_install = False
        if not vendor_dir:
            abort_install = True
            db4e.msg(DLabel.VENDOR_DIR, DStatus.ERROR, f"{DLabel.VENDOR_DIR} missing")
        return db4e, abort_install
        
    # Copy Db4E files
    def _copy_db4e_files(self, vendor_dir):
        results = []
        db4e_src_dir = DElem.DB4E
        db4e_dest_dir = DElem.DB4E + '-' + str(DDef.DB4E_VERSION)
        # Template directory
        tmpl_dir = self.depl_mgr.get_dir(DDir.TEMPLATE)
        # Substitute placeholder in the db4e-service.sh script
        install_dir = self.depl_mgr.get_dir(DDir.INSTALL)
        python = self.depl_mgr.get_dir(DDef.PYTHON)
        placeholders = {
            DPlaceholder.PYTHON: python,
            DPlaceholder.INSTALL_DIR: install_dir}
        fq_src_script =  os.path.join(
            tmpl_dir, db4e_src_dir, DDef.BIN_DIR, DDef.DB4E_START_SCRIPT)
        fq_dest_script = os.path.join(
            vendor_dir, db4e_dest_dir, DDef.BIN_DIR, DDef.DB4E_START_SCRIPT)
        script_contents = self._replace_placeholders(fq_src_script, placeholders)
        with open(fq_dest_script, 'w') as f:
            f.write(script_contents)        
        # Make it executable
        current_permissions = os.stat(fq_dest_script).st_mode
        new_permissions = current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        os.chmod(fq_dest_script, new_permissions)
        results.append(result_row(
            DLabel.DB4E, DStatus.GOOD,
            f"Installed: {fq_dest_script}"))
        return results
        
    # Copy monerod files
    def _copy_monerod_files(self, vendor_dir, db4e: Db4E):
        monerod_dir = DElem.MONEROD + '-' + str(DDef.MONEROD_VERSION)
        # Template directory
        tmpl_dir = self.depl_mgr.get_dir(DDir.TEMPLATE)

        # Copy in the Monero daemon and startup scripts
        fq_dst_bin_dir =  os.path.join(vendor_dir, monerod_dir, DDef.BIN_DIR)
        fq_dst_monerod_dest_script = os.path.join(
            vendor_dir, monerod_dir, DDef.BIN_DIR, DDef.MONEROD_START_SCRIPT)
        fq_src_monerod = os.path.join(
            tmpl_dir, monerod_dir, DDef.BIN_DIR, DDef.MONEROD_PROCESS)

        shutil.copy(fq_src_monerod, fq_dst_bin_dir)
        db4e.msg(DLabel.MONEROD, DStatus.GOOD,
            f"Installed: {fq_dst_bin_dir}/{DDef.MONEROD_PROCESS}")
        
        fq_src_monerod_start_script = os.path.join(
            tmpl_dir, monerod_dir, DDef.BIN_DIR, DDef.MONEROD_START_SCRIPT)
        shutil.copy(fq_src_monerod_start_script, fq_dst_monerod_dest_script)
        db4e.msg(DLabel.MONEROD, DStatus.GOOD,
            f"Installed: {fq_dst_monerod_dest_script}")

        # Make it executable
        current_permissions = os.stat(fq_dst_monerod_dest_script).st_mode
        new_permissions = current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        os.chmod(fq_dst_monerod_dest_script, new_permissions)
        return db4e

    def _copy_p2pool_files(self, vendor_dir:str , db4e: Db4E) -> Db4E:
        # Template directory
        tmpl_dir = self.depl_mgr.get_dir(DDir.TEMPLATE)
        # P2Pool directory
        p2pool_version = DDef.P2POOL_VERSION
        p2pool_dir = DElem.P2POOL +'-' + str(p2pool_version)
        # Copy in the P2Pool daemon and startup script
        fq_src_p2pool = os.path.join(
            tmpl_dir, p2pool_dir, DDef.BIN_DIR, DDef.P2POOL_PROCESS)
        fq_dst_bin_dir = os.path.join(vendor_dir, p2pool_dir, DDef.BIN_DIR)
        fq_src_p2pool_start_script  = os.path.join(
            tmpl_dir, p2pool_dir, DDef.BIN_DIR, DDef.P2POOL_START_SCRIPT)
        fq_dst_p2pool_start_script = os.path.join(
            vendor_dir, p2pool_dir, DDef.BIN_DIR, DDef.P2POOL_START_SCRIPT)
        shutil.copy(fq_src_p2pool, fq_dst_bin_dir)
        db4e.msg(DLabel.P2POOL, DStatus.GOOD,
            f"Installed: {fq_dst_bin_dir}/{DDef.P2POOL_PROCESS}")
        shutil.copy(fq_src_p2pool_start_script, fq_dst_p2pool_start_script)
        # Make it executable
        current_permissions = os.stat(fq_dst_p2pool_start_script).st_mode
        new_permissions = current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        os.chmod(fq_dst_p2pool_start_script, new_permissions)
        db4e.msg(DLabel.P2POOL, DStatus.GOOD, f"Installed: {fq_dst_p2pool_start_script}")
        return db4e

    def _copy_xmrig_file(self, vendor_dir:str , db4e: Db4E) -> Db4E:
        xmrig_binary = DDef.XMRIG_PROCESS
        # XMRig directory
        xmrig_version = DDef.XMRIG_VERSION
        xmrig_dir = DElem.XMRIG + '-' + str(xmrig_version)
        # Template directory
        tmpl_dir = self.depl_mgr.get_dir(DDir.TEMPLATE)
        fq_dst_xmrig_bin_dir = os.path.join(vendor_dir, xmrig_dir, DDef.BIN_DIR)
        fq_src_xmrig = os.path.join(tmpl_dir, xmrig_dir, DDef.BIN_DIR, xmrig_binary)
        shutil.copy(fq_src_xmrig, fq_dst_xmrig_bin_dir)
        db4e.msg(DLabel.XMRIG, DStatus.GOOD, f"Installed: {fq_dst_xmrig_bin_dir}/{xmrig_binary}")
        return db4e

    def _create_db4e_dirs(self, vendor_dir: str, db4e: Db4E) -> Db4E:
        #print(f"InstallMgr:_create_db4e_dirs(): vendor_dir {vendor_dir}")
        db4e_with_version = DElem.DB4E + '-' + str(DDef.DB4E_VERSION)
        fq_db4e_dir = os.path.join(vendor_dir, db4e_with_version)
        # Create the base Db4E directory
        os.makedirs(os.path.join(fq_db4e_dir))
        db4e.msg(DLabel.DB4E, DStatus.GOOD, f"Created directory: {fq_db4e_dir}")
        # Create the sub-directories
        for sub_dir in [DDef.LOG_DIR]:
            os.mkdir(os.path.join(fq_db4e_dir, sub_dir))
            db4e.msg(DLabel.DB4E, DStatus.GOOD, f"Created directory: {fq_db4e_dir}/{sub_dir}")
        # Create a symlink
        os.chdir(vendor_dir)
        os.symlink(
            os.path.join(db4e_with_version),
            os.path.join(DElem.DB4E))
        # Create a health message, the directories will be logged later...
        db4e.msg(
            DLabel.DB4E, DStatus.GOOD,
            f"Created symlink to directory: {DElem.DB4E} > {db4e_with_version}")
        return db4e

    def _create_monerod_dirs(self, vendor_dir, db4e):
        monerod_with_version = DElem.MONEROD + '-' + str(DDef.MONEROD_VERSION)
        fq_monerod_dir = os.path.join(vendor_dir, monerod_with_version)

        # Create the base Monero directory
        os.mkdir(fq_monerod_dir)
        db4e.msg(DLabel.MONEROD, DStatus.GOOD, f"Created directory: {fq_monerod_dir}")

        # Create the sub-directories
        for sub_dir in [DDef.BIN_DIR, DDef.CONF_DIR]:
            fq_sub_dir = os.path.join(fq_monerod_dir, sub_dir)
            os.mkdir(fq_sub_dir)
            db4e.msg(DLabel.MONEROD, DStatus.GOOD, f"Created directory: {fq_sub_dir}")

        os.chdir(vendor_dir)
        os.symlink(
            os.path.join(monerod_with_version),
            os.path.join(DElem.MONEROD))
        # Create a health message, the directories will be logged later...
        db4e.msg(
            DLabel.MONEROD, DStatus.GOOD,
            f"Created symlink to directory: {DElem.MONEROD} > {monerod_with_version}")
        return db4e

    def _create_p2pool_dirs(self, vendor_dir: str, db4e: Db4E) -> Db4E:
        p2pool_with_version = DElem.P2POOL + '-' + str(DDef.P2POOL_VERSION)  
        fq_p2pool_dir = os.path.join(vendor_dir, p2pool_with_version)

        # Create the base P2Pool directory
        os.mkdir(os.path.join(fq_p2pool_dir))
        db4e.msg(DLabel.P2POOL, DStatus.GOOD, f"Created directory ({fq_p2pool_dir})")

        # Create the sub directories
        for sub_dir in [DDef.BIN_DIR, DDef.CONF_DIR]:
            fq_sub_dir = os.path.join(fq_p2pool_dir, sub_dir)
            os.mkdir(fq_sub_dir)
            db4e.msg(DLabel.P2POOL, DStatus.GOOD, f"Created directory: {fq_sub_dir}")

        os.chdir(vendor_dir)
        os.symlink(
            os.path.join(p2pool_with_version),
            os.path.join(DElem.P2POOL))
        db4e.msg(DLabel.P2POOL, DStatus.GOOD,
            f"Created symlink to directory: {DElem.P2POOL} > {p2pool_with_version}")
        
        return db4e


    def _create_vendor_dir(self, vendor_dir: str, db4e: Db4E):
        #print(f"InstallMgr:_create_vendor_dir(): vendor_dir {vendor_dir}")
        abort_install = False
        if os.path.exists(vendor_dir):
            db4e.msg(DLabel.VENDOR_DIR, DStatus.WARN, 
                f'Found existing deployment directory: {vendor_dir}')
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_vendor_dir = vendor_dir + '.' + timestamp

            try:
                os.rename(vendor_dir, backup_vendor_dir)
                db4e.msg(DLabel.VENDOR_DIR, DStatus.WARN, 
                    f'Backed up old deployment directory: {backup_vendor_dir}')
                
            except (PermissionError, OSError, FileNotFoundError) as e:
                db4e.msg(
                    DLabel.VENDOR_DIR, DStatus.WARN, 
                    f"Failed to backup old deployment directory: {backup_vendor_dir}\n{e}")
                abort_install = True
                return db4e, abort_install # Abort the install

        try:
            os.makedirs(vendor_dir)
            db4e.msg(DLabel.VENDOR_DIR, DStatus.GOOD, f"Created directory: {vendor_dir}")
        except (PermissionError, FileNotFoundError, FileExistsError) as e:
            db4e.msg(
                DLabel.VENDOR_DIR, DStatus.WARN, 
                f'Failed to create directory: {vendor_dir}\n{e}')
            abort_install = True
            return db4e, abort_install

        return db4e, abort_install

    def _create_xmrig_dirs(self, vendor_dir: str, db4e: Db4E) -> Db4E:
        xmrig_with_version = DElem.XMRIG + '-' + str(DDef.XMRIG_VERSION)
        fq_xmrig_dir = os.path.join(vendor_dir, xmrig_with_version)
        os.mkdir(os.path.join(fq_xmrig_dir))
        db4e.msg(DLabel.XMRIG, DStatus.GOOD, f"Created directory: {fq_xmrig_dir}")
        for sub_dir in [DDef.BIN_DIR, DDef.CONF_DIR, DDef.LOG_DIR]:
            fq_sub_dir = os.path.join(fq_xmrig_dir, sub_dir)
            os.mkdir(fq_sub_dir)
            db4e.msg(DLabel.XMRIG, DStatus.GOOD, f"Created directory: {fq_sub_dir}")
        os.chdir(vendor_dir)
        os.symlink(xmrig_with_version, DElem.XMRIG)
        db4e.msg(DLabel.XMRIG, DStatus.GOOD,
            f"Created symlink to directory: {DElem.XMRIG} > {xmrig_with_version}")
        return db4e


    # Deploy metrics gathering P2Pool instances
    def _deploy_internal_p2pools(self, vendor_dir: str, db4e: Db4E):
        for chain_label in [DLabel.MAIN_CHAIN, DLabel.MINI_CHAIN, DLabel.NANO_CHAIN]:
            p2pool = InternalP2Pool()
            log_file = os.path.join(
                vendor_dir, DElem.P2POOL, chain_label, DDef.LOG_DIR, DFile.P2POOL_LOG)
            stats_mod = os.path.join(
                vendor_dir, DElem.P2POOL, chain_label, DDef.API_DIR, DFile.STATS_MOD)
            stdin_path = os.path.join(
                vendor_dir, DElem.P2POOL, chain_label, DDef.RUN_DIR, DFile.P2POOL_STDIN)
            p2pool.set_type(
                chain_label=chain_label, log_file=log_file, stats_mod=stats_mod,
                stdin_path=stdin_path)
            self.depl_mgr.add_deployment(p2pool)
            db4e.msg(
                chain_label, DStatus.GOOD,
                f"Created internal P2Pool deployment: {chain_label}")
        return db4e


    # Update the db4e service template with deployment values
    def _generate_db4e_service_file(self, db4e: Db4E):
        tmp_dir = self._get_tmp_dir()
        tmpl_dir = self.depl_mgr.get_dir(DDir.TEMPLATE)
        db4e_dir = self.depl_mgr.get_dir(DDir.INSTALL)
        fq_db4e_dir = os.path.join(db4e_dir)
        placeholders = {
            DPlaceholder.DB4E_USER: db4e.user(),
            DPlaceholder.DB4E_GROUP: db4e.group(),
            DPlaceholder.DB4E_DIR: fq_db4e_dir,
        }
        fq_db4e_service_file = os.path.join(
            tmpl_dir, DElem.DB4E, DDef.SYSTEMD_DIR, DDef.DB4E_SERVICE_FILE)
        service_contents = self._replace_placeholders(fq_db4e_service_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, DDef.DB4E_SERVICE_FILE)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

    def _generate_tmp_monerod_service_files(self, vendor_dir: str, db4e: Db4E):
        monerod_with_version = DElem.MONEROD + '-' + str(DDef.MONEROD_VERSION)
        # Template directory
        tmpl_dir = self.depl_mgr.get_dir(DDir.TEMPLATE)
        # Temporary directory
        tmp_dir = self._get_tmp_dir()

        # Substitution placeholders in the service template files
        placeholders = {
            DPlaceholder.MONEROD_DIR: os.path.join(vendor_dir, DElem.MONEROD),
            DPlaceholder.DB4E_USER: db4e.user(),
            DPlaceholder.DB4E_GROUP: db4e.group(),
        }

        # Generate a temporary monerod.systemd for the sudo script to install
        fq_monerod_service_file = os.path.join(
            tmpl_dir, monerod_with_version, DDef.SYSTEMD_DIR, DDef.MONEROD_SERVICE_FILE)
        service_contents = self._replace_placeholders(fq_monerod_service_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, DDef.MONEROD_SERVICE_FILE)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

        # Generate a temporary monerod.socket for the sudo script to install
        fq_monerod_socket_file = os.path.join(
            tmpl_dir, monerod_with_version, DDef.SYSTEMD_DIR, DDef.MONEROD_SOCKET_SERVICE)
        service_contents = self._replace_placeholders(fq_monerod_socket_file, placeholders)
        tmp_socket_file = os.path.join(tmp_dir, DDef.MONEROD_SOCKET_SERVICE)
        with open(tmp_socket_file, 'w') as f:
            f.write(service_contents)


    def _generate_tmp_p2pool_service_files(self, vendor_dir: str, db4e: Db4E):
        p2pool_with_version  = DElem.P2POOL + '-' + str(DDef.P2POOL_VERSION)
        # Template directory
        tmpl_dir = self.depl_mgr.get_dir(DDir.TEMPLATE)
        # Temporary directory
        tmp_dir = self._get_tmp_dir()

        # P2Pool directory
        fq_p2pool_dir = os.path.join(vendor_dir, DElem.P2POOL)

        # Substitution placeholders in the service template files        # 
        placeholders = {
            DPlaceholder.P2POOL_DIR: fq_p2pool_dir,
            DPlaceholder.DB4E_USER: db4e.user(),
            DPlaceholder.DB4E_GROUP: db4e.group(),
        }

        # Generate a temporary p2pool.service for the sudo script to install
        fq_p2pool_service_file  = os.path.join(
            tmpl_dir, p2pool_with_version, DDef.SYSTEMD_DIR, DDef.P2POOL_SERVICE_FILE)
        service_contents = self._replace_placeholders(fq_p2pool_service_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, DDef.P2POOL_SERVICE_FILE)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

        # Generate a temporary p2pool.socket 
        fq_p2pool_socket_file   = os.path.join(
            tmpl_dir, p2pool_with_version, DDef.SYSTEMD_DIR, DDef.P2POOL_SERVICE_SOCKET_FILE)
        service_contents = self._replace_placeholders(fq_p2pool_socket_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, DDef.P2POOL_SERVICE_SOCKET_FILE)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

    def _generate_tmp_xmrig_service_file(self, vendor_dir, db4e: Db4E) -> None:
        xmrig_with_version = DElem.XMRIG + '-' + str(DDef.XMRIG_VERSION)
        # Template directory
        tmpl_dir = self.depl_mgr.get_dir(DDir.TEMPLATE)
        # Temporary directory
        tmp_dir = self._get_tmp_dir()
        # XMRig directory
        fq_xmrig_dir = os.path.join(vendor_dir, DElem.XMRIG)
        placeholders = {
            DPlaceholder.XMRIG_DIR: fq_xmrig_dir,
            DPlaceholder.DB4E_USER: db4e.user(),
            DPlaceholder.DB4E_GROUP: db4e.group(),
        }
        fq_xmrig_service_file   = os.path.join(
            tmpl_dir, xmrig_with_version, DDef.SYSTEMD_DIR, DDef.XMRIG_SERVICE_FILE)
        service_contents = self._replace_placeholders(fq_xmrig_service_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, DDef.XMRIG_SERVICE_FILE)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

    def _get_templates_dir(self):
        # Helper function
        templates_dir = DDef.TEMPLATES_DIR
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
        # Temporary directory
        tmp_dir = self._get_tmp_dir()
        db4e_install_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        # Run the bin/db4e-installer.sh
        fq_initial_setup = os.path.join(
            db4e_install_dir, DDef.BIN_DIR, DDef.DB4E_INITIAL_SETUP_SCRIPT)
        try:
            cmd_result = subprocess.run(
                [ 
                    SUDO_CMD, fq_initial_setup, db4e_install_dir, 
                    db4e.user(), db4e.group(), vendor_dir, tmp_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                input=b"",
                timeout=10)
            stdout = cmd_result.stdout.decode().strip()
            stderr = cmd_result.stderr.decode().strip()

            # Check the return code
            if cmd_result.returncode != 0:
                db4e.msg(DLabel.DB4E, DStatus.ERROR, f'Service install failed.\n\n{stderr}')
                shutil.rmtree(tmp_dir)
                return db4e
            
            installer_output = f'{stdout}'
            for line in installer_output.split('\n'):
                db4e.msg(DLabel.DB4E, DStatus.GOOD, line)
            shutil.rmtree(tmp_dir)

        except Exception as e:
            db4e.msg(DLabel.DB4E, DStatus.ERROR, f'Fatal error: {e}')

        return db4e
    


