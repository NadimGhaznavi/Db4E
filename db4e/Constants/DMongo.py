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

# Mongo
class DMongo(ConstGroup):
    COLLECTION : str = "collection"
    CONFIG : str = "config"
    DB : str = "db"
    DB_NAME : str = "db4e"
    DB4E_REFRESH : str = "db4e_refresh"
    DEPLOYMENT_COL : str = "depl_collection"
    DOC_TYPE : str = "doc_type"
    LOG_COLLECTION : str = "log_collection"
    METRICS_COLLECTION : str = "metrics_collection"
    MINER : str = DField.MINER
    OBJECT_ID : str = DField.OBJECT_ID
    TEMPLATES_COLLECTION : str = "templates"
    TIMESTAMP : str = DField.TIMESTAMP