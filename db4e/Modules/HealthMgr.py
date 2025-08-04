"""
db4e/Modules/HealthMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

import os
import re
import socket
import ipaddress

from db4e.Modules.Helper import (
    worst_status, result_row, is_port_open, get_component_value)
from db4e.Constants.Fields import(
    CONFIG_FIELD, ERROR_FIELD, GOOD_FIELD, INSTANCE_FIELD, IP_ADDR_FIELD, MONEROD_FIELD,
    RPC_BIND_PORT_FIELD, P2POOL_FIELD, STRATUM_PORT_FIELD, WARN_FIELD,
    XMRIG_FIELD, ZMQ_PUB_PORT_FIELD, VENDOR_DIR_FIELD, USER_WALLET_FIELD, DB4E_FIELD,
    HEALTH_MSGS_FIELD, ELEMENT_TYPE_FIELD, MONEROD_REMOTE_FIELD, P2POOL_REMOTE_FIELD)
from db4e.Constants.Labels import(
    CONFIG_LABEL, P2POOL_LABEL, RPC_BIND_PORT_LABEL, STRATUM_PORT_LABEL, 
    ZMQ_PUB_PORT_LABEL, VENDOR_DIR_LABEL, USER_WALLET_LABEL)

class HealthMgr:

    def check(self, rec, parent_rec=None):
        elem_type = rec.get(ELEMENT_TYPE_FIELD, "")
        #print(f"HealthMgr:check(): elem_type: {elem_type}")
        #print(f"HealthMgr:check(): rec: {rec}")
        #print(f"HealthMgr:check(): elem_type: {elem_type}")

        if elem_type == DB4E_FIELD:
            return self.check_db4e(rec)
        elif elem_type == MONEROD_FIELD:
            return self.check_monerod(rec)
        elif elem_type == MONEROD_REMOTE_FIELD:
            return self.check_monerod_remote(rec)
        elif elem_type == P2POOL_FIELD:
            return self.check_p2pool(rec, parent_rec)
        elif elem_type == P2POOL_REMOTE_FIELD:
            return self.check_p2pool_remote(rec)
        elif elem_type == XMRIG_FIELD:
            return self.check_xmrig(rec, parent_rec)
        else:
            raise ValueError(f"HealthMgr:check(): No handler for {elem_type}")

    def check_db4e(self, rec):
        #print(f"HealthMgr:check_db4e(): rec: {rec}")
        results = []
        vendor_dir = get_component_value(rec, VENDOR_DIR_FIELD)
        if vendor_dir == "":
            results.append(result_row(
                f"{VENDOR_DIR_LABEL}", ERROR_FIELD,
                f"{VENDOR_DIR_LABEL} missing"
            ))
        
        elif os.path.isdir(vendor_dir):
            results.append(result_row(
                f"{VENDOR_DIR_LABEL}", GOOD_FIELD,
                f"{VENDOR_DIR_LABEL} exists: {vendor_dir}"
            ))

        else:
            results.append(result_row(
                f"{VENDOR_DIR_LABEL}", ERROR_FIELD,
                f"{vendor_dir} not found"
            ))

        wallet = get_component_value(rec, USER_WALLET_FIELD)
        # Future sanity check
        #if wallet and wallet.startswith("4") and len(wallet) >= 95:
        if wallet:        
            results.append(result_row(
                f"{USER_WALLET_LABEL}", GOOD_FIELD,
                f"{USER_WALLET_LABEL} exists: {wallet[:11]}..."
            ))
        else:
            results.append(result_row(
                f"{USER_WALLET_LABEL}", ERROR_FIELD,
                f"{USER_WALLET_LABEL} missing"
            ))

        #print(f"HealthMgr:check_db4e(): overall_state: rec:\n{rec}\noverall_state: {overall_state}\n{results}")
        rec[HEALTH_MSGS_FIELD] = results
        return rec

    def check_monerod(self, rec):
        rec[HEALTH_MSGS_FIELD] = []
        return rec

    def check_monerod_remote(self, rec):
        #print(f"HealthMgr:check_monerod_remote(): rec: {rec}")
        results = []
        ip_addr = get_component_value(rec, IP_ADDR_FIELD)
        rpc_bind_port = get_component_value(rec, RPC_BIND_PORT_FIELD)
        zmq_pub_port = get_component_value(rec, ZMQ_PUB_PORT_FIELD)

        if is_port_open(ip_addr, rpc_bind_port):
            results.append(result_row(
                RPC_BIND_PORT_LABEL, GOOD_FIELD,
                f"Connection to {RPC_BIND_PORT_LABEL} successful"
            ))
        else:
            results.append(result_row(
                RPC_BIND_PORT_LABEL, WARN_FIELD,
                f"Connection to {RPC_BIND_PORT_LABEL} failed"
            ))
        if is_port_open(ip_addr, zmq_pub_port):
            results.append(result_row(
                ZMQ_PUB_PORT_LABEL, GOOD_FIELD,
                f"Connection to {ZMQ_PUB_PORT_LABEL} successful"
            ))
        else:
            results.append(result_row(
                ZMQ_PUB_PORT_LABEL, WARN_FIELD,
                f"Connection to {ZMQ_PUB_PORT_LABEL} failed"
            ))
        rec[HEALTH_MSGS_FIELD] = results
        #print(f"HealthMgr:check_monerod_remote(): health_msgs: {rec[HEALTH_MSGS_FIELD]}")
        return rec


    def check_p2pool(self, rec, monerod_rec=None):
        rec[HEALTH_MSGS_FIELD] = []
        return rec

    def check_p2pool_remote(self, rec):
        if not rec:
            raise ValueError("HealthMgr:check_p2pool_remote(): rec is None")

        results = []
        ip_addr = get_component_value(rec, IP_ADDR_FIELD)
        stratum_port = get_component_value(rec, STRATUM_PORT_FIELD)

        if is_port_open(ip_addr, stratum_port):
            results.append(result_row(
                P2POOL_LABEL, GOOD_FIELD,
                f"Connection to {STRATUM_PORT_LABEL} successful"
            ))
        else:
            results.append(result_row(
                P2POOL_LABEL, WARN_FIELD,
                f"Connection to {STRATUM_PORT_LABEL} failed"
            ))
        rec[HEALTH_MSGS_FIELD] = results
        return rec
        

    def check_xmrig(self, rec, p2pool_rec):
        rec[HEALTH_MSGS_FIELD] = []
        #print(f"HealthMgr:check_xmrig(): p2pool_rec: {p2pool_rec}")
        results = []
        config_file = get_component_value(rec, CONFIG_FIELD)

        # Check that the XMRig configuration file exists
        if os.path.exists(config_file):
            results.append(result_row(
                CONFIG_LABEL, GOOD_FIELD,
                f"Found: {config_file}"
            ))
        elif not config_file:
            results.append(result_row(
                CONFIG_LABEL, WARN_FIELD,
                f"Missing"
            ))
        else:
            results.append(result_row(
                CONFIG_LABEL, WARN_FIELD,
                f"Not found: {config_file}"
            ))

        # Check that upstream P2Pool deployment exists
        p2pool_results = []
        if p2pool_rec:
            p2pool_instance = get_component_value(p2pool_rec, INSTANCE_FIELD)
            # See if it's healthy
            p2pool_rec = self.check_p2pool_remote(p2pool_rec)
            p2pool_status = worst_status(p2pool_rec[HEALTH_MSGS_FIELD])
            if p2pool_status != GOOD_FIELD:
                p2pool_results.append(result_row(
                    P2POOL_LABEL, WARN_FIELD,
                    f"Upstream {P2POOL_LABEL} ({p2pool_instance}) has issues"))
                p2pool_results +=p2pool_rec[HEALTH_MSGS_FIELD]
            else:
                p2pool_results.append(result_row(
                    P2POOL_LABEL, GOOD_FIELD,
                    f"Upstream {P2POOL_LABEL} ({p2pool_instance}) is healthy"))
                p2pool_results += p2pool_rec[HEALTH_MSGS_FIELD]

        # overall_state used in NavPane, results used in XMRig and other panes
        results += p2pool_results
        rec[HEALTH_MSGS_FIELD] = results
        return rec
