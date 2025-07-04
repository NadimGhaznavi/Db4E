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

# The Mongo collection that houses the deployment records
DEPL_COL = 'depl'

class InstallMgr:

    def __init__(self, config: Config):
        self.ini = config
        self.depl_mgr = DeploymentMgr(config)
        self.db = DbMgr(config)

    async def initial_setup(self, form_data: dict) -> dict:
        # Track the progress of the initial install
        results = []
        # Validate the data
        user_wallet = form_data['user_wallet']
        db4e_group = form_data['db4e_group']
        vendor_dir = form_data['vendor_dir']

        db4e_rec = self.depl_mgr.get_deployment('db4e')
        if db4e_rec:
            # The Mongo record for 'db4e' exists: Assume we're doing a reinstall
            results.append({'Db4E core': {'status': 'warn', 'msg': 'Db4E core already exists'}})
            old_user_wallet = db4e_rec['user_wallet']
            old_group = db4e_rec['group']
            old_vendor_dir = db4e_rec['vendor_dir']

            if user_wallet != old_user_wallet:
                results.append({'Monero wallet': {'status': 'warn', 'msg': 'Old Monero wallet record'}})
                db4e_rec['user_wallet'] = user_wallet
                self.depl_mgr.update_deployent(db4e_rec)
                results.append({'Monero wallet': {'status': 'good', 'msg': 'Updated Monero wallet'}})
            if db4e_group != old_group:
                results.append({'Db4E Group': {'status':'warn', 'msg': f'Old Db4E group ({old_group}) record'}})
                os.environ['DB4E_OLD_GROUP'] = old_group
            if vendor_dir != old_vendor_dir:
                results.append({'Deployment directory': {'status':'warn', 'msg': f'Old deployment directory ({old_vendor_dir}) record'}})
        else:
            db4e_rec = self.db.get_new_rec('db4e')
            db4e_rec['user_wallet'] = user_wallet
            self.depl_mgr.add_deployment(db4e_rec)

        # Create the vendor directory
        if os.path.exists(vendor_dir):
            results.append({'Deployment directory': {'status':'warn', 'msg': f'Found existing deployment directory ({vendor_dir})'}})
            timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            try:
                backup_vendor_dir = vendor_dir + '.' + timestamp
                os.rename(vendor_dir, backup_vendor_dir)
                results.append({'Deployment directory': {'status': 'warn', 'msg': f'Backed up old deployment directory ({backup_vendor_dir})'}})
            except PermissionError:
                results.append({'Deployment directory': {'status': 'error', 'msg': f'Failed to backup old deployment directory ({backup_vendor_dir})'}})
                return results # Abort the install
        try:
            os.mkdir(vendor_dir)
        except (PermissionError, FileNotFoundError, FileExistsError) as e:
            error_msg = f'Failed to create directory ({vendor_dir}). Make sure you '
            error_msg += 'have permission to create the directory and that the parent '
            error_msg += 'directory exists\n\n'
            error_msg += f'{e}'
            results.append({'Deployment directory': {'status': 'error', 'msg': error_msg}})
            return results # Abort the install

        # Additional config settings
        bin_dir              = self.ini.config['db4e']['bin_dir']
        conf_dir             = self.ini.config['db4e']['conf_dir']
        db4e_dir             = self.ini.config['db4e']['db4e_dir']
        db4e_service_file    = self.ini.config['db4e']['service_file']
        initial_setup_script = self.ini.config['db4e']['setup_script']
        log_dir              = self.ini.config['db4e']['log_dir']
        run_dir              = self.ini.config['db4e']['run_dir']
        systemd_dir          = self.ini.config['db4e']['systemd_dir']
        templates_dir        = self.ini.config['db4e']['template_dir']
        p2pool_binary        = self.ini.config['p2pool']['process']
        p2pool_service_file  = self.ini.config['p2pool']['service_file']
        p2pool_start_script  = self.ini.config['p2pool']['start_script']
        p2pool_socket_file   = self.ini.config['p2pool']['socket_file']
        p2pool_version       = self.ini.config['p2pool']['version']
        blockchain_dir       = self.ini.config['monerod']['blockchain_dir']
        monerod_binary       = self.ini.config['monerod']['process']
        monerod_service_file = self.ini.config['monerod']['service_file']
        monerod_socket_file  = self.ini.config['monerod']['socket_file']
        monerod_start_script = self.ini.config['monerod']['start_script']
        monerod_version      = self.ini.config['monerod']['version']
        xmrig_binary         = self.ini.config['xmrig']['process']
        xmrig_service_file   = self.ini.config['xmrig']['service_file'] 
        xmrig_version        = self.ini.config['xmrig']['version']

        # The db4e user (the account used to run Db4E)
        db4e_user = getpass.getuser()

        # db4e, P2Pool, Monero daemon and XMRig directories
        db4e_vendor_dir = 'db4e'
        p2pool_dir = 'p2pool-' + str(p2pool_version)
        monerod_dir = 'monerod-' + str(monerod_version)
        xmrig_dir = 'xmrig-' + str(xmrig_version)

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
        fq_db4e_service_file    = os.path.join(tmpl_dir, 'db4e', systemd_dir, db4e_service_file)
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
        tmp_dir = os.path.join('/tmp', 'db4e')
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        os.mkdir(tmp_dir)

        # Update the db4e service template with deployment values
        fq_db4e_dir = os.path.join(vendor_dir, )
        placeholders = {
            'DB4E_USER': db4e_user,
            'DB4E_GROUP': db4e_group,
            'DB4E_DIR': fq_db4e_dir,
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
            'P2POOL_DIR': fq_p2pool_dir,
            'DB4E_USER': db4e_user,
            'DB4E_GROUP': db4e_group,
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
            'MONEROD_DIR': fq_monerod_dir,
            'DB4E_USER': db4e_user,
            'DB4E_GROUP': db4e_group,
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
            'XMRIG_DIR': fq_xmrig_dir,
            'DB4E_USER': db4e_user,
            'DB4E_GROUP': db4e_group,
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
                ['sudo', fq_initial_setup, db4e_dir, db4e_user, db4e_group, vendor_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                input=b"",
                timeout=10)
            stdout = cmd_result.stdout.decode().strip()
            stderr = cmd_result.stderr.decode().strip()

            # Check the return code
            if cmd_result.returncode != 0:
                results.append({'Db4E core': {'status': 'error', 'msg': f'Service install failed.\n\n{stderr}'}})
                return results
            
            installer_output = f'{stdout}'
            results.append({'Db4E core': {'status': 'good', 'msg': installer_output}})
            shutil.rmtree(tmp_dir)

        except Exception as e:
            results.append({'Db4E core': {'status': 'error', 'msg': f'Fatal error: {e}'}})

        # Build the db4e deployment record
        db4e_rec['enable'] = True
        db4e_rec['group'] = db4e_group
        db4e_rec['install_dir'] = db4e_install_dir
        db4e_rec['user'] = db4e_user
        db4e_rec['vendor_dir'] = vendor_dir
        # Update the repo deployment record
        self.depl_mgr.update_deployent(db4e_rec)
        return results
