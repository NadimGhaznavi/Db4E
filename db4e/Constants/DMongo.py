"""
db4e/Constants/DMongo.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Modules.ConstGroup import ConstGroup
from db4e.Constants.DField import DField

###############################################################
#                                                             #
#  CAUTION: Changes here will result in Mongo schema changes  #
#                                                             #
#       You will likely break historical reporting!           #
#                                                             #
###############################################################


class DMongo(ConstGroup):
    CHAIN : str = "chain"
    COLLECTION : str = "collection"
    CONFIG : str = "config"
    DB : str = "db"
    DB_NAME : str = "db4e"
    DB4E_REFRESH : str = "db4e_refresh"
    DEPLOYMENT_COL : str = "depl_collection"
    DOC_TYPE : str = "doc_type"
    ELEMENT_TYPE : str = "element_type"
    ENABLED : str = "enabled"
    EVENT : str = "event"
    HASHRATE : str = "hashrate"
    INSTANCE : str = "instance"
    IP_ADDR : str = "ip_addr"
    JOBS_COLLECTION : str = "jobs_collection"
    LOG_COLLECTION : str = "log_collection"
    METRICS_COLLECTION : str = "metrics_collection"
    MINER : str = "miner"
    MINERS : str = "miners"
    OBJECT_ID : str = DField.OBJECT_ID
    OPS_COLLECTION: str = "ops"
    POOL : str = "pool"
    TEMPLATES_COLLECTION : str = "templates"
    TIMESTAMP : str = "timestamp"
    UPTIME : str = "uptime"