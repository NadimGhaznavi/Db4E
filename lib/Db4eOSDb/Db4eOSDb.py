"""
lib/Db4eOSDb/Db4eOSDb.py

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
lib_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(lib_dir)

# Import DB4E modules
from Db4eDb.Db4eDb import Db4eDb 
from Db4eLogger.Db4eLogger import Db4eLogger

DB4E_RECORD = {
    'component': 'db4e',
    'donation_wallet': '48aTDJfRH2JLcKW2fz4m9HJeLLVK5rMo1bKiNHFc43Ht2e2kPVh2tmk3Md7npz1WsSU7bpgtX2Xnf59RHCLUEaHfQHwao4j',
    'enable': None,
    'group': None,
    'install_dir': None,
    'name': 'db4e service',
    'status': None,
    'updated': None,
    'user': None,
    'user_wallet': None,
    'vendor_dir': None,
    'version': 'latest',
    'website_dir': None,
    }

REPO_RECORD = {  
    'component': 'repo',
    'enable': None,
    'github_repo': None,
    'github_user': None,
    'install_dir': None,
    'name': 'Website repo',
    'status': None,
    'updated': None,
    }

MONEROD_RECORD_REMOTE = {
    'component': 'monerod',
    'enable': None,
    'instance': None,
    'ip_addr': None,
    'name': 'Monero daemon',
    'remote': True,
    'rpc_bind_port': 18081,
    'status': None,
    'updated': None,
    'zmq_pub_port': 18083,
    }


MONEROD_RECORD = {
    'component': 'monerod',
    'config': 'monerod.ini',
    'data_dir': None,
    'enable': None,
    'in_peers': 16,
    'instance': None,
    'ip_addr': None,
    'log_level': 0,
    'log_name': 'monerod.log',
    'max_log_files': 5,
    'max_log_size': 100000,
    'name': 'Monero daemon',
    'out_peers': 16,
    'p2p_bind_port': 18080,
    'priority_node_1': 'p2pmd.xmrvsbeast.com',
    'priority_node_2': 'nodes.hashvault.pro',
    'priority_port_1': 18080,
    'priority_port_2': 18080,
    'remote': False,
    'rpc_bind_port': 18081,
    'show_time_stats': 1,
    'status': None,
    'updated': None,
    'version': '0.18.4.0',
    'zmq_pub_port': 18083,
    'zmq_rpc_port': 18082,
    }

P2POOL_RECORD_REMOTE = {
    'component': 'p2pool',
    'enable': None,
    'instance': None,
    'ip_addr': None,
    'name': 'P2Pool daemon',
    'remote': True,
    'status': None,
    'stratum_port': 3333,
    'updated': None,
    }

P2POOL_RECORD = {
    'any_ip': "0.0.0.0",
    'chain': None,
    'component': 'p2pool',
    'config': None,
    'enable': None,
    'in_peers': 16,
    'instance': None,
    'ip_addr': "127.0.0.1",
    'log_level': 0,
    'monerod_id': None,
    'name': 'P2Pool daemon',
    'out_peers': 16,
    'p2p_port': 37889,
    'remote': False,
    'status': None,
    'stratum_port': 3333,
    'updated': None,
    'version': '4.8',
    'wallet': None,
    }

XMRIG_RECORD = {
    'component': 'xmrig',
    'config': None,
    'enable': None,
    'instance': None,
    'name': 'XMRig miner',
    'num_threads': None,
    'p2pool_id': None,
    'status': None,
    'updated': None,
    }

class Db4eOSDb:
  
    def __init__(self):
        self._db = Db4eDb()
        self.log = Db4eLogger('Db4eOSDb')
        self._col = self._db.get_collection(self._db._depl_collection)
        db4e_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        self._db4e_dir = db4e_dir

    def delete_instance(self, component, instance):
        dbquery = { 'component': component, 'instance': instance }
        return self._db.delete_one(self._col, dbquery)

    def disable_instance(self, component, instance):
        self.update_deployment_instance(component, instance, {'enable': False})

    def add_deployment(self, jdoc):
        jdoc['doc_type'] = 'deployment'
        jdoc['updated'] = datetime.now(timezone.utc)
        self._db.insert_one(self._col, jdoc)

    def enable_instance(self, component, instance):
        self.update_deployment_instance(component, instance, {'enable': True})

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
    
    def get_deployment_by_id(self, dep_id):
        return self._db.find_one(self._col, {'doc_type': 'deployment', '_id': dep_id})

    def get_deployment_by_instance(self, component, instance):
        return self._db.find_one(
            self._col, {'doc_type': 'deployment', 'component': component, 'instance': instance})

    def get_deployment_config(self, component, instance):
        depl_rec = self.get_deployment_by_instance(component, instance)
        return depl_rec['config']

    def get_deployment_stdin(self, component, instance):
        depl = self.get_deployment_by_instance(component, instance)
        return depl['stdin']

    def get_dir(self, dirType):
        depl = self.get_deployment_by_component('db4e')
        if dirType == 'db4e':
            return depl['install_dir']
        elif dirType == 'vendor':
            return depl['vendor_dir']
        elif dirType == 'website':
            return depl['website_dir']

    def get_tmpl(self, component, remote=None):
        if component == 'db4e':
            return deepcopy(DB4E_RECORD)
        elif component == 'monerod':
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
    