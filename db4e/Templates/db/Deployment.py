"""
db4e/Templates/db/Deployment.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0

This module contains templates for the Mongo deployment record types.
"""

DB4E_RECORD = {
    'component': 'db4e',
    'donation_wallet': '48aTDJfRH2JLcKW2fz4m9HJeLLVK5rMo1bKiNHFc43Ht2e2kPVh2tmk3Md7npz1WsSU7bpgtX2Xnf59RHCLUEaHfQHwao4j',
    'enable': None,
    'group': None,
    'install_dir': None,
    'name': 'db4e service',
    'op': None,
    'status': None,
    'updated': None,
    'user': None,
    'user_wallet': None,
    'vendor_dir': None,
    'version': None,
    }

MONEROD_RECORD_REMOTE = {
    'component': 'monerod',
    'enable': None,
    'instance': None,
    'ip_addr': None,
    'name': 'Monero daemon',
    'op': None,
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
    'op': None,
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
    'version': None,
    'zmq_pub_port': 18083,
    'zmq_rpc_port': 18082,
    }

P2POOL_RECORD_REMOTE = {
    'component': 'p2pool',
    'enable': None,
    'instance': None,
    'ip_addr': None,
    'name': 'P2Pool daemon',
    'op': None,
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
    'op': None,
    'out_peers': 16,
    'p2p_port': 37889,
    'remote': False,
    'status': 'stopped',
    'stratum_port': 3333,
    'updated': None,
    'version': None,
    'wallet': None,
    }

XMRIG_RECORD = {
    'component': 'xmrig',
    'config': None,
    'enable': None,
    'instance': None,
    'name': 'XMRig miner',
    'num_threads': None,
    'op': None,
    'p2pool_id': None,
    'remote': False,
    'status': 'stopped',
    'updated': None,
    'version': None,
    }
