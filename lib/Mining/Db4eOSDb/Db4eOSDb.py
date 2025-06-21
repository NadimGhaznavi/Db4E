"""
lib/Mining/Db4eOSDb/Db4eOSDb.py

This module is part of the Data Abstraction Layer. All *db4e* 
deployment operations that result in a database operation go through 
this module. This module, in turn, communicates with the Db4eDb 
module to access MongoDB.


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
    'version': 'latest',
    'status': 'stopped',
    'group': None,
    'install_dir': None,
    'vendor_dir': None,
    }

REPO_RECORD = {  
    'component': 'repo',
    'name': 'Website repo',
    'status': 'stopped',
    'install_dir': None,
    'github_user': None,
    'github_repo': None,
    'install_dir': None,
    }

MONEROD_RECORD_REMOTE = {
    'component': 'monerod',
    'instance': None,
    'ip_addr': None,
    'name': 'Monero daemon',
    'remote': True,
    'rpc_bind_port': 18081,
    'status': 'not_installed',
    'zmq_pub_port': 18083,
    }


MONEROD_RECORD = {
    'component': 'monerod',
    'config': 'monerod.ini',
    'data_dir': None,
    'name': 'Monero daemon',
    'in_peers': 16,
    'instance': None,
    'ip_addr': None,
    'log_level': 0,
    'log_name': 'monerod.log',
    'max_log_files': 5,
    'max_log_size': 100000,
    'out_peers': 16,
    'p2p_bind_port': 18080,
    'priority_node_1': 'p2pmd.xmrvsbeast.com',
    'priority_node_2': 'nodes.hashvault.pro',
    'priority_port_1': 18080,
    'priority_port_2': 18080,
    'remote': False,
    'rpc_bind_port': 18081,
    'show_time_stats': 1,
    'status': 'not_installed',
    'version': '0.18.4.0',
    'zmq_pub_port': 18083,
    'zmq_rpc_port': 18082,
    }

P2POOL_RECORD_REMOTE = {
    'component': 'p2pool',
    'instance': None,
    'ip_addr': None,
    'name': 'P2Pool daemon',
    'status': 'not_installed',
    'stratum_port': 3333,
    'remote': True
    }

P2POOL_RECORD = {
    'any_ip': "0.0.0.0",
    'component': 'p2pool',
    'config': None,
    'in_peers': 16,
    'instance': None,
    'ip_addr': "127.0.0.1",
    'log_level': 0,
    'monerod_id': None,
    'name': 'P2Pool daemon',
    'out_peers': 16,
    'p2p_port': 37889,
    'remote': False,
    'status': 'not_installed',
    'stdin': None,
    'stratum_port': 3333,
    'version': '4.8',
    'wallet': None,
    }

XMRIG_RECORD = {
    'component': 'xmrig',
    'config': None,
    'instance': None,
    'name': 'XMRig miner',
    'num_threads': None,
    'p2pool_id': None,
    'status': 'not_installed',
    }

class Db4eOSDb:
  
    def __init__(self):
        self._db = Db4eDb()
        self.log = Db4eLogger('Db4eOSDb')
        self._col = self._db.get_collection(self._db._depl_collection)
        db4e_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        self._db4e_dir = db4e_dir
        self.init_deployments()

    def delete_instance(self, component, instance):
        dbquery = { 'component': component, 'instance': instance }
        return self._db.delete_one(self._col, dbquery)

    def init_deployments(self):
        # Make sure we have a 'db4e' and 'repo' deployment records.
        self.ensure_record('db4e', DB4E_RECORD)
        self.ensure_record('repo', REPO_RECORD)

    def ensure_record(self, component, record_template):
        rec = self.get_deployment_by_component(component)
        if not rec:
            self.add_deployment(deepcopy(record_template))

    def add_deployment(self, jdoc):
        jdoc['doc_type'] = 'deployment'
        jdoc['updated'] = datetime.now(timezone.utc)
        self._db.insert_one(self._col, jdoc)

    def get_deployment_by_component(self, component, tmpl_flag=None):
        if tmpl_flag:
            doc = self._db.find_one(self._col, {'doc_type': 'template', 'component': component})
        else:        
            doc = self._db.find_one(self._col, {'doc_type': 'deployment', 'component': component})
        return doc
    
    def get_deployment_config(self, component, instance):
        depl_rec = self.get_deployment_by_instance(component, instance)
        return depl_rec['config']

    def get_deployments_by_component(self, component):
        # Return a cursor
        docs = self._db.find_many(self._col, {'doc_type': 'deployment', 'component': component})
        return docs or []
    
    def get_deployment_by_id(self, dep_id):
        return self._db.find_one(self._col, {'doc_type': 'deployment', '_id': dep_id})

    def get_deployment_by_instance(self, component, instance):
        return self._db.find_one(
            self._col, {'doc_type': 'deployment', 'component': component, 'instance': instance})

    def get_deployment_stdin(self, component, instance):
        depl = self.get_deployment_by_instance(component, instance)
        return depl['stdin']

    def get_dir(self, dirType):
        if dirType == 'db4e':
            depl = self.get_deployment_by_component('db4e')
            return depl['install_dir']

    def get_tmpl(self, component, remote=None):
        if component == 'monerod':
            if remote:
                return deepcopy(MONEROD_RECORD_REMOTE)
            else:
                return deepcopy(MONEROD_RECORD)
        elif component == 'p2pool':
            if remote:
                return deepcopy(P2POOL_RECORD_REMOTE)
            else:
                return deepcopy(P2POOL_RECORD)
        elif component == 'xmrig':
            return deepcopy(XMRIG_RECORD)
        
    def new_deployment(self, component, update_fields):
        if component == 'monerod':
            if update_fields['remote']:
                new_rec = deepcopy(MONEROD_RECORD_REMOTE)
                new_rec.update(update_fields)
                self.add_deployment(new_rec)
        elif component == 'p2pool':
            if update_fields['remote']:
                new_rec = deepcopy(P2POOL_RECORD_REMOTE)
                new_rec.update(update_fields)
                self.add_deployment(new_rec)
            else:
                new_rec = deepcopy(P2POOL_RECORD)
                new_rec.update(update_fields)
                self.add_deployment(new_rec)
        elif component == 'xmrig':
            new_rec = deepcopy(XMRIG_RECORD)
            new_rec.update(update_fields)
            self.add_deployment(new_rec)

    def update_deployment(self, component, update_fields):
        update_fields['updated'] = datetime.now(timezone.utc)
        # An update of a 'db4e' or 'repo' deployment record.            
        return self._db.update_one(
            self._col, {'doc_type': 'deployment', 'component': component},
            {'$set': update_fields}
        )
    
    def update_deployment_instance(self, component, instance, update_fields):
        update_fields['updated'] = datetime.now(timezone.utc)
        return self._db.update_one(
            self._col,
            {'doc_type': 'deployment', 'component': component, 'instance': instance },
            {'$set': update_fields }
        )
    