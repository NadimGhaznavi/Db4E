# db4e/Modules/InstallMgr.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

import os, shutil
from datetime import datetime, timezone
import tempfile
import subprocess
import stat
import traceback

from textual.containers import Container

from db4e.mgr.BootstrapMgr import BootstrapMgr
from db4e.util.Helper import result_row
from db4e.recs.monero.Db4E import Db4E
from db4e.recs.ops.TUILogLine import TUILogLine
from db4e.recs.monero.P2PoolInternal import P2PoolInternal
from db4e.db.SQLDb import SQLDb
from db4e.db.OpsDb import OpsDb
from db4e.db.DeplDb import DeplDb
from db4e.db.MiningDb import MiningDb

from db4e.constants.DSQL import DCol
from db4e.constants.DDir import DDir
from db4e.constants.DStatus import DStatus
from db4e.constants.DLabel import DLabel
from db4e.constants.DDef import DDef
from db4e.constants.DElem import DElem
from db4e.constants.DPlaceholder import DPlaceholder
from db4e.constants.DField import DField
from db4e.constants.DFile import DFile


class InstallMgr(Container):
    """
    Installer and bootstrap orchestrator for Db4E deployments.
    """

    def __init__(self, bs_mgr: BootstrapMgr):
        """
        Initialize the installer manager and its DB backends.

        :param bs_mgr: Bootstrap manager instance.
        :type bs_mgr: BootstrapMgr
        """
        super().__init__()
        self.bs_mgr = bs_mgr
        self.sql_db = SQLDb(db_type=DField.SERVER, bs_mgr=bs_mgr)
        self.ops_db = OpsDb(sql_db=self.sql_db)
        self.depl_db = DeplDb(sql_db=self.sql_db)
        self.col_name = DDef.DEPL_COLLECTION
        self.tmp_dir = None

    def initial_setup(self, form_data: dict) -> dict:
        """
        Run the initial setup workflow and return log lines.

        :param form_data: Initial setup form payload.
        :type form_data: dict
        :return: TUI log line data.
        :rtype: list[dict]
        """
        try:
            # Track the progress of the initial install
            abort_install = False

            # Clear the console log if the DB has been initialized
            if self.sql_db.is_initialized():
                self.depl_db.clear_all()
                self.ops_db.clear_tui_log()

            # This is the data from the form on the InitialSetup pane
            db4e = form_data[DField.ELEMENT]

            log_line_data = []

            # Check that the user entered their wallet
            log_line_data, abort_install = self._check_wallet(
                log_line_data=log_line_data, db4e=db4e
            )
            if abort_install:
                log_line = {
                    DCol.TRACKED_INSTANCE: DLabel.USER_WALLET,
                    DCol.TRACKED_TYPE: DElem.DB4E,
                    DCol.OPERATION: DField.NEW,
                    DCol.STATUS: DStatus.ERROR,
                    DCol.MESSAGE: "Fatal error, aborting install",
                }
                log_line = self._add_timestamp(log_line)
                log_line_data.append(log_line)
                return log_line_data

            # Check that the user entered a vendor directory
            log_line_data, abort_install = self._check_vendor_dir(
                db4e=db4e, log_line_data=log_line_data
            )
            if abort_install:
                log_line = {
                    DCol.TRACKED_INSTANCE: DLabel.VENDOR_DIR,
                    DCol.TRACKED_TYPE: DElem.DB4E,
                    DCol.OPERATION: DField.NEW,
                    DCol.STATUS: DStatus.ERROR,
                    DCol.MESSAGE: "Fatal error, aborting install",
                }
                log_line = self._add_timestamp(log_line)
                log_line_data.append(log_line)
                return log_line_data

            # Create the vendor directory on the filesystem
            log_line_data, abort_install = self._create_vendor_dir(
                db4e=db4e, log_line_data=log_line_data
            )
            if abort_install:
                log_line = {
                    DCol.TRACKED_INSTANCE: DLabel.VENDOR_DIR,
                    DCol.TRACKED_TYPE: DElem.DB4E,
                    DCol.OPERATION: DField.NEW,
                    DCol.STATUS: DStatus.ERROR,
                    DCol.MESSAGE: "Fatal error, aborting install",
                }
                log_line = self._add_timestamp(log_line)
                log_line_data.append(log_line)
                return log_line_data

            ## We have a valid vendor_dir
            # Initialize the BootstrapMgr and the DB backends
            self.bs_mgr.initialize(vendor_dir=db4e.vendor_dir())
            self.sql_db.initialize(db_dir=self.bs_mgr.get_dir(DDir.DB))
            # The deployment and ops databases get initialized as part
            # of the initial install. Force an initializing of the mining
            # DB.
            mining_db = MiningDb(sql_db=self.sql_db)
            mining_db.check_initialized()  # Initializes the DB

            # Add the log_line_data to the newly initialized ops DB.
            self.ops_db.add_tui_log_line_data(log_line_data=log_line_data)

            # Insert the db4e object into the database
            db4e = self.depl_db.insert_one(db4e)
            # Create a TUI log message
            self.ops_db.add_tui_log_line(
                tracked_instance=DLabel.DB4E,
                tracked_type=DElem.DB4E,
                operation=DField.NEW,
                status=DStatus.COMPLETE,
                message="New Deployment",
            )

            # Create base vendor directories
            vendor_dir = db4e.vendor_dir()
            for aDir in [DDef.BACKUP_DIR, DDef.LOGROTATE]:
                os.makedirs(os.path.join(vendor_dir, aDir))
                self.ops_db.add_tui_log_line(
                    tracked_instance=DLabel.VENDOR_DIR,
                    tracked_type=DElem.DB4E,
                    operation=DField.NEW,
                    status=DStatus.COMPLETE,
                    message="Create Directory",
                    details=f"{vendor_dir}/{aDir}",
                )

            # We have everything we need to finish the install. Update the record.
            self.depl_db.update_one(db4e)

            # Create the Db4E vendor directories
            db4e = self._create_db4e_dirs(db4e=db4e)

            # Create a lograte file for Db4E
            db4e = self._generate_db4e_logrotate(db4e=db4e)

            # Generate the Db4E service file (installed by the sudo installer)
            self._generate_db4e_service_file(db4e=db4e)

            # Create the Monero daemon vendor directories
            db4e = self._create_monerod_dirs(db4e=db4e)

            # Generate the Monero service files (installed by the sudo installer)
            self._generate_tmp_monerod_service_files(db4e=db4e)

            # Copy in the Monero daemon and start script
            db4e = self._copy_monerod_files(db4e=db4e)

            # Create the P2Pool daemon vendor directories
            db4e = self._create_p2pool_dirs(db4e=db4e)

            # Generate the P2Pool service files (installed by the sudo installer)
            self._generate_tmp_p2pool_service_files(db4e=db4e)

            # Copy in the P2Pool daemon and start script
            db4e = self._copy_p2pool_files(db4e=db4e)

            # Create the XMRig miner vendor directories
            db4e = self._create_xmrig_dirs(db4e=db4e)

            # Generate the XMRig service file (installed by the sudo installer)
            self._generate_tmp_xmrig_service_file(db4e=db4e)

            # Copy in the XMRig miner
            db4e = self._copy_xmrig_file(db4e=db4e)

            # Deploy internal P2Pool instances to gather metrics
            db4e = self._deploy_internal_p2pools(db4e=db4e)

            # Run the installer (with sudo)
            db4e = self._run_sudo_installer(db4e=db4e)

            # Return the updated Db4E deployment object with embded results
            log_lines = self._return_tui_log()

            # Close the connection to the vendor_dir/db/server.db file, so the Db4E server can
            # open it cleanly.
            self.sql_db.close()

            return log_lines

        except Exception as e:
            print(f"ERROR: {e}")
            print(f"STACKTRACE: {traceback.format_exc()}")

    def initial_setup_proceed(self, form_data: dict):
        """
        Placeholder for initial setup proceed action.

        :param form_data: Initial setup form payload.
        :type form_data: dict
        :return: Db4E deployment object.
        :rtype: Db4E
        """
        db4e = Db4E()
        return db4e

    def _add_timestamp(self, log_line: dict):
        """
        Add timestamp fields to a log line dict.

        :param log_line: Log line dictionary to update.
        :type log_line: dict
        :return: Updated log line dictionary.
        :rtype: dict
        """
        now = datetime.now()
        log_line.update(
            {
                DCol.UPDATED_YEAR: now.year,
                DCol.UPDATED_MONTH: now.month,
                DCol.UPDATED_DAY: now.day,
                DCol.UPDATED_HOUR: now.hour,
                DCol.UPDATED_MINUTE: now.minute,
                DCol.UPDATED_SECOND: now.second,
            }
        )
        return log_line

    def _check_wallet(self, log_line_data: list, db4e: Db4E):
        """
        Validate that a user wallet is present.

        :param log_line_data: Accumulated log lines.
        :type log_line_data: list[dict]
        :param db4e: Db4E deployment object.
        :type db4e: Db4E
        :return: Tuple of (log_line_data, abort_install).
        :rtype: tuple[list[dict], bool]
        """
        # print(f"InstallMgr:_check_wallet(): user_wallet: {user_wallet}")
        abort_install = False
        # User did not provide any wallet
        if not db4e.user_wallet():
            abort_install = True
            log_line = {
                DCol.TRACKED_INSTANCE: DLabel.USER_WALLET,
                DCol.TRACKED_TYPE: DElem.DB4E,
                DCol.OPERATION: DField.NEW,
                DCol.STATUS: DStatus.ERROR,
                DCol.MESSAGE: "Missing user wallet",
            }
            log_line = self._add_timestamp(log_line)
            log_line_data.append(log_line)
            return log_line_data, abort_install

        log_line = {
            DCol.TRACKED_INSTANCE: DLabel.USER_WALLET,
            DCol.TRACKED_TYPE: DElem.DB4E,
            DCol.OPERATION: DField.NEW,
            DCol.STATUS: DStatus.COMPLETE,
            DCol.MESSAGE: "Set User Wallet",
            DCol.DETAILS: f"{db4e.user_wallet()[:7]}...",
        }
        log_line = self._add_timestamp(log_line)
        log_line_data.append(log_line)

        return log_line_data, abort_install

    def _check_vendor_dir(self, db4e: Db4E, log_line_data: list):
        """
        Validate that a vendor directory is present.

        :param db4e: Db4E deployment object.
        :type db4e: Db4E
        :param log_line_data: Accumulated log lines.
        :type log_line_data: list[dict]
        :return: Tuple of (log_line_data, abort_install).
        :rtype: tuple[list[dict], bool]
        """
        # print(f"InstallMgr:_vendor_dir(): {vendor_dir}")
        abort_install = False
        if not db4e.vendor_dir():
            abort_install = True
            log_line = {
                DCol.TRACKED_INSTANCE: DLabel.VENDOR_DIR,
                DCol.TRACKED_TYPE: DElem.DB4E,
                DCol.OPERATION: DField.NEW,
                DCol.STATUS: DStatus.ERROR,
                DCol.MESSAGE: "Missing vendor directory",
            }
            log_line = self._add_timestamp(log_line)
            log_line_data.append(log_line)
        return log_line_data, abort_install

    # Copy Db4E files
    def _copy_db4e_files(self, vendor_dir):
        """
        Copy Db4E scripts into the vendor directory.

        :param vendor_dir: Vendor directory path.
        :type vendor_dir: str
        :return: List of results or log entries.
        :rtype: list
        """
        results = []
        db4e_src_dir = DElem.DB4E
        db4e_dest_dir = DElem.DB4E + "-" + str(DDef.DB4E_VERSION)
        # Template directory
        tmpl_dir = self.bs_mgr.get_dir(DDir.TEMPLATE)
        # Substitute placeholder in the db4e-service.sh script
        install_dir = self.bs_mgr.get_dir(DDir.INSTALL)
        python = self.bs_mgr.get_dir(DFile.PYTHON)
        placeholders = {
            DPlaceholder.PYTHON: python,
            DPlaceholder.INSTALL_DIR: install_dir,
        }
        fq_src_script = os.path.join(
            tmpl_dir, db4e_src_dir, DDef.BIN_DIR, DDef.DB4E_START_SCRIPT
        )
        fq_dest_script = os.path.join(
            vendor_dir, db4e_dest_dir, DDef.BIN_DIR, DDef.DB4E_START_SCRIPT
        )
        script_contents = self._replace_placeholders(fq_src_script, placeholders)
        with open(fq_dest_script, "w") as f:
            f.write(script_contents)
        # Make it executable
        current_permissions = os.stat(fq_dest_script).st_mode
        new_permissions = (
            current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )
        os.chmod(fq_dest_script, new_permissions)
        self.ops_db.add_tui_log_line(
            tracked_type=DElem.DB4E,
            tracked_instance=DLabel.DB4E,
            operation=DField.NEW,
            status=DStatus.COMPLETE,
            message="Install Script",
            details=fq_dest_script,
        )
        return results

    # Copy monerod files
    def _copy_monerod_files(self, db4e: Db4E):
        """
        Copy MoneroD binaries and scripts into the vendor directory.

        :param db4e: Db4E deployment object.
        :type db4e: Db4E
        :return: Updated Db4E deployment object.
        :rtype: Db4E
        """
        vendor_dir = db4e.vendor_dir()
        # Template directory
        tmpl_dir = self.bs_mgr.get_dir(DDir.TEMPLATE)
        # Copy in the Monero daemon and startup scripts
        fq_dst_bin_dir = os.path.join(vendor_dir, DElem.MONEROD, DDef.BIN_DIR)
        fq_dst_monerod_dest_script = os.path.join(
            vendor_dir, DElem.MONEROD, DDef.BIN_DIR, DDef.MONEROD_START_SCRIPT
        )
        fq_src_monerod = os.path.join(
            tmpl_dir, DElem.MONEROD, DDef.BIN_DIR, DDef.MONEROD_PROCESS
        )

        shutil.copy(fq_src_monerod, fq_dst_bin_dir)
        self.ops_db.add_tui_log_line(
            tracked_type=DElem.DB4E,
            tracked_instance=DLabel.MONEROD,
            operation=DField.NEW,
            status=DStatus.COMPLETE,
            message="Install Program",
            details=f"{fq_dst_bin_dir}/{DDef.MONEROD_PROCESS}",
        )
        fq_src_monerod_start_script = os.path.join(
            tmpl_dir, DElem.MONEROD, DDef.BIN_DIR, DDef.MONEROD_START_SCRIPT
        )
        shutil.copy(fq_src_monerod_start_script, fq_dst_monerod_dest_script)
        # Make it executable
        current_permissions = os.stat(fq_dst_monerod_dest_script).st_mode
        new_permissions = (
            current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )
        os.chmod(fq_dst_monerod_dest_script, new_permissions)
        self.ops_db.add_tui_log_line(
            tracked_type=DElem.DB4E,
            tracked_instance=DLabel.MONEROD,
            operation=DField.NEW,
            status=DStatus.COMPLETE,
            message="Install Script",
            details=f"{fq_dst_monerod_dest_script}",
        )
        return db4e

    def _copy_p2pool_files(self, db4e: Db4E) -> Db4E:
        """
        Copy P2Pool binaries and scripts into the vendor directory.

        :param db4e: Db4E deployment object.
        :type db4e: Db4E
        :return: Updated Db4E deployment object.
        :rtype: Db4E
        """
        vendor_dir = db4e.vendor_dir()
        # Template directory
        tmpl_dir = self.bs_mgr.get_dir(DDir.TEMPLATE)
        # Copy in the P2Pool daemon and startup script
        fq_src_p2pool = os.path.join(
            tmpl_dir, DElem.P2POOL, DDef.BIN_DIR, DDef.P2POOL_PROCESS
        )
        fq_dst_bin_dir = os.path.join(vendor_dir, DElem.P2POOL, DDef.BIN_DIR)
        fq_src_p2pool_start_script = os.path.join(
            tmpl_dir, DElem.P2POOL, DDef.BIN_DIR, DDef.P2POOL_START_SCRIPT
        )
        fq_dst_p2pool_start_script = os.path.join(
            vendor_dir, DElem.P2POOL, DDef.BIN_DIR, DDef.P2POOL_START_SCRIPT
        )
        shutil.copy(fq_src_p2pool, fq_dst_bin_dir)
        self.ops_db.add_tui_log_line(
            tracked_type=DElem.DB4E,
            tracked_instance=DLabel.P2POOL,
            operation=DField.NEW,
            status=DStatus.COMPLETE,
            message="Install Program",
            details=f"{fq_dst_bin_dir}/{DDef.P2POOL_PROCESS}",
        )
        shutil.copy(fq_src_p2pool_start_script, fq_dst_p2pool_start_script)
        # Make it executable
        current_permissions = os.stat(fq_dst_p2pool_start_script).st_mode
        new_permissions = (
            current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )
        os.chmod(fq_dst_p2pool_start_script, new_permissions)
        self.ops_db.add_tui_log_line(
            tracked_type=DElem.DB4E,
            tracked_instance=DLabel.P2POOL,
            operation=DField.NEW,
            status=DStatus.COMPLETE,
            message="Install Script",
            details=f"{fq_dst_p2pool_start_script}",
        )
        return db4e

    def _copy_xmrig_file(self, db4e: Db4E) -> Db4E:
        """
        Copy XMRig binaries into the vendor directory.

        :param db4e: Db4E deployment object.
        :type db4e: Db4E
        :return: Updated Db4E deployment object.
        :rtype: Db4E
        """
        vendor_dir = db4e.vendor_dir()
        xmrig_binary = DDef.XMRIG_PROCESS
        # Template directory
        tmpl_dir = self.bs_mgr.get_dir(DDir.TEMPLATE)
        fq_dst_xmrig_bin_dir = os.path.join(vendor_dir, DElem.XMRIG, DDef.BIN_DIR)
        fq_src_xmrig = os.path.join(tmpl_dir, DElem.XMRIG, DDef.BIN_DIR, xmrig_binary)
        shutil.copy(fq_src_xmrig, fq_dst_xmrig_bin_dir)
        self.ops_db.add_tui_log_line(
            tracked_type=DElem.DB4E,
            tracked_instance=DLabel.XMRIG,
            operation=DField.NEW,
            status=DStatus.COMPLETE,
            message="Install Program",
            details=f"{fq_dst_xmrig_bin_dir}/{xmrig_binary}",
        )
        return db4e

    def _create_db4e_dirs(self, db4e: Db4E) -> Db4E:
        """
        Create Db4E vendor directories.

        :param db4e: Db4E deployment object.
        :type db4e: Db4E
        :return: Updated Db4E deployment object.
        :rtype: Db4E
        """
        vendor_dir = db4e.vendor_dir()
        fq_db4e_dir = os.path.join(vendor_dir, DElem.DB4E)
        # Create the base Db4E directory
        os.makedirs(os.path.join(fq_db4e_dir))
        self.ops_db.add_tui_log_line(
            tracked_type=DElem.DB4E,
            tracked_instance=DLabel.DB4E,
            operation=DField.NEW,
            status=DStatus.COMPLETE,
            message="Create Directory",
            details=fq_db4e_dir,
        )
        # Create the sub-directories
        for sub_dir in [DDef.LOG_DIR, DDef.DB_DIR]:
            os.mkdir(os.path.join(fq_db4e_dir, sub_dir))
            self.ops_db.add_tui_log_line(
                tracked_type=DElem.DB4E,
                tracked_instance=DLabel.DB4E,
                operation=DField.NEW,
                status=DStatus.COMPLETE,
                message="Create Directory",
                details=f"{fq_db4e_dir}/{sub_dir}",
            )
        return db4e

    def _create_monerod_dirs(self, db4e: Db4E) -> Db4E:
        """
        Create MoneroD vendor directories.

        :param db4e: Db4E deployment object.
        :type db4e: Db4E
        :return: Updated Db4E deployment object.
        :rtype: Db4E
        """
        vendor_dir = db4e.vendor_dir()
        fq_monerod_dir = os.path.join(vendor_dir, DElem.MONEROD)

        # Create the base Monero directory
        os.mkdir(fq_monerod_dir)
        self.ops_db.add_tui_log_line(
            tracked_type=DElem.DB4E,
            tracked_instance=DLabel.MONEROD,
            operation=DField.NEW,
            status=DStatus.COMPLETE,
            message="Create Directory",
            details=fq_monerod_dir,
        )

        # Create the sub-directories
        for sub_dir in [DDef.BIN_DIR, DDef.CONF_DIR]:
            fq_sub_dir = os.path.join(fq_monerod_dir, sub_dir)
            os.mkdir(fq_sub_dir)
            self.ops_db.add_tui_log_line(
                tracked_type=DElem.DB4E,
                tracked_instance=DLabel.MONEROD,
                operation=DField.NEW,
                status=DStatus.COMPLETE,
                message="Create Directory",
                details=fq_sub_dir,
            )
        return db4e

    def _create_p2pool_dirs(self, db4e: Db4E) -> Db4E:
        """
        Create P2Pool vendor directories.

        :param db4e: Db4E deployment object.
        :type db4e: Db4E
        :return: Updated Db4E deployment object.
        :rtype: Db4E
        """
        vendor_dir = db4e.vendor_dir()
        fq_p2pool_dir = os.path.join(vendor_dir, DElem.P2POOL)

        # Create the base P2Pool directory
        os.mkdir(os.path.join(fq_p2pool_dir))
        self.ops_db.add_tui_log_line(
            tracked_type=DElem.DB4E,
            tracked_instance=DLabel.P2POOL,
            operation=DField.NEW,
            status=DStatus.COMPLETE,
            message="Create Directory",
            details=fq_p2pool_dir,
        )

        # Create the sub directories
        for sub_dir in [DDef.BIN_DIR, DDef.CONF_DIR]:
            fq_sub_dir = os.path.join(fq_p2pool_dir, sub_dir)
            os.mkdir(fq_sub_dir)
            self.ops_db.add_tui_log_line(
                tracked_type=DElem.DB4E,
                tracked_instance=DLabel.P2POOL,
                operation=DField.NEW,
                status=DStatus.COMPLETE,
                message="Create Directory",
                details=fq_sub_dir,
            )
        return db4e

    def _create_vendor_dir(self, db4e: Db4E, log_line_data):
        """
        Create or rotate the vendor directory.

        :param db4e: Db4E deployment object.
        :type db4e: Db4E
        :param log_line_data: Accumulated log lines.
        :type log_line_data: list[dict]
        :return: Tuple of (log_line_data, abort_install).
        :rtype: tuple[list[dict], bool]
        """
        # print(f"InstallMgr:_create_vendor_dir(): vendor_dir {vendor_dir}")
        abort_install = False
        vendor_dir = db4e.vendor_dir()
        if os.path.exists(vendor_dir):
            log_line = {
                DCol.TRACKED_INSTANCE: DLabel.VENDOR_DIR,
                DCol.TRACKED_TYPE: DElem.DB4E,
                DCol.OPERATION: DField.NEW,
                DCol.STATUS: DStatus.WARN,
                DCol.MESSAGE: "Found directory",
                DCol.DETAILS: vendor_dir,
            }
            log_line = self._add_timestamp(log_line)
            log_line_data.append(log_line)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_vendor_dir = vendor_dir + "." + timestamp

            try:
                os.rename(vendor_dir, backup_vendor_dir)
                log_line = {
                    DCol.TRACKED_INSTANCE: DLabel.VENDOR_DIR,
                    DCol.TRACKED_TYPE: DElem.DB4E,
                    DCol.OPERATION: DField.NEW,
                    DCol.STATUS: DStatus.WARN,
                    DCol.MESSAGE: "Renamed directory",
                    DCol.DETAILS: f"{vendor_dir} > {backup_vendor_dir}",
                }
                log_line = self._add_timestamp(log_line)
                log_line_data.append(log_line)

            except (PermissionError, OSError, FileNotFoundError) as e:
                log_line = {
                    DCol.TRACKED_INSTANCE: DLabel.VENDOR_DIR,
                    DCol.TRACKED_TYPE: DElem.DB4E,
                    DCol.OPERATION: DField.NEW,
                    DCol.STATUS: DStatus.ERROR,
                    DCol.MESSAGE: "Failed to rename existing vendor directory",
                    DCol.DETAILS: e,
                }
                log_line = self._add_timestamp(log_line)
                log_line_data.append(log_line)
                abort_install = True
                return log_line_data, abort_install  # Abort the install

        try:
            os.makedirs(vendor_dir)
            log_line = {
                DCol.TRACKED_INSTANCE: DLabel.VENDOR_DIR,
                DCol.TRACKED_TYPE: DElem.DB4E,
                DCol.OPERATION: DField.NEW,
                DCol.STATUS: DStatus.COMPLETE,
                DCol.MESSAGE: "Create Directory",
                DCol.DETAILS: vendor_dir,
            }
            log_line = self._add_timestamp(log_line)
            log_line_data.append(log_line)

        except (PermissionError, FileNotFoundError, FileExistsError) as e:
            log_line = {
                DCol.TRACKED_INSTANCE: DLabel.VENDOR_DIR,
                DCol.TRACKED_TYPE: DElem.DB4E,
                DCol.OPERATION: DField.NEW,
                DCol.STATUS: DStatus.ERROR,
                DCol.MESSAGE: "Failed to create vendor directory",
                DCol.DETAILS: e,
            }
            log_line = self._add_timestamp(log_line)
            log_line_data.append(log_line)
            return log_line_data, abort_install

        return log_line_data, abort_install

    def _create_xmrig_dirs(self, db4e: Db4E) -> Db4E:
        """
        Create XMRig vendor directories.

        :param db4e: Db4E deployment object.
        :type db4e: Db4E
        :return: Updated Db4E deployment object.
        :rtype: Db4E
        """
        vendor_dir = db4e.vendor_dir()
        fq_xmrig_dir = os.path.join(vendor_dir, DElem.XMRIG)
        os.mkdir(os.path.join(fq_xmrig_dir))
        self.ops_db.add_tui_log_line(
            tracked_type=DElem.DB4E,
            tracked_instance=DLabel.XMRIG,
            operation=DField.NEW,
            status=DStatus.COMPLETE,
            message="Create Directory",
            details=fq_xmrig_dir,
        )
        for sub_dir in [DDef.BIN_DIR, DDef.CONF_DIR, DDef.LOG_DIR]:
            fq_sub_dir = os.path.join(fq_xmrig_dir, sub_dir)
            os.mkdir(fq_sub_dir)
            self.ops_db.add_tui_log_line(
                tracked_type=DElem.DB4E,
                tracked_instance=DLabel.XMRIG,
                operation=DField.NEW,
                status=DStatus.COMPLETE,
                message="Create Directory",
                details=fq_sub_dir,
            )
        return db4e

    # Deploy metrics gathering P2Pool instances
    def _deploy_internal_p2pools(self, db4e: Db4E):
        """
        Deploy internal P2Pool instances for metrics gathering.

        :param db4e: Db4E deployment object.
        :type db4e: Db4E
        :return: Updated Db4E deployment object.
        :rtype: Db4E
        """
        try:
            vendor_dir = db4e.vendor_dir()
            for chain_label in [
                DLabel.MAIN_CHAIN,
                DLabel.MINI_CHAIN,
                DLabel.NANO_CHAIN,
            ]:
                p2pool = P2PoolInternal()
                log_file = os.path.join(
                    vendor_dir,
                    DElem.P2POOL,
                    chain_label,
                    DDef.LOG_DIR,
                    DFile.P2POOL_LOG,
                )
                stats_mod = os.path.join(
                    vendor_dir, DElem.P2POOL, chain_label, DDef.API_DIR, DFile.STATS_MOD
                )
                stdin_path = os.path.join(
                    vendor_dir,
                    DElem.P2POOL,
                    chain_label,
                    DDef.RUN_DIR,
                    DFile.P2POOL_STDIN,
                )
                config_file = os.path.join(
                    vendor_dir,
                    DElem.P2POOL,
                    DDef.CONF_DIR,
                    chain_label + DField.INI_SUFFIX,
                )

                # Set the internal P2Pool instance parameters
                p2pool.set_type(
                    chain_label=chain_label,
                    log_file=log_file,
                    stats_mod=stats_mod,
                    stdin_path=stdin_path,
                    config_file=config_file,
                )

                # Add the new deployment record
                self.depl_db.insert_one(p2pool)

                # Create a TUI log message
                self.ops_db.add_tui_log_line(
                    tracked_type=DElem.P2POOL_INTERNAL,
                    tracked_instance=f"{chain_label} Sidechain",
                    operation=DField.NEW,
                    status=DStatus.COMPLETE,
                    message="New Deployment",
                )

                # Create a logrotate config file for the P2Pool log
                logrotate_tmpl = self.bs_mgr.get_logrotate_template(DElem.P2POOL)
                db4e_group = db4e.db4e_group()
                vendor_dir = db4e.vendor_dir()
                p2pool.gen_logrotate_config(
                    tmpl_file=logrotate_tmpl,
                    vendor_dir=vendor_dir,
                    db4e_group=db4e_group,
                )
                logrotate_config = DElem.P2POOL + "-" + chain_label + DDef.CONF_SUFFIX
                fq_logrotate_config = os.path.join(
                    vendor_dir, DDef.LOGROTATE, logrotate_config
                )
                self.ops_db.add_tui_log_line(
                    tracked_type=DElem.P2POOL_INTERNAL,
                    tracked_instance=f"{chain_label} Sidechain",
                    operation=DField.NEW,
                    status=DStatus.COMPLETE,
                    message="Create Config",
                    details=fq_logrotate_config,
                )

                # Create the base, API, run and logs directories
                base_dir = os.path.join(vendor_dir, DElem.P2POOL, chain_label)
                os.makedirs(base_dir)
                for aDir in [DDef.API_DIR, DDef.RUN_DIR, DDef.LOG_DIR]:
                    sub_dir = os.path.join(base_dir, aDir)
                    os.makedirs(sub_dir)
                    self.ops_db.add_tui_log_line(
                        tracked_type=DElem.P2POOL_INTERNAL,
                        tracked_instance=f"{chain_label} Sidechain",
                        operation=DField.NEW,
                        status=DStatus.COMPLETE,
                        message="Create Directory",
                        details=sub_dir,
                    )

            return db4e

        except Exception as e:
            print(f"ERROR: {e}")
            print(f"STACKTRACE: {traceback.format_exc()}")

    # Create a logrotate file for Db4E
    def _generate_db4e_logrotate(self, db4e: Db4E):
        """
        Generate the Db4E logrotate configuration.

        :param db4e: Db4E deployment object.
        :type db4e: Db4E
        :return: Updated Db4E deployment object.
        :rtype: Db4E
        """
        logrotate_tmpl = self.bs_mgr.get_logrotate_template(DElem.DB4E)
        vendor_dir = db4e.vendor_dir()
        fq_config = os.path.join(
            vendor_dir, DDef.LOGROTATE, DElem.DB4E + DDef.CONF_SUFFIX
        )

        # Populate the config template
        placeholders = {
            DPlaceholder.VENDOR_DIR: vendor_dir,
            DPlaceholder.MAX_LOG_FILES: DDef.MAX_LOG_FILES,
            DPlaceholder.MAX_LOG_SIZE: DDef.MAX_LOG_SIZE,
        }
        with open(logrotate_tmpl, "r") as f:
            logrotate_contents = f.read()
            final_config = logrotate_contents
            for key, val in placeholders.items():
                final_config = final_config.replace(f"[[{key}]]", str(val))

        # Write the config file
        with open(fq_config, "w") as f:
            f.write(final_config)
        self.ops_db.add_tui_log_line(
            tracked_type=DElem.DB4E,
            tracked_instance=DLabel.DB4E,
            operation=DField.NEW,
            status=DStatus.COMPLETE,
            message="Create Config",
            details=fq_config,
        )
        return db4e

    # Update the db4e service template with deployment values
    def _generate_db4e_service_file(self, db4e: Db4E):
        """
        Generate a temporary Db4E service file.

        :param db4e: Db4E deployment object.
        :type db4e: Db4E
        """
        tmp_dir = self._get_tmp_dir()
        tmpl_dir = self.bs_mgr.get_dir(DDir.TEMPLATE)
        db4e_dir = self.bs_mgr.get_dir(DDir.INSTALL)
        fq_db4e_dir = os.path.join(db4e_dir)
        placeholders = {
            DPlaceholder.DB4E_USER: db4e.db4e_user(),
            DPlaceholder.DB4E_GROUP: db4e.db4e_group(),
            DPlaceholder.DB4E_DIR: fq_db4e_dir,
        }
        fq_db4e_service_file = os.path.join(
            tmpl_dir, DElem.DB4E, DDef.SYSTEMD_DIR, DDef.DB4E_SERVICE_FILE
        )
        service_contents = self._replace_placeholders(
            fq_db4e_service_file, placeholders
        )
        tmp_service_file = os.path.join(tmp_dir, DDef.DB4E_SERVICE_FILE)
        with open(tmp_service_file, "w") as f:
            f.write(service_contents)

    def _generate_tmp_monerod_service_files(self, db4e: Db4E):
        """
        Generate temporary MoneroD systemd service files.

        :param db4e: Db4E deployment object.
        :type db4e: Db4E
        """
        vendor_dir = db4e.vendor_dir()
        # Template directory
        tmpl_dir = self.bs_mgr.get_dir(DDir.TEMPLATE)
        # Temporary directory
        tmp_dir = self._get_tmp_dir()

        # Substitution placeholders in the service template files
        placeholders = {
            DPlaceholder.MONEROD_DIR: os.path.join(vendor_dir, DElem.MONEROD),
            DPlaceholder.DB4E_USER: db4e.db4e_user(),
            DPlaceholder.DB4E_GROUP: db4e.db4e_group(),
        }

        # Generate a temporary monerod.systemd for the sudo script to install
        fq_monerod_service_file = os.path.join(
            tmpl_dir, DElem.MONEROD, DDef.SYSTEMD_DIR, DDef.MONEROD_SERVICE_FILE
        )
        service_contents = self._replace_placeholders(
            fq_monerod_service_file, placeholders
        )
        tmp_service_file = os.path.join(tmp_dir, DDef.MONEROD_SERVICE_FILE)
        with open(tmp_service_file, "w") as f:
            f.write(service_contents)

        # Generate a temporary monerod.socket for the sudo script to install
        fq_monerod_socket_file = os.path.join(
            tmpl_dir,
            DElem.MONEROD,
            DDef.SYSTEMD_DIR,
            DDef.MONEROD_SOCKET_SERVICE,
        )
        service_contents = self._replace_placeholders(
            fq_monerod_socket_file, placeholders
        )
        tmp_socket_file = os.path.join(tmp_dir, DDef.MONEROD_SOCKET_SERVICE)
        with open(tmp_socket_file, "w") as f:
            f.write(service_contents)

    def _generate_tmp_p2pool_service_files(self, db4e: Db4E):
        """
        Generate temporary P2Pool systemd service files.

        :param db4e: Db4E deployment object.
        :type db4e: Db4E
        """
        vendor_dir = db4e.vendor_dir()
        # Template directory
        tmpl_dir = self.bs_mgr.get_dir(DDir.TEMPLATE)
        # Temporary directory
        tmp_dir = self._get_tmp_dir()

        # P2Pool directory
        fq_p2pool_dir = os.path.join(vendor_dir, DElem.P2POOL)

        # Substitution placeholders in the service template files        #
        placeholders = {
            DPlaceholder.P2POOL_DIR: fq_p2pool_dir,
            DPlaceholder.DB4E_USER: db4e.db4e_user(),
            DPlaceholder.DB4E_GROUP: db4e.db4e_group(),
        }

        # Generate a temporary p2pool.service for the sudo script to install
        fq_p2pool_service_file = os.path.join(
            tmpl_dir, DElem.P2POOL, DDef.SYSTEMD_DIR, DDef.P2POOL_SERVICE_FILE
        )
        service_contents = self._replace_placeholders(
            fq_p2pool_service_file, placeholders
        )
        tmp_service_file = os.path.join(tmp_dir, DDef.P2POOL_SERVICE_FILE)
        with open(tmp_service_file, "w") as f:
            f.write(service_contents)

        # Generate a temporary p2pool.socket
        fq_p2pool_socket_file = os.path.join(
            tmpl_dir,
            DElem.P2POOL,
            DDef.SYSTEMD_DIR,
            DDef.P2POOL_SERVICE_SOCKET_FILE,
        )
        service_contents = self._replace_placeholders(
            fq_p2pool_socket_file, placeholders
        )
        tmp_service_file = os.path.join(tmp_dir, DDef.P2POOL_SERVICE_SOCKET_FILE)
        with open(tmp_service_file, "w") as f:
            f.write(service_contents)

    def _generate_tmp_xmrig_service_file(self, db4e: Db4E) -> None:
        """
        Generate a temporary XMRig systemd service file.

        :param db4e: Db4E deployment object.
        :type db4e: Db4E
        """
        vendor_dir = db4e.vendor_dir()
        # Template directory
        tmpl_dir = self.bs_mgr.get_dir(DDir.TEMPLATE)
        # Temporary directory
        tmp_dir = self._get_tmp_dir()
        # XMRig directory
        fq_xmrig_dir = os.path.join(vendor_dir, DElem.XMRIG)
        placeholders = {
            DPlaceholder.XMRIG_DIR: fq_xmrig_dir,
            DPlaceholder.DB4E_USER: db4e.db4e_user(),
            DPlaceholder.DB4E_GROUP: db4e.db4e_group(),
        }
        fq_xmrig_service_file = os.path.join(
            tmpl_dir, DElem.XMRIG, DDef.SYSTEMD_DIR, DDef.XMRIG_SERVICE_FILE
        )
        service_contents = self._replace_placeholders(
            fq_xmrig_service_file, placeholders
        )
        tmp_service_file = os.path.join(tmp_dir, DDef.XMRIG_SERVICE_FILE)
        with open(tmp_service_file, "w") as f:
            f.write(service_contents)

    def _get_tmp_dir(self):
        """
        Return the temporary directory path, creating it if needed.

        :return: Temporary directory path.
        :rtype: str
        """
        # Helper function
        if not self.tmp_dir:
            tmp_obj = tempfile.TemporaryDirectory()
            self.tmp_dir = tmp_obj.name  # Store path string
            self._tmp_obj = tmp_obj  # Keep a reference to the object
        return self.tmp_dir

    def _replace_placeholders(self, path: str, placeholders: dict) -> str:
        """
        Replace placeholders in a template file and return its contents.

        :param path: Template file path.
        :type path: str
        :param placeholders: Placeholder mapping.
        :type placeholders: dict
        :return: Rendered template contents.
        :rtype: str
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Template file ({path}) not found")
        with open(path, "r") as f:
            content = f.read()
        for key, val in placeholders.items():
            content = content.replace(f"[[{key}]]", str(val))
        return content

    def _return_tui_log(self):
        """
        Return TUI log data and append an install success marker.

        :return: Log data list.
        :rtype: list
        """
        log_data = self.ops_db.get_tui_log()
        log_data.append(DField.INSTALL_SUCCESSFUL)
        return log_data

    def _run_sudo_installer(self, db4e: Db4E) -> Db4E:
        """
        Run the sudo installer script to complete installation.

        :param db4e: Db4E deployment object.
        :type db4e: Db4E
        :return: Updated Db4E deployment object.
        :rtype: Db4E
        """
        vendor_dir = db4e.vendor_dir()
        # Temporary directory
        tmp_dir = self._get_tmp_dir()
        db4e_install_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )
        # Run the bin/db4e-installer.sh
        fq_initial_setup = os.path.join(
            db4e_install_dir, DDef.BIN_DIR, DDef.DB4E_INITIAL_SETUP_SCRIPT
        )
        try:
            cmd_result = subprocess.run(
                [
                    DDef.SUDO_CMD,
                    fq_initial_setup,
                    db4e_install_dir,
                    db4e.db4e_user(),
                    db4e.db4e_group(),
                    vendor_dir,
                    tmp_dir,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                input=b"",
                timeout=10,
            )
            stdout = cmd_result.stdout.decode().strip()
            stderr = cmd_result.stderr.decode().strip()

            # Check the return code
            if cmd_result.returncode != 0:
                db4e.msg(
                    DLabel.DB4E, DStatus.ERROR, f"Service install failed.\n\n{stderr}"
                )
                shutil.rmtree(tmp_dir)
                return db4e

            installer_output = f"{stdout}"
            for line in installer_output.split("\n"):
                message, details = line.split("----")
                self.ops_db.add_tui_log_line(
                    tracked_type=DElem.DB4E,
                    tracked_instance=DLabel.DB4E,
                    operation=DField.NEW,
                    status=DStatus.COMPLETE,
                    message=message,
                    details=details,
                )
            shutil.rmtree(tmp_dir)

        except Exception as e:
            self.ops_db.add_tui_log_line(
                tracked_type=DElem.DB4E,
                tracked_instance=DLabel.DB4E,
                operation=DField.NEW,
                status=DStatus.ERROR,
                message=f"Fatal error: {e}",
            )

        return db4e
