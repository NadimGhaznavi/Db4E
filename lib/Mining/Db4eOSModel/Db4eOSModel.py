"""
lib/Mining/Db4eOSModel.py

This is the db4e-os model, which is part of db4e-os MVC pattern.
"""


"""
  This file is part of *db4e*, the *Database 4 Everything* project
  <https://github.com/NadimGhaznavi/db4e>, developed independently
  by Nadim-Daniel Ghaznavi. Copyright (c) 2024-2025 NadimGhaznavi
  <https://github.com/NadimGhaznavi/db4e>.
 
  This program is free software: you can redistribute it and/or 
  modify it under the terms of the GNU General Public License as 
  published by the Free Software Foundation, version 3.
 
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  General Public License for more details.

  You should have received a copy (LICENSE.txt) of the GNU General 
  Public License along with this program. If not, see 
  <http://www.gnu.org/licenses/>.
"""

# Import supporting modules
import os, sys
import stat
import subprocess
import re

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../lib/"
# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure',
  lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from Db4eOS.Db4eOS import Db4eOS
from Db4eOSDb.Db4eOSDb import Db4eOSDb
from Db4eConfig.Db4eConfig import Db4eConfig

# The five core component types managed by db4e-os.
DB4E_CORE = ['db4e', 'p2pool', 'xmrig', 'monerod', 'repo']

# Dummy model for status reporting and probing
class Db4eOSModel:
    def __init__(self):
        # ['db4e', 'p2pool', 'xmrig', 'monerod', 'repo']
        self.deployments = DB4E_CORE
        self._os = Db4eOS()
        self._db = Db4eOSDb()
        self.ini = Db4eConfig()

    def delete_instance(self, component, instance):
        return self._db.delete_instance(component, instance)

    def get_db4e_deployment(self):
        db4e_rec = self._db.get_db4e_deployment()
        """
        status = self.get_status('db4e')
        if status[0]['state'] == 'good':
            db4e_status = 'running'
        else:
            db4e_status = 'stopped'
        db4e = {
            'name': db4e_rec['name'],
            'status': db4e_status
        }
        return db4e
        """
        return {'name': db4e_rec['name'], 'status': db4e_rec['status']}
    
    def get_db4e_dir(self):
        db4e_rec = self._db.get_db4e_deployment()
        return db4e_rec['install_dir']
    
    def get_monerod_deployment(self, instance):
        return self._db.get_deployment_by_instance('monerod', instance)

    def get_monerod_deployments(self):
        deployments = {}
        for deployment in self._db.get_monerod_deployments():
            name = deployment['name']
            instance = deployment['instance']
            status = self.get_status('monerod', instance)
            if status[0]['state'] == 'good':
                monerod_status = 'running'
            else:
                monerod_status = 'stopped'
            deployments[instance] = { 'name': name, 'status': monerod_status, 'instance': instance }
        return deployments
        
    def get_p2pool_deployments(self):
        deployments = {}
        for deployment in self._db.get_p2pool_deployments():
            name = deployment['name']
            status = None
            remote = deployment['remote']
            instance = deployment['instance']
            if not remote:
                # Check that the P2Pool instance's Monero daemon deployment record exists
                if not self._db.get_deployment_by_id(deployment['monerod_id']):
                    status = 'stopped'
            if status != 'stopped':
                status = self.get_status('p2pool', instance)
                if status[0]['state'] == 'good':
                    p2pool_status = 'running'
                else:
                    p2pool_status = 'stopped'
            deployments[instance] = { 'name': name, 'status': p2pool_status, 'instance': instance }
        return deployments

    def get_p2pool_deployment(self, instance):
        return self._db.get_deployment_by_instance('p2pool', instance)

    def get_p2pool_deployment_by_id(self, p2pool_id):
        return self._db.get_deployment_by_id(p2pool_id)

    def get_repo_deployment(self):
        repo_rec = self._db.get_repo_deployment()
        status = self.get_status('repo')
        if status[0]['state'] == 'good':
            repo_status = 'running'
        else:
            repo_status = 'stopped'

        repo = {
            'name': repo_rec['name'],
            'status': repo_status
        }
        return repo
    
    def get_repo_dir(self):
        repo_rec = self._db.get_repo_deployment()
        return repo_rec['install_dir']
    
    def get_status(self, component, instance=None):
        status = []
        if component == 'db4e':
            # Helper fuction
            def mark_unhealthy():
                status[0] = {'state': 'warning', 'msg': 'The db4e service has issue(s)'}            
            # Get the DB record
            depl_rec = self._db.get_db4e_deployment()
            # Initialize the state to be 'good'
            status.append({'state': 'good', 'msg': 'The db4e service is healthy'})
            # Version
            version = depl_rec['version']
            status.append({'state': 'good', 'msg': f'Version: {version}'})
            # Service status
            cmd_result = subprocess.run(['systemctl', 'status', 'db4e'],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        input='',
                                        timeout=10)
            stdout = cmd_result.stdout.decode().strip()
            stderr = cmd_result.stderr.decode().strip()
            if stderr == 'Unit db4e.service could not be found.':
                status.append({'state': 'warning', 'msg': 'The db4e service is not installed'})
                mark_unhealthy()
            else:
                for aLine in stdout.split('\n'):
                    # Sample: "   Main PID: 28155 (python)"
                    pattern = r"\s*Main PID:\s+(?P<db4e_pid>\d+)\s+\(python\)"
                    match = re.search(pattern, aLine)
                    if match:
                        db4e_pid = match.group('db4e_pid')
                        status.append({'state': 'good', 'msg': f'The db4e service is running (PID {db4e_pid})'})
                    # Sample: "     Active: inactive (dead)"
                    if aLine == '     Active: inactive (dead)':
                        status.append({'state': 'warning', 'msg': 'The db4e service is stopped'})
                        mark_unhealthy()
            # Install directory
            install_dir = depl_rec['install_dir']
            status.append({'state': 'good', 'msg': f'The db4e install directory, {install_dir}, is good'})
            # 3rd party software directory
            vendor_dir = depl_rec['vendor_dir']
            if not vendor_dir:
                status.append({'state': 'warning', 'msg': 'The 3rd party software directory has not been set'})
                mark_unhealthy()
            elif not os.path.exists(vendor_dir):
                status.append({'state': 'warning', 'msg': f'The 3rd party software directory, {vendor_dir})=, does not exist'})
                mark_unhealthy()
            else:
                status.append({'state': 'good', 'msg': f'The 3rd party software directory, {vendor_dir}, is good'})
            # Last updated
            updated = depl_rec['updated'].strftime("%Y-%m-%d %H:%M:%S")
            status.append({'state': 'good', 'msg': f'Record last updated: {updated}'})
            return status

        elif component == 'repo':
            # Helper function
            def mark_unhealthy():
                status[0] = {'state': 'warning', 'msg': 'The website repository has issue(s)'}            
            # Get the DB record
            depl_rec = self._db.get_repo_deployment()
            # Initialize the state to be 'good'
            status.append({'state': 'good', 'msg': 'The website repository is healthy'})
            # GitHub account
            github_user = depl_rec['github_user']
            status.append({'state': 'good', 'msg': f'GitHub account name: {github_user}'})
            # GitHub repository
            github_repo = depl_rec['github_repo']
            status.append({'state': 'good', 'msg': f'GitHub repository name: {github_repo}'})
            # Local repo install directory
            install_dir = depl_rec['install_dir']
            if not install_dir:
                status.append({'state': 'warning', 'msg': f'Local website repository has not been setup'})
                mark_unhealthy()
            elif not os.path.exists(install_dir):
                status.append({'state': 'warning', 'msg': f'Local repository ({install_dir}) not found'})
                mark_unhealthy()
            elif not os.path.exists(os.path.join(install_dir, '.git')):
                status.append({'state': 'warning', 'msg': f'Local repository ({install_dir}) is not a valid GitHub repository'})
                mark_unhealthy()
            else:
                status.append({'state': 'good', 'msg': f'Local path to repository: {install_dir}'})
            # Last updated
            updated = depl_rec['updated'].strftime("%Y-%m-%d %H:%M:%S")
            status.append({'state': 'good', 'msg': f'Record last updated: {updated}'})
            return status
        
        elif component == 'monerod':
            # Helper function
            def mark_unhealthy():
                status[0] = {'state': 'warning', 'msg': f'The Monero daemon ({instance}) has issue(s)'}            
            # Get the DB record
            depl_rec = self._db.get_deployment_by_instance('monerod', instance)
            # Initialize the state to be 'good'
            status.append({'state': 'good', 'msg': 'The website repository is healthy'})
            # Instance name
            status.append({'state': 'good', 'msg': f'Instance name: {instance}'})
            # IP address
            ip_addr = depl_rec['ip_addr']
            status.append({'state': 'good', 'msg': f'Hostname or IP address: {ip_addr}'})
            # RPC bind port
            rpc_port = depl_rec['rpc_bind_port']
            if self._os.is_port_open(ip_addr, rpc_port):
                status.append({'state': 'good', 'msg': f'Connected to RPC port ({rpc_port}) on {ip_addr}'})
            else:
                status.append({'state': 'warning', 'msg': f'Unable to connect to RPC port ({rpc_port}) on {ip_addr}'})
                mark_unhealthy()
            # ZMQ pub port
            zmq_port = depl_rec['zmq_pub_port']
            if self._os.is_port_open(ip_addr, zmq_port):
                status.append({'state': 'good', 'msg': f'Connected to ZMQ port ({zmq_port}) on {ip_addr}'})
            else:
                status.append({'state': 'warning', 'msg': f'Unable to connect to ZMQ port ({zmq_port}) on {ip_addr}'})
                mark_unhealthy()
            # Last updated
            updated = depl_rec['updated'].strftime("%Y-%m-%d %H:%M:%S")
            status.append({'state': 'good', 'msg': f'Record last updated: {updated}'})
            return status            

        elif component == 'p2pool':
            # Helper function
            def mark_unhealthy():
                status[0] = {'state': 'warning', 'msg': f'The P2Pool daemon ({instance}) has issue(s)'}            
            # Get the DB record
            depl_rec = self._db.get_deployment_by_instance('p2pool', instance)
            # Initialize the state to be 'good'
            status.append({'state': 'good', 'msg': 'The website repository is healthy'})
            # Instance name
            status.append({'state': 'good', 'msg': f'Instance name: {instance}'})
            # IP address
            ip_addr = depl_rec['ip_addr']
            status.append({'state': 'good', 'msg': f'Hostname or IP address: {ip_addr}'})
            # Stratum port
            stratum_port = depl_rec['stratum_port']
            if self._os.is_port_open(ip_addr, stratum_port):
                status.append({'state': 'good', 'msg': f'Connected to stratum port ({stratum_port}) on {ip_addr}'})
            else:
                status.append({'state': 'warning', 'msg': f'Unable to connect to stratum port ({stratum_port}) on {ip_addr}'})
                mark_unhealthy()
            ## Local P2Pool instance
            if not depl_rec['remote']:
                # Monero wallet
                wallet = depl_rec['wallet']
                status.append({'state': 'good', 'msg': f'Monero wallet: {wallet}'})
                # Listening on IP
                any_ip = depl_rec['any_ip']
                status.append({'state': 'good', 'msg': f'Listens on IP address: {any_ip}'})
                # P2P port
                p2p_port = depl_rec['p2p_port']
                if self._os.is_port_open(ip_addr, p2p_port):
                    status.append({'state': 'good', 'msg': f'Connected to P2P port ({p2p_port}) on {ip_addr}'})
                else:
                    status.append({'state': 'warning', 'msg': f'Unable to connect to P2P port ({p2p_port}) on {ip_addr}'})
                    mark_unhealthy()
                # Log level
                log_level = depl_rec['log_level']
                status.append({'state': 'good', 'msg': f'Log level: {log_level}'})
                # Configuration file
                config = depl_rec['config']
                if os.path.exists(config):
                    status.append({'state': 'good', 'msg': f'Configuration file: {config}'})
                else:
                    status.append({'state': 'warning', 'msg': f'Unable to find configuration file: {config}'})
                    mark_unhealthy()
            # Connections
                in_peers = depl_rec['in_peers']
                status.append({'state': 'good', 'msg': f'Allowed incoming connections: {in_peers}'})
                out_peers = depl_rec['out_peers']
                status.append({'state': 'good', 'msg': f'Allowed outbound connections: {out_peers}'})
                # Version
                version = depl_rec['version']
                status.append({'state': 'good', 'msg': f'P2Pool version: {version}'})
                # Monero daemon this P2Pool is using
                monerod_id = depl_rec['monerod_id']
                monerod_depl = self._db.get_deployment_by_id(monerod_id)
                if not monerod_depl:
                    status.append({'state': 'warning', 'msg': f'Upstream Monero daemon deployment not found'})
                    mark_unhealthy()
                else:
                    monerod_instance = monerod_depl['instance']
                    status.append({'state': 'good', 'msg': f'Upstream Monero daemon deployment: {monerod_instance}'})
            # Last updated
            updated = depl_rec['updated'].strftime("%Y-%m-%d %H:%M:%S")
            status.append({'state': 'good', 'msg': f'Record last updated: {updated}'})
            return status

        elif component == 'xmrig':
            vendor_dir = self._db.get_vendor_dir()
            xmrig_version = self.ini.config['xmrig']['version']
            xmrig_progname = self.ini.config['xmrig']['process']
            bin_dir = self.ini.config['db4e']['bin_dir']
            self._xmrig = os.path.join(vendor_dir, 'xmrig-' + xmrig_version, bin_dir, xmrig_progname)
            self._xmrig_perms = self.ini.config['xmrig']['permissions']

            # Helper function
            def mark_unhealthy():
                status[0] = {'state': 'warning', 'msg': f'The XMRig miner ({instance}) has issue(s)'}            
                mark_unhealthy()
            # Get the DB record
            depl_rec = self._db.get_deployment_by_instance('xmrig', instance)
            # Initialize the state to be 'good'
            status.append({'state': 'good', 'msg': f'The XMRig miner ({instance}) is healthy'})
            # Instance name
            status.append({'state': 'good', 'msg': f'Instance name: {instance}'})
            # Number of threads
            num_threads = depl_rec['num_threads']
            status.append({'state': 'good', 'msg': f'CPU threads: {num_threads}'})
            p2pool_id = depl_rec['p2pool_id']
            p2pool_depl = self._db.get_deployment_by_id(p2pool_id)
            if not p2pool_depl:
                status.append({'state': 'warning', 'msg': f'Upstream P2Pool daemon deployment not found'})    
                mark_unhealthy()
            else:
                p2pool_instance = p2pool_depl['instance']
                status.append({'state': 'good', 'msg': f'Upstream P2Pool daemon deployment: {p2pool_instance}'})
            # Check the permissions of the xmrig binary
            xmrig_info = os.stat(self._xmrig)
            permissions = stat.filemode(xmrig_info.st_mode)
            if permissions == self._xmrig_perms:
                status.append({'state': 'good', 'msg': f'File permissions ({permissions}) on xmrig ({self._xmrig}) are good'})
            else:
                status.append({'state': 'warning', 'msg': f'File permissions ({permissions}) on xmrig ({self._xmrig}) are wrong, should be {self._xmrig_perms}'})                
            return status

    def get_vendor_dir(self):
        # Return the 'vendor dir' where the vendor config and other supporting
        # files are installed (log dir, run dir, startup scripts etc.)
        depl = self._db.get_db4e_deployment()
        return depl['vendor_dir']

    def get_xmrig_deployment(self, instance):
        return self._db.get_deployment_by_instance('xmrig', instance)

    def get_xmrig_deployments(self):
        deployments = {}
        for deployment in self._db.get_xmrig_deployments():
            name = deployment['name']
            instance = deployment['instance']
            status = self.get_status('xmrig', instance)
            if status[0]['state'] == 'good':
                xmrig_status = 'running'
            else:
                xmrig_status = 'stopped'
            deployments[instance] = { 'name': name, 'status': xmrig_status, 'instance': instance }
        return deployments
    
    def is_remote(self, component, instance):
        depl = self._db.get_deployment_by_instance(component, instance)
        return depl['remote']

    def update_db4e(self, update_fields):
        self._db.update_db4e(update_fields)

    def update_repo(self, update_fields):
        self._db.update_repo(update_fields)

    def update_monerod(self, update_fields, instance):
        self._db.update_monerod(update_fields, instance)

    def update_p2pool(self, update_fields, instance):
        self._db.update_p2pool(update_fields, instance)

    def update_xmrig(self, update_fields, instance):
        self._db.update_xmrig(update_fields, instance)