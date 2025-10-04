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
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField

from db4e.Modules.MiningDb import MiningDb




class MiningETL:


    def __init__(self, mining_db: MiningDb):
        self.mining_db = mining_db


    def get_block_found_events(self, instance):
        recs = self.mining_db.get_block_found_events(instance)
        if not recs:
            return {"values": [], "times": [], "units": "blocks"}

        results = {}

        cur_day = recs[0][DMongo.TIMESTAMP].replace(hour=0, minute=0, second=0, microsecond=0)

        for rec in recs:
            rec_day = rec[DMongo.TIMESTAMP].replace(hour=0, minute=0, second=0, microsecond=0)

            # Fill in all missing days with 0
            while cur_day < rec_day:
                if cur_day not in results:
                    results[cur_day] = 0
                cur_day += timedelta(days=1)

            # Count the block for this day
            results[rec_day] = results.get(rec_day, 0) + 1
            cur_day = rec_day

        # Convert dict → lists (sorted by day)
        times = [day.strftime("%Y-%m-%d %H:%M") for day in sorted(results.keys())]
        values = [results[day] for day in sorted(results.keys())]

        # Replace datetime days with integers for plotting
        new_times = range(- len(times), 0, 1)

        new_values = []
        for value in values:
            new_values.append(float(value))

        return {
            "values": new_values,
            "days": new_times,
            "units": "blocks",
        }

    
    def get_chain_hashrate(self, instance):
        rec = self.mining_db.get_chain_hashrate(instance)
        if rec:
            hashrate = str(rec[DMining.HASHRATE])
            units = rec[DMining.UNIT]
        else:
            hashrate = "Unknown"
            units = ""
        return hashrate + " " + units
    

    def get_chain_hashrates(self, instance):
        recs = self.mining_db.get_chain_hashrates(instance)
        return self.get_hashrates(recs) or {}
    

    def get_miner_hashrate(self, miner):
        rec = self.mining_db.get_miner_hashrate(miner)
        if rec:
            hashrate = str(rec[DMining.HASHRATE])
        else:
            hashrate = "Unknown"
        return hashrate + " " + DLabel.H_PER_S


    def get_miner_hashrates(self, miner):
        recs = self.mining_db.get_miner_hashrates(miner)
        return self.get_hashrates(recs) or {}


    def get_miner_uptime(self, miner):
        rec = self.mining_db.get_miner_uptime(miner)
        if rec:
            uptime = str(rec[DMongo.UPTIME])
        else:
            uptime = "Unknown"
        return uptime


    def get_pool_hashrate(self, instance):
        hashrate_rec = self.mining_db.get_pool_hashrate(instance)
        if hashrate_rec:
            hashrate = str(hashrate_rec[DMining.HASHRATE])
            units = hashrate_rec[DMining.UNIT]
        else:
            hashrate = "Unknown"
            units = ""
        return hashrate + " " + units


    def get_pool_hashrates(self, instance):
        recs = self.mining_db.get_pool_hashrates(instance=instance)
        return self.get_hashrates(recs)


    def get_hashrates(self, recs):
        if not recs:
            return {DField.VALUES: [], DField.DAYS: [], DField.UNITS: ""}

        value_list = []
        time_list = []
        day_list = []

        prev_time = recs[0][DMongo.TIMESTAMP]
        prev_hashrate = recs[0][DMining.HASHRATE]
        if DMining.UNIT in recs[0]:
            units = recs[0][DMining.UNIT]
        else:
            units = "H/s"


        # Number of data points
        cur_day = - float(len(recs) / 24)


        # Append first record
        time_list.append(prev_time.strftime("%Y-%m-%d %H:%M"))
        day_list.append(cur_day)
        value_list.append(float(prev_hashrate))

        for rec in recs[1:]:
            cur_time = rec[DMongo.TIMESTAMP]
            cur_hashrate = float(rec[DMining.HASHRATE])
            cur_day += float(1 / 24)

            # Fill gaps
            gap_time = prev_time + timedelta(hours=1)
            while gap_time < cur_time:
                time_list.append(gap_time.strftime("%Y-%m-%d %H:%M"))
                value_list.append(cur_hashrate)
                gap_time += timedelta(hours=1)
                day_list.append(cur_day)
                cur_day += float(1 / 24)


            # Append current record
            time_list.append(cur_time.strftime("%Y-%m-%d %H:%M"))
            value_list.append(cur_hashrate)
            day_list.append(cur_day)

            prev_time = cur_time


        if DMining.UNIT in recs[0]:
            units = recs[0][DMining.UNIT]
        else:
            units = "H/s"

        return {
            DField.VALUES: value_list,
            DField.DAYS: day_list,
            DField.UNITS: units
        }
    

    def get_remote_xmrig_timestamp(self, instance):
        rec = self.mining_db.get_rt_miner_rec(instance)
        if rec:
            return rec[DMongo.TIMESTAMP]
        return None
    
