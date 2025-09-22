"""
Modules/MiningETL.py

Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from datetime import datetime

from db4e.Constants.DMongo import DMongo
from db4e.Constants.DMining import DMining

from db4e.Modules.MiningDb import MiningDb




class MiningETL:


    def __init__(self, mining_db: MiningDb):
        self.mining_db = mining_db

    
    def get_chain_hashrates(self, chain):
        recs = self.mining_db.get_chain_hashrates(chain)

        value_list = []
        time_list = []
        for db_rec in recs:
            time_list.append(db_rec[DMongo.TIMESTAMP].strftime("%Y-%m-%d %H:%M"))
            value, _ = db_rec[DMining.HASHRATE].split(" ")
            value_list.append(float(value))

        results = {
            "values": value_list,
            "times": time_list,
            "units": recs[0][DMining.HASHRATE].split(" ")[1]
        }

        return results