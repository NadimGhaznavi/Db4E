"""
Modules/MiningETL.py

Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from datetime import datetime, timedelta

from db4e.Constants.DMongo import DMongo
from db4e.Constants.DMining import DMining

from db4e.Modules.MiningDb import MiningDb




class MiningETL:


    def __init__(self, mining_db: MiningDb):
        self.mining_db = mining_db

    
    def get_chain_hashrates(self, chain):
        recs = self.mining_db.get_chain_hashrates(chain)
        return self.get_hashrates(recs)
    

    def get_pool_hashrates(self, chain):
        recs = self.mining_db.get_pool_hashrates(chain)
        return self.get_hashrates(recs)


    def get_hashrates(self, recs):
        if not recs:
            return {"values": [], "times": [], "units": ""}

        value_list = []
        time_list = []

        prev_time = recs[0][DMongo.TIMESTAMP]
        prev_hashrate = recs[0][DMining.HASHRATE]
        units = recs[0][DMining.UNIT]

        print(prev_hashrate)

        # Append first record
        time_list.append(prev_time.strftime("%Y-%m-%d %H:%M"))
        value_list.append(float(prev_hashrate))

        for db_rec in recs[1:]:
            cur_time = db_rec[DMongo.TIMESTAMP]
            cur_hashrate = float(db_rec[DMining.HASHRATE])

            # Fill gaps
            gap_time = prev_time + timedelta(hours=1)
            while gap_time < cur_time:
                time_list.append(gap_time.strftime("%Y-%m-%d %H:%M"))
                value_list.append(cur_hashrate)
                gap_time += timedelta(hours=1)

            # Append current record
            time_list.append(cur_time.strftime("%Y-%m-%d %H:%M"))
            value_list.append(cur_hashrate)

            prev_time = cur_time

        # Extract units safely
        parts = str(recs[0][DMining.HASHRATE]).split(" ")
        units = parts[1] if len(parts) > 1 else ""

        print(value_list)

        return {
            "values": value_list,
            "times": time_list,
            "units": units,
        }
