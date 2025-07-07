"""
tests/Constants/test_Templates.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

from db4e.Constants.MongoRecords import (
    Db4E_Record_Template,
    MoneroD_Remote_Record_Template,
    MoneroD_Record_Template,
    P2Pool_Remote_Record_Template,
    P2Pool_Record_Template,
    XMRig_Record_Template    
)

def test_Db4E_Record_Template():
    assert isinstance(Db4E_Record_Template, dict)
    required_keys = ['component', 'donation_wallet', 'enable', 'group', 'install_dir', 'name', 'op',
                     'status', 'updated', 'user', 'user_wallet', 'vendor_dir', 'version']
    for key in required_keys:
        assert key in Db4E_Record_Template

def test_MoneroD_Remote_Record_Template():
    assert isinstance(MoneroD_Remote_Record_Template, dict)
    required_keys = ['component', 'enable', 'instance', 'ip_addr', 'name', 'op', 'remote',
                     'rpc_bind_port', 'status', 'updated', 'zmq_pub_port']
    for key in required_keys:
        assert key in MoneroD_Remote_Record_Template

def test_MoneroD_Record_Template():
    assert isinstance(MoneroD_Record_Template, dict)
    required_keys = ['component', 'config', 'data_dir', 'enable', 'in_peers', 'instance', 'ip_addr',
                     'log_level', 'log_name', 'max_log_files', 'max_log_size', 'name', 'op',
                     'out_peers', 'p2p_bind_port', 'priority_node_1', 'priority_node_2',
                     'priority_port_1', 'priority_port_2', 'remote', 'rpc_bind_port',
                     'show_time_stats', 'status', 'updated', 'version', 'zmq_pub_port', 'zmq_rpc_port']
    for key in required_keys:
        assert key in MoneroD_Record_Template

def test_P2Pool_Remote_Record_Template():
    assert isinstance(P2Pool_Remote_Record_Template, dict)
    required_keys = ['component', 'enable', 'instance', 'ip_addr', 'name', 'op',
                     'remote', 'status', 'stratum_port', 'updated']
    for key in required_keys:
        assert key in P2Pool_Remote_Record_Template

def test_P2Pool_Record_Template():
    assert isinstance(P2Pool_Record_Template, dict)
    required_keys = ['any_ip', 'chain', 'component', 'config', 'enable', 'in_peers', 'instance',
                     'ip_addr', 'log_level', 'monerod_id', 'name', 'op', 'out_peers',
                     'p2p_port', 'remote', 'status', 'stratum_port', 'updated', 'version', 'wallet']
    for key in required_keys:
        assert key in P2Pool_Record_Template

def test_XMRig_Record_Template():
    assert isinstance(XMRig_Record_Template, dict)
    required_keys = ['component', 'config', 'enable', 'instance', 'name', 'num_threads',
                     'op', 'p2pool_id', 'remote', 'status', 'updated', 'version']
    for key in required_keys:
        assert key in XMRig_Record_Template