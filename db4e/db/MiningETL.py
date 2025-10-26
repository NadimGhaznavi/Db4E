"""
Modules/MiningETL.py

Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from datetime import datetime, timedelta
from bson.decimal128 import Decimal128
from decimal import Decimal, ROUND_HALF_UP

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
        return self.get_found_events(recs)

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
        return self.etl_recs(recs) or {}

    def get_found_events(self, recs):
        if not recs:
            return {DField.DAYS: [], DField.VALUES: []}

        results = {}

        cur_day = recs[0][DMongo.TIMESTAMP].replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        for rec in recs:
            rec_day = rec[DMongo.TIMESTAMP].replace(
                hour=0, minute=0, second=0, microsecond=0
            )

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
        new_times = range(-len(times), 0, 1)

        new_values = []
        for value in values:
            new_values.append(float(value))

        first_day = -len(new_times)
        new_days = list(range(first_day, 0, 1))

        return {
            DField.DAYS: new_days,
            DField.VALUES: new_values,
        }

    def etl_recs(self, recs):
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
        cur_day = 0

        # Append first record
        time_list.append(prev_time.strftime("%Y-%m-%d %H:%M"))
        day_list.append(cur_day)
        value_list.append(float(prev_hashrate))

        for rec in recs[1:]:
            cur_time = rec[DMongo.TIMESTAMP]
            cur_hashrate = float(rec[DMining.HASHRATE])
            cur_day -= float(1 / 24)

            # Fill gaps
            gap_time = prev_time + timedelta(hours=1)
            while gap_time < cur_time:
                time_list.append(gap_time.strftime("%Y-%m-%d %H:%M"))
                value_list.append(cur_hashrate)
                gap_time += timedelta(hours=1)
                day_list.append(cur_day)
                cur_day -= float(1 / 24)

            # Append current record
            time_list.append(cur_time.strftime("%Y-%m-%d %H:%M"))
            value_list.append(cur_hashrate)
            day_list.append(cur_day)

            prev_time = cur_time

        if DMining.UNIT in recs[0]:
            units = recs[0][DMining.UNIT]
        else:
            units = "H/s"

        return {DField.VALUES: value_list, DField.DAYS: day_list, DField.UNITS: units}

    def get_miner_hashrate(self, miner):
        rec = self.mining_db.get_miner_hashrate(miner)
        if rec:
            hashrate = str(rec[DMining.HASHRATE])
        else:
            hashrate = "Unknown"
        return hashrate + " " + DLabel.H_PER_S

    def get_miner_hashrates(self, miner):
        recs = self.mining_db.get_miner_hashrates(miner)
        return self.etl_recs(recs) or {}

    def get_miner_uptime(self, miner):
        rec = self.mining_db.get_miner_uptime(miner)
        if rec:
            uptime = str(rec[DMongo.UPTIME])
        else:
            uptime = "Unknown"
        return uptime

    def get_payments(self):
        recs = self.mining_db.get_payments()
        # Aggregate the payments into daily totals.
        results = {}
        if not recs:
            return {DField.DAYS: [], DField.VALUES: []}

        results = {}

        cur_day = recs[0][DMongo.TIMESTAMP].replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        for rec in recs:
            rec_day = rec[DMongo.TIMESTAMP].replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            # Fill in all missing days with 0
            while cur_day < rec_day:
                if cur_day not in results:
                    results[cur_day] = Decimal128("0")
                cur_day += timedelta(days=1)

            # Add up the XMR payements, we need to be careful to avoid floating point
            # rounding errors.
            db_payment = rec[DMining.XMR_PAYMENT].to_decimal()
            cur_day_payment = results.get(rec_day, Decimal128("0")).to_decimal()
            results[rec_day] = Decimal128(db_payment + cur_day_payment)
            cur_day = rec_day

        # Convert dict → lists (sorted by day)
        times = [day.strftime("%Y-%m-%d %H:%M") for day in sorted(results.keys())]
        values = [results[day] for day in sorted(results.keys())]

        # Replace datetime days with integers for plotting
        new_times = range(-len(times), 0, 1)

        first_day = -len(new_times)
        new_days = list(range(first_day, 0, 1))

        # For plotting, we don't need or want 12 decimal places. We avoid the round()
        # function since Python converts to float behind the scenes.
        new_values = []
        for value in values:
            new_values.append(float(round(value.to_decimal(), 6)))

        print(f"results: {new_days}\n{new_values}")
        return {
            DField.DAYS: new_days,
            DField.VALUES: new_values,
        }

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
        return self.etl_recs(recs)

    def get_remote_xmrig_timestamp(self, instance):
        rec = self.mining_db.get_rt_miner_rec(instance)
        if rec:
            return rec[DMongo.TIMESTAMP]
        return None

    def get_share_found_events(self, pool=None, miner=None):
        if pool is not None:
            recs = self.mining_db.get_share_found_events(pool=pool)
        elif miner is not None:
            recs = self.mining_db.get_share_found_events(miner=miner)
        return self.get_found_events(recs)

    def get_share_found_events_stacked(self, pool=None, miner=None):
        if pool is not None:
            recs = self.mining_db.get_share_found_events(pool=pool)
        elif miner is not None:
            recs = self.mining_db.get_share_found_events(miner=miner)

        if not recs:
            return {DField.DAYS: [], DField.VALUES: [], DField.MINERS: []}

        results = {}
        miner_set = set()

        cur_day = recs[0][DMongo.TIMESTAMP].replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        for rec in recs:
            rec_day = rec[DMongo.TIMESTAMP].replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            # Fill in all missing days with 0
            while cur_day < rec_day:
                results.setdefault(cur_day, {})
                cur_day += timedelta(days=1)

            # Get the miner name
            miner = rec[DMining.MINER]
            miner_set.add(miner)

            # Count the share found for this day
            results.setdefault(rec_day, {})
            results[rec_day][miner] = results[rec_day].get(miner, 0) + 1

            cur_day = rec_day

        miners = sorted(miner_set)
        miner_lists = {miner: [] for miner in miners}

        for day in results:
            for miner in miners:
                miner_lists[miner].append(results[day].get(miner, 0))

        new_days = range(-len(results), 0, 1)

        final_results = {
            DField.DAYS: list(new_days),
            DField.VALUES: list(miner_lists.values()),
            DField.MINERS: list(miner_set),
        }
        print(final_results)
        return final_results

    def get_table_data(self, p2pool):
        pass
