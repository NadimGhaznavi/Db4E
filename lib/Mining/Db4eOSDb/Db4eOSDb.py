"""
lib/Mining/Db4eOSDb/Db4eOSDb.py

This module is part of the Data Abstraction Layer. All *db4e* 
deployment operations that result in a database operation go through 
this module. This module, in turn, communicates with the Db4eDb 
module to access MongoDB.
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


# Supporting modules
import os, sys
from datetime import datetime, timezone
from copy import deepcopy

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
    lib_dir + 'Infrastructure',
    lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
    sys.path.append(db4e_dir)

from Db4eDb.Db4eDb import Db4eDb 
from Db4eLogger.Db4eLogger import Db4eLogger

DB4E_RECORD = {
    'component': 'db4e',
    'name': 'db4e service',
    'version': '0.15.0-beta',
    'status': 'stopped',
    'install_dir': None,
    }

REPO_RECORD = {  
    'component': 'repo',
    'name': 'Website repo',
    'status': 'not_installed',
    'install_dir': None,
    'github_user': None,
    'github_repo': None,
    'install_dir': None,
}

MONEROD_RECORD = {
    'component': 'monerod',
    'name': 'Monero daemon',
    'version': '0.18.4.0',
    'instance': 'Primary',
    'status': 'not_installed',
    'ip_addr': None,
    'zmq_pub_port': 18083,
    'zmq_rpc_port': 18082,
    'p2p_bind_port': 18080,
    'rpc_bind_port': 18081,
    'out_peers': 16,
    'in_peers': 16,
    'log_level': 0,
    'max_log_files': 5,
    'max_log_size': 100000,
    'log_name': 'monerod.log',
    'show_time_stats': 1,
    'install_dir': None,
    'data_dir': None,
    'priority_node_1': 'p2pmd.xmrvsbeast.com',
    'priority_port_1': 18080,
    'priority_node_2': 'nodes.hashvault.pro',
    'priority_node_2': 18080,
    'bin_dir': 'bin',
    'conf_dir': 'conf',
    'log_dir': 'logs',
    'run_dir': 'run',
    'config': 'monerod.ini'
    }

P2POOL_RECORD = {
    'component': 'p2pool',
    'name': 'P2Pool daemon',
    'version': '4.7',
    'instance': 'N/A',
    'status': 'not_installed',
    'wallet': None,
    'monero_node': None,
    'zmq_port': 18083,
    'rpc_port': 18081,
    'stratum_port': 3339,
    'p2p_port': 38900,
    'log_level': 1,
    'in_peers': 16,
    'out_peers': 16,
    'api_dir': 'api',
    'bin_dir': 'bin',
    'log_dir': 'logs',
    'conf_dir': 'conf',
    'config': 'p2pool.ini'
    }

XMRIG_RECORD = {
    'component': 'xmrig',
    'name': 'XMRig miner',
    'version': '6.22.21',
    'instance': 'N/A',
    'status': 'not_installed',
    'hostname': None,
    'miner': None,
    'install_dir': None,
    'bin_dir': 'bin',
    'conf_dir': 'conf',
    'config': 'config.json'
    }

class Db4eOSDb:
  
    def __init__(self):
        self._db = Db4eDb()
        self.log = Db4eLogger('Db4eOSDb')
        self._col = self._db.get_collection(self._db._depl_collection)
        db4e_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        self._db4e_dir = db4e_dir
        self.init_deployments()

    def init_deployments(self):
        # Make sure we have a 'db4e' deployment record
        self.ensure_record('db4e', DB4E_RECORD)
        self.ensure_record('repo', REPO_RECORD)
        self.ensure_record('p2pool', P2POOL_RECORD)
        self.ensure_record('monerod', MONEROD_RECORD)
        self.ensure_record('xmrig', XMRIG_RECORD)

    def ensure_record(self, component, record_template, tmpl_flag=None):
        if tmpl_flag:
            rec = self.get_deployment_by_component(component, tmpl_flag)    
            if not rec:
                self.add_deployment(deepcopy(record_template, tmpl_flag))
        else:
            rec = self.get_deployment_by_component(component)
            if not rec:
                self.add_deployment(deepcopy(record_template))

    def add_deployment(self, jdoc, tmpl_flag=None):
        if tmpl_flag:
            jdoc['doc_type'] = 'template'
        else:
            jdoc['doc_type'] = 'deployment'
        jdoc['updated'] = datetime.now(timezone.utc)
        self._db.insert_one(self._col, jdoc)

    def get_deployment_by_component(self, component, tmpl_flag=None):
        if tmpl_flag:
            doc = self._db.find_one(self._col, {'doc_type': 'template', 'component': component})
        else:        
            doc = self._db.find_one(self._col, {'doc_type': 'deployment', 'component': component})
        return doc

    def get_deployments_by_component(self, component):
        # Return a cursor
        docs = self._db.find_many(self._col, {'doc_type': 'deployment', 'component': component})
        return docs or []
    
    def get_db4e_deployment(self):
        # Return the db4e deployment doc
        return self.get_deployment_by_component('db4e')
    
    def get_repo_deployment(self):
        # Return the repo deployment doc
        return self.get_deployment_by_component('repo')

    def get_monerod_deployments(self):
        # Return the Monero daemon deployment docs
        return self.get_deployments_by_component('monerod')

    def get_monerod_tmpl(self):
        return self._db.find_one(self._col, {'doc_type': 'template', 'component': 'monerod'})

    def get_p2pool_deployments(self):
        # Return the P2Pool deployment docs
        return self.get_deployments_by_component('p2pool')

    def get_xmrig_deployments(self):
        # Return the xmrig deployment docs
        return self.get_deployments_by_component('xmrig')

    def update_deployment(self, component, update_fields):
        update_fields['updated'] = datetime.now(timezone.utc)
        return self._db.update_one(
            self._col,
            {'doc_type': 'deployment', 'component': component},
            {'$set': update_fields}
        )
    
    def update_deployment_instance(self, component, instance, update_fields):
        update_fields['updated'] = datetime.now(timezone.utc)
        return self._db.update_one(
            self._col,
            {'doc_type': 'deployment', 'component': component, 'instance': instance },
            {'$set': update_fields }
        )
    
    def update_db4e(self, update_fields):
        return self.update_deployment('db4e', update_fields)
    
    def update_repo(self, update_fields):
        return self.update_deployment('repo', update_fields)
    
    def update_monerod(self, update_fields, instance):
        return self.update_deployment_instance('monerod', instance, update_fields)

    def update_p2pool(self, update_fields, instance):
        return self.update_deployment_instance('p2pool', instance, update_fields)

    def update_xmrig(self, update_fields, instance):
        return self.update_deployment_instance('xmrig', instance, update_fields)
