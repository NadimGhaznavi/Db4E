"""
db4e/Modules/InstallMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

import os, shutil
from datetime import datetime, timezone
import tempfile
import subprocess

from textual.containers import Container

from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Modules.ConfigMgr import Config
from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.Helper import result_row, get_effective_identity
from db4e.Constants.Fields import (
    BIN_DIR_FIELD, BLOCKCHAIN_DIR_FIELD, COMPONENT_FIELD, CONF_DIR_FIELD, 
    DB4E_FIELD, DB4E_DIR_FIELD, ENABLE_FIELD, ERROR_FIELD, GOOD_FIELD, 
    GROUP_FIELD, INSTALL_DIR_FIELD, LOG_DIR_FIELD, MONEROD_FIELD, P2POOL_FIELD, 
    PROCESS_FIELD, RUN_DIR_FIELD, SETUP_SCRIPT_FIELD, SERVICE_FILE_FIELD, 
    SOCKET_FILE_FIELD, START_SCRIPT_FIELD, SYSTEMD_DIR_FIELD, 
    TEMPLATE_DIR_FIELD, TMP_DIR_ENVIRON_FIELD, USER_FIELD, USER_WALLET_FIELD, 
    VENDOR_DIR_FIELD, VERSION_FIELD, WARN_FIELD, XMRIG_FIELD
)
from db4e.Constants.SystemdTemplates import (
    DB4E_USER_PLACEHOLDER, DB4E_GROUP_PLACEHOLDER, DB4E_DIR_PLACEHOLDER,
    MONEROD_DIR_PLACEHOLDER, P2POOL_DIR_PLACEHOLDER, XMRIG_DIR_PLACEHOLDER,
)
from db4e.Constants.Labels import (
    DB4E_GROUP_LABEL, DB4E_LABEL, DB4E_USER_LABEL, DEPLOYMENT_DIR_LABEL, 
    INSTALL_DIR_LABEL, MONEROD_LABEL, MONERO_WALLET_LABEL, P2POOL_LABEL, 
    STARTUP_SCRIPT, XMRIG_LABEL
)
from db4e.Constants.Defaults import (
    DB4E_OLD_GROUP_ENVIRON_DEFAULT, DEPLOYMENT_COL_DEFAULT, SUDO_CMD_DEFAULT, 
    TMP_DIR_DEFAULT
)
# The Mongo collection that houses the deployment records
DEPL_COL = DEPLOYMENT_COL_DEFAULT
DB4E_OLD_GROUP_ENVIRON = DB4E_OLD_GROUP_ENVIRON_DEFAULT
TMP_DIR = TMP_DIR_DEFAULT
SUDO_CMD = SUDO_CMD_DEFAULT

class InstallMgr(Container):
    
    def __init__(self, config: Config):
        super().__init__()
        self.ini = config
        self.depl_mgr = DeploymentMgr(config)
        self.db = DbMgr(config)
        self.col_name = DEPLOYMENT_COL_DEFAULT
        self.tmp_dir = None

    def initial_setup(self, form_data: dict) -> dict:
        # Track the progress of the initial install
        abort_install = False

        # This is the data from the form on the InitialSetup pane
        user_wallet = form_data[USER_WALLET_FIELD]
        vendor_dir = form_data[VENDOR_DIR_FIELD]

        # Check if there's an existing 'db4e' record
        results, db4e_rec = self._check_or_create_db4e_rec()

        # Intitialize the db4e_rec
        results, db4e_rec = self._init_db4e_rec(db4e_rec=db4e_rec, results=results)

        # Confirm that the user actually filled out the form.
        results, db4e_rec, abort_install = self._check_form_data(
            user_wallet=user_wallet, vendor_dir=vendor_dir, db4e_rec=db4e_rec, 
            results=results)
        if abort_install:
            return results
        
        # Create the vendor directory
        results, abort_install = self._create_vendor_dir(
            vendor_dir=vendor_dir, results=results
        )
        if abort_install:
            return results

        # The 'db4e' record has been created, the user wallet and vendor dir
        # have been set
        self.db.update_one(
            col_name=self.col_name, filter={COMPONENT_FIELD: DB4E_FIELD}, 
            new_values=db4e_rec)
        self.post_message(RefreshNavPane(self))

        # Setup Db4E
        self._generate_db4e_service_file(vendor_dir=vendor_dir)

        # Create the Monero daemon vendor directories
        self._create_monerod_dirs(vendor_dir=vendor_dir)

        # Generate the Monero service files (installed by the sudo installer)
        self._generate_monerod_service_files(vendor_dir=vendor_dir)

        # Copy in the Monero daemon and start script
        results = self._copy_monerod_files(vendor_dir=vendor_dir, results=results)

        # Create the P2Pool daemon vendor directories
        self._create_p2pool_dirs(vendor_dir=vendor_dir)

        # Generate the P2Pool service files (installed by the sudo installer)
        self._generate_p2pool_service_files(vendor_dir=vendor_dir)

        # Copy in the P2Pool daemon and start script
        results = self._copy_p2pool_files(vendor_dir=vendor_dir, results=results)

        # Create the XMRig miner vendor directories
        self._create_xmrig_dirs(vendor_dir=vendor_dir)

        # Generate the XMRig service file (installed by the sudo installer)
        self._generate_xmrig_service_file(vendor_dir=vendor_dir)

        # Copy in the XMRig miner
        results = self._copy_xmrig_file(vendor_dir=vendor_dir, results=results)

        # Run the installer (with sudo)
        results = self._run_sudo_installer(
            vendor_dir=vendor_dir, results=results, db4e_rec=db4e_rec)

        # Return the results
        return results

    def _check_form_data(
            self, user_wallet: str, 
            vendor_dir: str, 
            db4e_rec: dict,
            results: list,
            abort_install = False):

        if not user_wallet:
            results.append(result_row(
                MONERO_WALLET_LABEL, ERROR_FIELD, 
                f"Missing {MONERO_WALLET_LABEL}"))
            abort_install = True
        else:
            db4e_rec[USER_WALLET_FIELD] = user_wallet
            user_wallet_short = user_wallet[0:6] + '...'
            results.append(result_row(
                MONERO_WALLET_LABEL, GOOD_FIELD, 
                f"Added wallet ({user_wallet_short}) to the {DB4E_LABEL} " + 
                "deployment record"))

        if not vendor_dir:
            results.append(result_row(
                DEPLOYMENT_DIR_LABEL, ERROR_FIELD, 
                f"Missing {DEPLOYMENT_DIR_LABEL}"))
            abort_install = True
        else:
            db4e_rec[VENDOR_DIR_FIELD] = vendor_dir
            results.append(result_row(
                DEPLOYMENT_DIR_LABEL, GOOD_FIELD, 
                f"Added deployment directory ({vendor_dir}) to the {DB4E_LABEL} " +
                "deployment record"))

        if abort_install:
            results.append(result_row (
                DB4E_LABEL, GOOD_FIELD, 
                f"Click on Db4e Core to try again"))
            return (results, db4e_rec, abort_install)
        self.depl_mgr.update_deployment(db4e_rec)
        return (results, db4e_rec, abort_install)


    def _check_or_create_db4e_rec(self):
        results = []
        db4e_rec = self.depl_mgr.get_deployment(DB4E_FIELD)
        if db4e_rec:
            results.append(result_row(
                DB4E_LABEL, WARN_FIELD,
                f"Found existing {DB4E_LABEL} deployment record"
            ))
        else: # No record, so get a new one
            db4e_rec = self.depl_mgr.get_new_rec({COMPONENT_FIELD: DB4E_FIELD})
            self.db.insert_one(self.col_name, db4e_rec)
            results.append(result_row(
                DB4E_LABEL, GOOD_FIELD,
                f"Created {DB4E_LABEL} deployment record"
            ))
        return (results, db4e_rec)

    def _create_vendor_dir(self, vendor_dir: str, results: list):
        abort_install = False

        if os.path.exists(vendor_dir):
            results.append(result_row(
                DEPLOYMENT_DIR_LABEL, WARN_FIELD, 
                f'Found existing deployment directory ({vendor_dir})'))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            backup_vendor_dir = vendor_dir + '.' + timestamp
            try:
                os.rename(vendor_dir, backup_vendor_dir)
                results.append(result_row(
                    DEPLOYMENT_DIR_LABEL, WARN_FIELD, 
                    f'Backed up old deployment directory ({backup_vendor_dir})'))
            except (PermissionError, OSError, FileNotFoundError) as e:
                results.append(result_row(
                    DEPLOYMENT_DIR_LABEL, ERROR_FIELD, 
                    'Failed to backup old deployment directory ' +
                    f'({backup_vendor_dir})\n{e}'))
                abort_install = True
                return (results, abort_install) # Abort the install

        try:
            os.makedirs(vendor_dir)
            results.append(result_row(
                DEPLOYMENT_DIR_LABEL, GOOD_FIELD, 
                f"Created {DEPLOYMENT_DIR_LABEL} ({vendor_dir})"))        
        except (PermissionError, FileNotFoundError, FileExistsError) as e:
            results.append(result_row(
                DEPLOYMENT_DIR_LABEL, ERROR_FIELD, 
                f'Failed to create directory ({vendor_dir}\n{e}'))
            abort_install = True
        return (results, abort_install)

    # Copy monerod files
    def _copy_monerod_files(self, vendor_dir, results):
        bin_dir              = self.ini.config[DB4E_FIELD][BIN_DIR_FIELD]
        monerod_binary       = self.ini.config[MONEROD_FIELD][PROCESS_FIELD]
        monerod_start_script = self.ini.config[MONEROD_FIELD][START_SCRIPT_FIELD]
        monerod_version      = self.ini.config[MONEROD_FIELD][VERSION_FIELD]
        monerod_dir = MONEROD_FIELD + '-' + str(monerod_version)
        # Template directory
        tmpl_dir = self._get_templates_dir()
        # Copy in the Monero daemon and startup scripts
        fq_dst_monerod_bin_dir = os.path.join(vendor_dir, monerod_dir, bin_dir)
        fq_src_monerod = os.path.join(tmpl_dir, monerod_dir, bin_dir, monerod_binary)
        fq_src_monerod_start_script = os.path.join(
            tmpl_dir, monerod_dir, bin_dir, monerod_start_script)
        shutil.copy(fq_src_monerod, fq_dst_monerod_bin_dir)
        results.append(result_row(
            MONEROD_LABEL, GOOD_FIELD,
            f"Installed {MONEROD_LABEL} into {fq_dst_monerod_bin_dir}"
        ))
        shutil.copy(fq_src_monerod_start_script, fq_dst_monerod_bin_dir)
        results.append(result_row(
            MONEROD_LABEL, GOOD_FIELD,
            f"Installed {MONEROD_LABEL} {STARTUP_SCRIPT} into {fq_dst_monerod_bin_dir}"
        ))
        return results

    def _copy_p2pool_files(self, vendor_dir, results):
        bin_dir = self.ini.config[DB4E_FIELD][BIN_DIR_FIELD]
        p2pool_binary = self.ini.config[P2POOL_FIELD][PROCESS_FIELD]
        p2pool_start_script  = self.ini.config[P2POOL_FIELD][START_SCRIPT_FIELD]
        # Template directory
        tmpl_dir = self._get_templates_dir()
        # P2Pool directory
        p2pool_version = self.ini.config[P2POOL_FIELD][VERSION_FIELD]
        p2pool_dir = P2POOL_FIELD +'-' + str(p2pool_version)
        # Copy in the P2Pool daemon and startup script
        fq_src_p2pool = os.path.join(tmpl_dir, p2pool_dir, bin_dir, p2pool_binary)
        fq_src_p2pool_start_script  = os.path.join(tmpl_dir, p2pool_dir, bin_dir, p2pool_start_script)
        fq_dst_p2pool_bin_dir = os.path.join(vendor_dir, p2pool_dir, bin_dir)
        shutil.copy(fq_src_p2pool, fq_dst_p2pool_bin_dir)
        results.append(result_row(
            P2POOL_LABEL, GOOD_FIELD,
            f"Installed {P2POOL_LABEL} into {fq_dst_p2pool_bin_dir}"
        ))
        shutil.copy(fq_src_p2pool_start_script, fq_dst_p2pool_bin_dir)
        results.append(result_row(
            P2POOL_LABEL, GOOD_FIELD,
            f"Installed {P2POOL_LABEL} {STARTUP_SCRIPT} into {fq_dst_p2pool_bin_dir}"
        ))
        return results

    def _copy_xmrig_file(self, vendor_dir, results):
        bin_dir = self.ini.config[DB4E_FIELD][BIN_DIR_FIELD]
        xmrig_binary = self.ini.config[XMRIG_FIELD][PROCESS_FIELD]
        # XMRig directory
        xmrig_version = self.ini.config[XMRIG_FIELD][VERSION_FIELD]
        xmrig_dir = XMRIG_FIELD + '-' + str(xmrig_version)
        # Template directory
        tmpl_dir = self._get_templates_dir()
        fq_dst_xmrig_bin_dir = os.path.join(vendor_dir, xmrig_dir, bin_dir)
        fq_src_xmrig = os.path.join(tmpl_dir, xmrig_dir, bin_dir, xmrig_binary)
        shutil.copy(fq_src_xmrig, fq_dst_xmrig_bin_dir)
        results.append(result_row(
            XMRIG_LABEL, GOOD_FIELD,
            f"Installed {XMRIG_LABEL} into {fq_dst_xmrig_bin_dir}"
        ))
        return results

    def _create_monerod_dirs(self, vendor_dir):
        bin_dir = self.ini.config[DB4E_FIELD][BIN_DIR_FIELD]
        conf_dir = self.ini.config[DB4E_FIELD][CONF_DIR_FIELD]
        log_dir = self.ini.config[DB4E_FIELD][LOG_DIR_FIELD]
        run_dir = self.ini.config[DB4E_FIELD][RUN_DIR_FIELD]
        blockchain_dir = self.ini.config[MONEROD_FIELD][BLOCKCHAIN_DIR_FIELD]
        monerod_version = self.ini.config[MONEROD_FIELD][VERSION_FIELD]
        monerod_dir = MONEROD_FIELD + '-' + str(monerod_version)
        os.mkdir(os.path.join(vendor_dir, monerod_dir))
        os.mkdir(os.path.join(vendor_dir, blockchain_dir))
        for sub_dir in [bin_dir, conf_dir, run_dir, log_dir]:
            os.mkdir(os.path.join(vendor_dir, monerod_dir, sub_dir))

    def _create_p2pool_dirs(self, vendor_dir):
        bin_dir = self.ini.config[DB4E_FIELD][BIN_DIR_FIELD]
        conf_dir = self.ini.config[DB4E_FIELD][CONF_DIR_FIELD]
        run_dir = self.ini.config[DB4E_FIELD][RUN_DIR_FIELD]
        p2pool_version = self.ini.config[P2POOL_FIELD][VERSION_FIELD]
        p2pool_dir = P2POOL_FIELD +'-' + str(p2pool_version)
        os.mkdir(os.path.join(vendor_dir, p2pool_dir))
        for sub_dir in [bin_dir, conf_dir, run_dir]:
            os.mkdir(os.path.join(vendor_dir, p2pool_dir, sub_dir))

    def _create_xmrig_dirs(self, vendor_dir):
        bin_dir = self.ini.config[DB4E_FIELD][BIN_DIR_FIELD]
        conf_dir = self.ini.config[DB4E_FIELD][CONF_DIR_FIELD]
        xmrig_version = self.ini.config[XMRIG_FIELD][VERSION_FIELD]
        xmrig_dir = XMRIG_FIELD + '-' + str(xmrig_version)
        os.mkdir(os.path.join(vendor_dir, xmrig_dir))
        for sub_dir in [bin_dir, conf_dir]:
            os.mkdir(os.path.join(vendor_dir, xmrig_dir, sub_dir))

    # Update the db4e service template with deployment values
    def _generate_db4e_service_file(self, vendor_dir):
        effective_id = get_effective_identity()
        user = effective_id[USER_FIELD]
        group = effective_id[GROUP_FIELD]
        systemd_dir = self.ini.config[DB4E_FIELD][SYSTEMD_DIR_FIELD]
        db4e_service_file = self.ini.config[DB4E_FIELD][SERVICE_FILE_FIELD]
        tmpl_dir = self._get_templates_dir()
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

    def _generate_monerod_service_files(self, vendor_dir):
        monerod_version      = self.ini.config[MONEROD_FIELD][VERSION_FIELD]
        monerod_dir = MONEROD_FIELD + '-' + str(monerod_version)
        systemd_dir          = self.ini.config[DB4E_FIELD][SYSTEMD_DIR_FIELD]
        monerod_service_file = self.ini.config[MONEROD_FIELD][SERVICE_FILE_FIELD]
        monerod_socket_file  = self.ini.config[MONEROD_FIELD][SOCKET_FILE_FIELD]
        # Use the effective UID/GID for the Db4E user/group
        effective_id = get_effective_identity()
        user = effective_id[USER_FIELD]
        group = effective_id[GROUP_FIELD]
        # Template directory
        tmpl_dir = self._get_templates_dir()
        # Temporary directory
        tmp_dir = self._get_tmp_dir()
        # Substitution placeholders in the service template files
        placeholders = {
            MONEROD_DIR_PLACEHOLDER: os.path.join(vendor_dir, monerod_dir),
            DB4E_USER_PLACEHOLDER: user,
            DB4E_GROUP_PLACEHOLDER: group,
        }
        fq_monerod_service_file = os.path.join(tmpl_dir, monerod_dir, systemd_dir, monerod_service_file)
        service_contents = self._replace_placeholders(fq_monerod_service_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, monerod_service_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)
        fq_monerod_socket_file = os.path.join(
            tmpl_dir, monerod_dir, systemd_dir, monerod_socket_file)
        service_contents = self._replace_placeholders(fq_monerod_socket_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, monerod_socket_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

    def _generate_p2pool_service_files(self, vendor_dir):
        systemd_dir          = self.ini.config[DB4E_FIELD][SYSTEMD_DIR_FIELD]
        p2pool_service_file  = self.ini.config[P2POOL_FIELD][SERVICE_FILE_FIELD]
        p2pool_socket_file   = self.ini.config[P2POOL_FIELD][SOCKET_FILE_FIELD]
        # Use the effective UID/GID for the Db4E user/group
        effective_id = get_effective_identity()
        user = effective_id[USER_FIELD]
        group = effective_id[GROUP_FIELD]
        # Template directory
        tmpl_dir = self._get_templates_dir()
        # Temporary directory
        tmp_dir = self._get_tmp_dir()
        # P2Pool directory
        p2pool_version       = self.ini.config[P2POOL_FIELD][VERSION_FIELD]
        p2pool_dir = P2POOL_FIELD +'-' + str(p2pool_version)
        fq_p2pool_dir = os.path.join(vendor_dir, p2pool_dir)
        # 
        placeholders = {
            P2POOL_DIR_PLACEHOLDER: fq_p2pool_dir,
            DB4E_USER_PLACEHOLDER: user,
            DB4E_GROUP_PLACEHOLDER: group,
        }
        fq_p2pool_service_file  = os.path.join(
            tmpl_dir, p2pool_dir, systemd_dir, p2pool_service_file)
        service_contents = self._replace_placeholders(fq_p2pool_service_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, p2pool_service_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)
        fq_p2pool_socket_file   = os.path.join(
            tmpl_dir, p2pool_dir, systemd_dir, p2pool_socket_file)
        service_contents = self._replace_placeholders(fq_p2pool_socket_file, placeholders)
        tmp_service_file = os.path.join(tmp_dir, p2pool_socket_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

    def _generate_xmrig_service_file(self, vendor_dir):
        systemd_dir = self.ini.config[DB4E_FIELD][SYSTEMD_DIR_FIELD]
        xmrig_service_file = self.ini.config[XMRIG_FIELD][SERVICE_FILE_FIELD] 
        # Use the effective UID/GID for the Db4E user/group
        effective_id = get_effective_identity()
        user = effective_id[USER_FIELD]
        group = effective_id[GROUP_FIELD]
        # Template directory
        tmpl_dir = self._get_templates_dir()
        # Temporary directory
        tmp_dir = self._get_tmp_dir()
        # XMRig directory
        xmrig_version = self.ini.config[XMRIG_FIELD][VERSION_FIELD]
        xmrig_dir = XMRIG_FIELD + '-' + str(xmrig_version)
        fq_xmrig_dir = os.path.join(vendor_dir, xmrig_dir)
        placeholders = {
            XMRIG_DIR_PLACEHOLDER: fq_xmrig_dir,
            DB4E_USER_PLACEHOLDER: user,
            DB4E_GROUP_PLACEHOLDER: group,
        }
        fq_xmrig_service_file   = os.path.join(
            tmpl_dir, xmrig_dir, systemd_dir, xmrig_service_file)
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


    def _init_db4e_rec(self, db4e_rec, results):
        # Use the effective UID/GID for the Db4E user/group
        effective_id = get_effective_identity()
        user = effective_id[USER_FIELD]
        group = effective_id[GROUP_FIELD]
        db4e_rec[USER_FIELD] = user
        db4e_rec[GROUP_FIELD] = group

        # Determine the Db4E install dir
        db4e_install_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        db4e_rec[INSTALL_DIR_FIELD] = db4e_install_dir
        
        results.append(result_row(
            DB4E_USER_LABEL, GOOD_FIELD,
            f"Added user ({user}) to the {DB4E_LABEL} deployment record"))
        results.append(result_row(
            DB4E_GROUP_LABEL, GOOD_FIELD,
            f"Added group ({group}) to the {DB4E_LABEL} deployment record"))
        results.append(result_row(
            DB4E_GROUP_LABEL, GOOD_FIELD,
            f"Added the {DB4E_LABEL} {INSTALL_DIR_LABEL} to the deployment record"))
        return (results, db4e_rec)

    def _replace_placeholders(self, path: str, placeholders: dict) -> str:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Template file ({path}) not found")
        with open(path, 'r') as f:
            content = f.read()
        for key, val in placeholders.items():
            content = content.replace(f'[[{key}]]', str(val))
        return content

    def _run_sudo_installer(self, vendor_dir, db4e_rec, results):
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
        initial_setup_script = self.ini.config[DB4E_FIELD][SETUP_SCRIPT_FIELD]
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
        self.depl_mgr.update_deployment(db4e_rec)
        return results
    
