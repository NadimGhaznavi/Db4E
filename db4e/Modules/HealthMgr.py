"""
db4e/Modules/HealthMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

import os
import re
import socket
import ipaddress

from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.Helper import result_row, is_port_open
from db4e.Constants.Fields import(
    CONFIG_FIELD, ERROR_FIELD, GOOD_FIELD, INSTANCE_FIELD, IP_ADDR_FIELD, MONEROD_FIELD,
    RPC_BIND_PORT_FIELD, P2POOL_FIELD, P2POOL_ID_FIELD, STRATUM_PORT_FIELD, WARN_FIELD, 
    XMRIG_FIELD, ZMQ_PUB_PORT_FIELD)
from db4e.Constants.Labels import(
    CONFIG_LABEL, P2POOL_LABEL, RPC_BIND_PORT_LABEL, STRATUM_PORT_LABEL, ZMQ_PUB_PORT_LABEL)

class HealthMgr:

    def __init__(self, depl_mgr: DeploymentMgr):
        self.depl_mgr = depl_mgr

    def check_monerod(self, instance):
        results = []
        overall_state = GOOD_FIELD
        monerod_rec = self.depl_mgr.get_deployment_by_instance(MONEROD_FIELD, instance)
        
        if is_port_open(monerod_rec[IP_ADDR_FIELD], monerod_rec[RPC_BIND_PORT_FIELD]):
            results.append(result_row(
                RPC_BIND_PORT_LABEL, GOOD_FIELD,
                f"Connection to {RPC_BIND_PORT_LABEL} successful"
            ))
        else:
            results.append(result_row(
                RPC_BIND_PORT_LABEL, WARN_FIELD,
                f"Connection to {RPC_BIND_PORT_LABEL} failed"
            ))
            overall_state = WARN_FIELD
        if is_port_open(monerod_rec[IP_ADDR_FIELD], monerod_rec[ZMQ_PUB_PORT_FIELD]):
            results.append(result_row(
                ZMQ_PUB_PORT_LABEL, GOOD_FIELD,
                f"Connection to {ZMQ_PUB_PORT_LABEL} successful"
            ))
        else:
            results.append(result_row(
                ZMQ_PUB_PORT_LABEL, WARN_FIELD,
                f"Connection to {ZMQ_PUB_PORT_LABEL} failed"
            ))
            overall_state = WARN_FIELD
        return (overall_state, results)

    def check_p2pool(self, instance):
        results = []
        overall_state = GOOD_FIELD
        p2pool_rec = self.depl_mgr.get_deployment_by_instance(P2POOL_FIELD, instance)
        
        if is_port_open(p2pool_rec[IP_ADDR_FIELD], p2pool_rec[STRATUM_PORT_FIELD]):
            results.append(result_row(
                STRATUM_PORT_LABEL, GOOD_FIELD,
                f"Connection to {STRATUM_PORT_LABEL} successful"
            ))
        else:
            results.append(result_row(
                STRATUM_PORT_LABEL, WARN_FIELD,
                f"Connection to {STRATUM_PORT_LABEL} failed"
            ))
            overall_state = WARN_FIELD
        return (overall_state, results)
        

    def check_xmrig(self, instance):
        results = []
        overall_state = GOOD_FIELD
        xmrig_rec = self.depl_mgr.get_deployment_by_instance(XMRIG_FIELD, instance)
        
        # Check that the XMRig configuration file exists
        if os.path.exists(xmrig_rec[CONFIG_FIELD]):
            results.append(result_row(
                CONFIG_LABEL, GOOD_FIELD,
                f"{xmrig_rec[CONFIG_FIELD]}"
            ))
        else:
            results.append(result_row(
                CONFIG_LABEL, WARN_FIELD,
                f"Not found: {xmrig_rec[CONFIG_FIELD]}"
            ))
            overall_state = WARN_FIELD

        # Check that upstream P2Pool deployment exists
        p2pool_rec = self.depl_mgr.get_deployment_by_id(xmrig_rec[P2POOL_ID_FIELD])
        if p2pool_rec:
            results.append(result_row(
                P2POOL_LABEL, GOOD_FIELD,
                f"Found upstream P2Pool deployment: {p2pool_rec[INSTANCE_FIELD]}"
            ))
        else:
            results.append(result_row(
                P2POOL_LABEL, ERROR_FIELD,
                f"Missing upstream P2Pool deployment"
            ))
            overall_state = ERROR_FIELD
        # overall_state used in NavPane, results used in XMRig and other panes
        return (overall_state, results)
