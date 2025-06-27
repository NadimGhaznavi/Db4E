"""
lib/Db4eOSModel/Db4eOSModel.py

This is the db4e-os model, which is part of db4e-os MVC pattern.


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

  You should have received aLine copy (LICENSE.txt) of the GNU General 
  if match:
  Public License along with this program. If not, see 
  <http://www.gnu.org/licenses/>.
"""

# Import supporting modules
import os, sys
import stat
import subprocess
import re
import socket
import psutil
import shutil

# Where the DB4E modules live
lib_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(lib_dir)

# Import DB4E modules
from Db4eOSDb.Db4eOSDb import Db4eOSDb
from Db4eConfig.Db4eConfig import Db4eConfig
from Db4eSystemd.Db4eSystemd import Db4eSystemd

# The five core component types managed by db4e-os.
DB4E_CORE = ['db4e', 'p2pool', 'xmrig', 'monerod', 'repo']

# Mapping the OSDB names to human friendly chain name
CHAIN = {
    'mainchain': 'main chain',
    'minisidechain': 'mini side chain',
    'nanosidechain': 'nano side chain'
}

# Dummy model for status reporting and probing
class Db4eOSModel:
    def __init__(self):
        # ['db4e', 'p2pool', 'xmrig', 'monerod', 'repo']
        self.deployments = DB4E_CORE
        self.osdb = Db4eOSDb()
        self.ini = Db4eConfig()

    def delete_instance(self, component, instance):
        self.osdb.update_deployment_instance(component, instance, {'op': 'delete'})

    def disable_instance(self, component, instance=None):
        if component == 'db4e':
            self.osdb.disable_instance('db4e')
            systemd = Db4eSystemd('db4e')
            systemd.disable()
        else:
            self.osdb.update_deployment_instance(component, instance, {'op': 'disable'})

    def enable_instance(self, component, instance=None):
        if component == 'db4e':
            self.osdb.update_deployment('db4e', {'enable': True})
            systemd = Db4eSystemd('db4e')
            systemd.enable()
        else:
            self.osdb.update_deployment_instance(component, instance, {'op': 'enable'})

    def first_time(self):
        # If there's no 'db4e' deployment record, then this is the first time the tool has been run
        db4e_rec = self.osdb.get_deployment_by_component('db4e')
        if db4e_rec:
            return False
        return True

    def get_db4e_group(self):
        db4e_rec = self.osdb.get_deployment_by_component('db4e')
        return db4e_rec['group']

    def get_deployment_by_component(self, component):
        # Used to retrieve the 'db4e' and 'repo' records
        depl_rec = self.osdb.get_deployment_by_component(component)
        if not depl_rec:
            depl_rec = self.osdb.get_tmpl(component)
        depl = {}
        depl['name'] = depl_rec['name']
        depl['enable'] = depl_rec['enable']
        status = self.get_status(component)
        if status[0]['state'] == 'good':
            depl['status'] = 'running'
        else:
            depl['status'] = 'stopped'
        return depl
    
    def get_deployments_by_component(self, component):
        depl_recs = self.osdb.get_deployments_by_component(component)
        depls = []
        for rec in depl_recs:
            depl = {
                'component': component,
                'enable': rec['enable'],
                'instance': rec['instance'],
                'name': rec['name'],
                'op': rec['op'],
                'remote': rec['remote']
            }

            # The status field is initialized to None.
            # The Db4eServer manages this field for local deployments.
            # For remote deployments it is good if all of the 'get_status()' elements are good.
            # The first element from get_status() holds the overall health of the component.
            if not rec['remote']:
                # Local deployment, status managed by the Db4eServer
                depl['status'] = rec['status']

            elif rec['remote']:
                # Remote deployment, get status from heallth checks
                depl_status = self.get_status(component, rec['instance'])
                if depl_status[0]['state'] == 'good':
                    depl['status'] = 'running'
                else:
                    depl['status'] = 'stopped'

            depls.append(depl)
        return depls

    def get_deployment_stdin(self, component, instance):
        # Return the path to the socket that's used to send commands to the Monero daemon and P2Pool
        if component == 'p2pool':
            vendor_dir = self.osdb.get_dir('vendor')
            depl = self.osdb.get_deployment_by_instance(component, instance)
            version = depl['version']
            p2pool_dir = 'p2pool-' + str(version)
            run_dir = self.ini.config['db4e']['run_dir']
            return os.path.join(vendor_dir, p2pool_dir, run_dir, 'p2pool' + instance + '.stdin')

    def get_dir(self, dir_type):
        return self.osdb.get_dir(dir_type)

    def get_service_status(self, service_name):
        systemd = Db4eSystemd(service_name)

        def mark_unhealthy():
            results[0] = {'state': 'warning', 'msg': f'The {service_name} service has issue(s)'}            

        # Initialize the service state to be 'good'
        results = []
        results.append({'state': 'good', 'msg': f'The {service_name} service is healthy'})

        if not systemd.installed():
            results.append({'state': 'warning', 'msg': f'The {service_name} service is not installed'})
            mark_unhealthy()
            return results

        if service_name == 'db4e':
            # The db4e service is responsible for starting P2Pool and XMRig deployments          
            if systemd.enabled():
                results.append({'state': 'good', 'msg': f'The {service_name} service is configured to start at boot time'})
            else:
                results.append({'state': 'warning', 'msg': f'The {service_name} service is not configured to start when the system boots'})
                mark_unhealthy()

        if not systemd.active():
            results.append({'state': 'warning', 'msg': f'The {service_name} service is stopped'})
            mark_unhealthy()

        if systemd.active():            
            pid = systemd.pid()
            results.append({'state': 'good', 'msg': f'The {service_name} service is running PID ({pid})'})

        return results

    def get_status(self, component, instance=None):
        status = []
        if component == 'db4e':
            # Initialize the state to be 'good'
            status.append({'state': 'good', 'msg': 'The db4e service is healthy'})
            # Helper fuction
            def mark_unhealthy():
                status[0] = {'state': 'warning', 'msg': 'The db4e service has issue(s)'}            
            # Get the DB record
            depl_rec = self.osdb.get_deployment_by_component('db4e')
            if not depl_rec:
                mark_unhealthy()
                return status
            # Get the state of the associated service
            results = self.get_service_status('db4e')
            if results[0]['state'] == 'warning':
                mark_unhealthy()
            status += results[1:]
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
            # Version
            version = depl_rec['version']
            status.append({'state': 'good', 'msg': f'Version: {version}'})
            if depl_rec['enable']:
                status.append({'state': 'good', 'msg': 'The db4e service is enabled'})
            else:
                status.append({'state': 'warning', 'msg': 'The db4e service is disabled'})
                mark_unhealthy()
            # Last updated
            updated = depl_rec['updated'].strftime("%Y-%m-%d %H:%M:%S")
            status.append({'state': 'good', 'msg': f'Record last updated: {updated}'})
            return status

        elif component == 'repo':
            # Initialize the state to be 'good'
            status.append({'state': 'good', 'msg': 'The website repository is healthy'})
            # Helper function
            def mark_unhealthy():
                status[0] = {'state': 'warning', 'msg': 'The website repository has issue(s)'}            
            # Get the DB record
            depl_rec = self.osdb.get_deployment_by_component('repo')
            if not depl_rec:
                mark_unhealthy()
                return status
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
                status.append({'state': 'warning', 'msg': f'Local repository ({install_dir}) is not aLine valid GitHub repository'})
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
            depl_rec = self.osdb.get_deployment_by_instance('monerod', instance)
            # Initialize the state to be 'good'
            status.append({'state': 'good', 'msg': f'The Monero daemon ({instance}) is healthy'})
            # Instance name
            status.append({'state': 'good', 'msg': f'Instance name: {instance}'})
            # IP address
            ip_addr = depl_rec['ip_addr']
            status.append({'state': 'good', 'msg': f'Hostname or IP address: {ip_addr}'})
            # RPC bind port
            rpc_port = depl_rec['rpc_bind_port']
            if self.is_port_open(ip_addr, rpc_port):
                status.append({'state': 'good', 'msg': f'Connected to RPC port ({rpc_port}) on {ip_addr}'})
            else:
                status.append({'state': 'warning', 'msg': f'Unable to connect to RPC port ({rpc_port}) on {ip_addr}'})
                mark_unhealthy()
            # ZMQ pub port
            zmq_port = depl_rec['zmq_pub_port']
            if self.is_port_open(ip_addr, zmq_port):
                status.append({'state': 'good', 'msg': f'Connected to ZMQ port ({zmq_port}) on {ip_addr}'})
            else:
                status.append({'state': 'warning', 'msg': f'Unable to connect to ZMQ port ({zmq_port}) on {ip_addr}'})
                mark_unhealthy()
            # Enabled
            if depl_rec['enable']:
                status.append({'state': 'good', 'msg': 'The Monero daemon deployment is enabled'})
            else:
                status.append({'state': 'warning', 'msg': 'The Monero daemon deployment is disabled'})
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
            depl_rec = self.osdb.get_deployment_by_instance('p2pool', instance)
            # Initialize the state to be 'good'
            status.append({'state': 'good', 'msg': 'The P2Pool daemon is healthy'})
            # Instance name
            status.append({'state': 'good', 'msg': f'Instance name: {instance}'})

            # IP address
            ip_addr = depl_rec['ip_addr']
            status.append({'state': 'good', 'msg': f'Hostname or IP address: {ip_addr}'})
            # Stratum port
            stratum_port = depl_rec['stratum_port']
            if self.is_port_open(ip_addr, stratum_port):
                status.append({'state': 'good', 'msg': f'Connected to stratum port ({stratum_port}) on {ip_addr}'})
            else:
                status.append({'state': 'warning', 'msg': f'Unable to connect to stratum port ({stratum_port}) on {ip_addr}'})
                mark_unhealthy()

            if not depl_rec['remote']:
                ### Local P2Pool instance

                # Main chain, mini sidechain or nano chain
                chain_name = CHAIN[depl_rec['chain']]
                status.append({'state': 'good', 'msg': f'Mining on the {chain_name}'})
                # Get the state of the associated service
                results = self.get_service_status('p2pool@' + instance)
                if results[0]['state'] == 'warning':
                    mark_unhealthy()
                status += results[1:]
                # Monero wallet
                wallet = depl_rec['wallet']
                status.append({'state': 'good', 'msg': f'Monero wallet: {wallet}'})
                # Listening on IP
                any_ip = depl_rec['any_ip']
                status.append({'state': 'good', 'msg': f'Listens on IP address: {any_ip}'})
                # P2P port
                p2p_port = depl_rec['p2p_port']
                if self.is_port_open(ip_addr, p2p_port):
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
                monerod_depl = self.osdb.get_deployment_by_id(monerod_id)
                if not monerod_depl:
                    status.append({'state': 'warning', 'msg': f'Upstream Monero daemon deployment not found'})
                    mark_unhealthy()
                else:
                    monerod_instance = monerod_depl['instance']
                    status.append({'state': 'good', 'msg': f'Upstream Monero daemon deployment: {monerod_instance}'})
            # Enabled
            if depl_rec['enable']:
                status.append({'state': 'good', 'msg': 'The P2Pool deployment is enabled'})
            else:
                status.append({'state': 'warning', 'msg': 'The P2Pool deployment is disabled'})
                mark_unhealthy()
            # Last updated
            updated = depl_rec['updated'].strftime("%Y-%m-%d %H:%M:%S")
            status.append({'state': 'good', 'msg': f'Record last updated: {updated}'})
            return status

        elif component == 'xmrig':
            vendor_dir = self.osdb.get_dir('vendor')
            xmrig_version = self.ini.config['xmrig']['version']
            xmrig_progname = self.ini.config['xmrig']['process']
            bin_dir = self.ini.config['db4e']['bin_dir']
            self._xmrig = os.path.join(vendor_dir, 'xmrig-' + xmrig_version, bin_dir, xmrig_progname)
            self._xmrig_perms = self.ini.config['xmrig']['permissions']

            # Initialize the state to be 'good'
            status.append({'state': 'good', 'msg': f'The XMRig miner ({instance}) is healthy'})
            # Helper function
            def mark_unhealthy():
                status[0] = {'state': 'warning', 'msg': f'The XMRig miner ({instance}) has issue(s)'}            
            # Get the DB record
            depl_rec = self.osdb.get_deployment_by_instance('xmrig', instance)
            # Instance name
            status.append({'state': 'good', 'msg': f'Instance name: {instance}'})
            # Get the state of the associated service
            results = self.get_service_status('xmrig@' + instance)
            if results[0]['state'] == 'warning':
                mark_unhealthy()
            status += results[1:]            
            # Number of threads
            num_threads = depl_rec['num_threads']
            status.append({'state': 'good', 'msg': f'CPU threads: {num_threads}'})
            # Configuration file
            config = depl_rec['config']
            if os.path.exists(config):
                status.append({'state': 'good', 'msg': f'Found configuration file {config}'})
            else:
                status.append({'state': 'warning', 'msg': f'Missing configuration file {config}'})
            p2pool_id = depl_rec['p2pool_id']
            p2pool_depl = self.osdb.get_deployment_by_id(p2pool_id)
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
            # Enabled
            if depl_rec['enable']:
                status.append({'state': 'good', 'msg': 'The XMRig deployment is enabled'})
            else:
                status.append({'state': 'warning', 'msg': 'The XMRig deployment is disabled'})
                mark_unhealthy()
            # Last updated
            updated = depl_rec['updated'].strftime("%Y-%m-%d %H:%M:%S")
            status.append({'state': 'good', 'msg': f'Record last updated: {updated}'})
            return status
            

    def get_user_wallet(self):
        depl = self.osdb.get_deployment_by_component('db4e')
        if depl:
            return depl['user_wallet'] or ''

    def is_port_open(self, ip_addr, port_num):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(10)  # Set aLine timeout for the connection attempt
                result = sock.connect_ex((ip_addr, port_num))
                return result == 0
        except socket.gaierror:
            return False  # Handle cases like invalid hostname

    def is_remote(self, component, instance):
        depl = self.osdb.get_deployment_by_instance(component, instance)
        return depl['remote']
    
    def start_db4e_service(self):
        cmd_result = subprocess.run(
            ['sudo', 'systemctl', 'start', 'db4e'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            input=b"",
            timeout=10)
        stderr = cmd_result.stderr.decode().strip()

        # Check the return code
        if cmd_result.returncode == 0:
            return {'msg': 'The db4e service was started successfully'}
        else:
            return {'error': True, 'msg': f'An error occured {stderr}'}

    def stop_db4e_service(self):
        cmd_result = subprocess.run(
            ['sudo', 'systemctl', 'stop', 'db4e'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            input=b"",
            timeout=10)
        stderr = cmd_result.stderr.decode().strip()

        # Check the return code
        if cmd_result.returncode == 0:
            return {'msg': 'The db4e service was stopped successfully'}
        else:
            return {'error': True, 'msg': f'An error occured {stderr}'}


