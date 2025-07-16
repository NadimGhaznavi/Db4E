"""
db4e/Modules/HealthMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

import os

from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.Helper import result_row
from db4e.Constants.Fields import(
    CONFIG_FIELD, ERROR_FIELD, GOOD_FIELD, INSTANCE_FIELD, P2POOL_FIELD, P2POOL_ID_FIELD, 
    WARN_FIELD, XMRIG_FIELD)
from db4e.Constants.Labels import(
    CONFIG_LABEL, P2POOL_LABEL, XMRIG_LABEL)

class HealthMgr:

    def __init__(self, depl_mgr: DeploymentMgr):
        self.depl_mgr = depl_mgr

    def check_xmrig(self, instance):
        results = []
        state = GOOD_FIELD
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
            state = WARN_FIELD

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
            state = ERROR_FIELD
        return (state, results)
