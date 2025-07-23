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

from db4e.Modules.Helper import result_row, is_port_open
from db4e.Constants.Fields import(
    CONFIG_FIELD, ERROR_FIELD, GOOD_FIELD, INSTANCE_FIELD, IP_ADDR_FIELD, MONEROD_FIELD,
    RPC_BIND_PORT_FIELD, P2POOL_FIELD, PARENT_ID_FIELD, STRATUM_PORT_FIELD, WARN_FIELD, 
    XMRIG_FIELD, ZMQ_PUB_PORT_FIELD, VENDOR_DIR_FIELD, USER_WALLET_FIELD, DB4E_FIELD)
from db4e.Constants.Labels import(
    CONFIG_LABEL, P2POOL_LABEL, RPC_BIND_PORT_LABEL, STRATUM_PORT_LABEL, 
    ZMQ_PUB_PORT_LABEL, VENDOR_DIR_LABEL, USER_WALLET_LABEL)

hi = "#31b8e6"

class HealthMgr:

    def check(self, component, rec, parent_rec=None):
        if component == DB4E_FIELD:
            return self.check_db4e(rec)
        elif component == MONEROD_FIELD:
            return self.check_monerod(rec)
        elif component == P2POOL_FIELD:
            return self.check_p2pool(rec, parent_rec)
        elif component == XMRIG_FIELD:
            return self.check_xmrig(rec, parent_rec)

    def check_db4e(self, rec):
        print(f"HealthMgr:check_db4e(): rec: {rec}")
        results = []
        overall_state = GOOD_FIELD

        # Example: check if vendor dir exists
        vendor_dir = rec.get(VENDOR_DIR_FIELD, "")

        if vendor_dir == "":
            results.append(result_row(
                f"[bold]{VENDOR_DIR_LABEL}[/]", ERROR_FIELD,
                f"Missing {VENDOR_DIR_LABEL}"
            ))
            overall_state = ERROR_FIELD
        
        elif os.path.isdir(vendor_dir):
            results.append(result_row(
                f"[bold]{VENDOR_DIR_LABEL}[/]", GOOD_FIELD,
                f"{VENDOR_DIR_LABEL} exists: [{hi}]{vendor_dir}"
            ))

        else:
            results.append(result_row(
                f"[bold]{VENDOR_DIR_LABEL}[/]", ERROR_FIELD,
                f"[{hi}]{vendor_dir}[/] not found"
            ))
            overall_state = ERROR_FIELD

        # Example: check if wallet address looks valid
        wallet = rec.get(USER_WALLET_FIELD)
        #if wallet and wallet.startswith("4") and len(wallet) >= 95:
        if wallet:        
            results.append(result_row(
                f"[bold]{USER_WALLET_LABEL}[/]", GOOD_FIELD,
                f"Found wallet address: [{hi}]{wallet[:11]}...[/]"
            ))
        else:
            results.append(result_row(
                USER_WALLET_LABEL, ERROR_FIELD,
                f"Wallet address is missing"
            ))
            if overall_state != ERROR_FIELD:
                overall_state = WARN_FIELD

        print(f"HealthMgr:check_db4e(): overall_state: {overall_state}\n{results}")
        return (overall_state, results)

    def check_monerod(self, rec):
        results = []
        overall_state = GOOD_FIELD
        if is_port_open(rec[IP_ADDR_FIELD], rec[RPC_BIND_PORT_FIELD]):
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
        if is_port_open(rec[IP_ADDR_FIELD], rec[ZMQ_PUB_PORT_FIELD]):
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

    def check_p2pool(self, rec, parent_rec):
        results = []
        overall_state = GOOD_FIELD
        if not rec:
            return(overall_state, results)
        if is_port_open(rec[IP_ADDR_FIELD], rec[STRATUM_PORT_FIELD]):
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
        

    def check_xmrig(self, rec, p2pool_rec):
        results = []
        overall_state = GOOD_FIELD
        # Check that the XMRig configuration file exists
        if os.path.exists(rec[CONFIG_FIELD]):
            results.append(result_row(
                CONFIG_LABEL, GOOD_FIELD,
                f"{rec[CONFIG_FIELD]}"
            ))
        else:
            results.append(result_row(
                CONFIG_LABEL, WARN_FIELD,
                f"Not found: {rec[CONFIG_FIELD]}"
            ))
            overall_state = WARN_FIELD

        # Check that upstream P2Pool deployment exists
        if p2pool_rec:
            results.append(result_row(
                P2POOL_LABEL, GOOD_FIELD,
                f"Found upstream P2Pool deployment: {p2pool_rec[INSTANCE_FIELD]}"
            ))
            p2_overall_state, p2p_results = self.check_p2pool(p2pool_rec[INSTANCE_FIELD])
            if p2_overall_state != GOOD_FIELD:
                results.append(result_row(
                    P2POOL_LABEL, WARN_FIELD,
                    f"Upstream P2Pool deployment ({p2pool_rec[INSTANCE_FIELD]}) has issues..."
                ))
                overall_state = p2_overall_state
                results.extend(p2p_results)
        else:
            results.append(result_row(
                P2POOL_LABEL, ERROR_FIELD,
                f"Missing upstream P2Pool deployment"
            ))
            overall_state = ERROR_FIELD


        # overall_state used in NavPane, results used in XMRig and other panes
        return (overall_state, results)
