"""
db4e/MiningDb.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""


# Supporting modules
import os, sys
from bson.decimal128 import Decimal128
from decimal import Decimal
from datetime import datetime, timezone

# Import DB4E modules
from db4e.Modules.DbMgr import DbMgr
from db4e.Constants.Defaults import MINING_COL_DEFAULT
from db4e.Constants.Fields import (
    DOC_TYPE_FIELD, TIMESTAMP_FIELD, INSTANCE_FIELD, OBJECT_ID_FIELD, IP_ADDR_FIELD,
    ACTIVE_FIELD)
from db4e.Constants.Mining import (
    BLOCK_FOUND_EVENT_FIELD, MAINCHAIN_HASHRATE_FIELD, POOL_HASHRATE_FIELD,
    SHARE_FOUND_EVENT_FIELD, RT_MAINCHAIN_HASHRATE_FIELD, RT_POOL_HASHRATE_FIELD,
    SHARE_POSITION_FIELD, HASHRATE_FIELD, MINER_FIELD, XMR_PAYMENT_FIELD,
    EFFORT_FIELD, SHARE_FOUND_EVENT_FIELD, SIDECHAIN_HASHRATE_FIELD,
    SIDECHAIN_MINERS_FIELD, WALLET_BALANCE_FIELD, RT_SIDECHAIN_HASHRATE_FIELD
)


class MiningDb():


    def __init__(self):
        self.db = DbMgr()
        self.mining_col = MINING_COL_DEFAULT
    

    def add_block_found(self, timestamp):
        """
        Create a block found record
        """
        jdoc = {
            DOC_TYPE_FIELD: BLOCK_FOUND_EVENT_FIELD,
            TIMESTAMP_FIELD: timestamp
        }
        self.db.insert_uniq_by_timestamp(self.mining_col, jdoc)
        print(f'Creating a new {timestamp} block found event record')


    def add_mainchain_hashrate(self, hashrate):
        """
        Store the mainchain hashrate
        """
        # Update the 'realtime' (rt) record first
        rt_timestamp = datetime.now(timezone.utc)
        jdoc = {
            DOC_TYPE_FIELD: RT_MAINCHAIN_HASHRATE_FIELD,
            TIMESTAMP_FIELD: rt_timestamp,
            HASHRATE_FIELD: hashrate
        }
        existing = self.db.find_one(self.mining_col, {
                DOC_TYPE_FIELD: RT_MAINCHAIN_HASHRATE_FIELD,
        })
        if existing:
            self.db.update_one(
                self.mining_col, {OBJECT_ID_FIELD: existing[OBJECT_ID_FIELD]}, 
                {'$set': {HASHRATE_FIELD: hashrate, TIMESTAMP_FIELD: rt_timestamp}})
            print(f'Updated existing real-time mainchain hashrate ({hashrate}) record')
        else:
            self.db.insert_one(self.mining_col, jdoc)
            print(f'Created new real-time mainchain hashrate ({hashrate}) record')

        # Update the historical, hourly record next
        timestamp = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        jdoc = {
            DOC_TYPE_FIELD: MAINCHAIN_HASHRATE_FIELD,
            TIMESTAMP_FIELD: timestamp,
            HASHRATE_FIELD: hashrate
        }
        existing = self.db.find_one(self.mining_col, {
            DOC_TYPE_FIELD: MAINCHAIN_HASHRATE_FIELD,
            TIMESTAMP_FIELD: timestamp
        })
        if existing:
            self.db.update_one(
                self.mining_col, {OBJECT_ID_FIELD: existing[OBJECT_ID_FIELD]},
                {'$set': {HASHRATE_FIELD: hashrate }})
            print(f'Updated existing mainchain hashrate ({hashrate}) record')
        else:
            self.db.insert_one(self.mining_col, jdoc)
            print(f'Created new real-time mainchain hashrate ({hashrate}) record')


    def add_pool_hashrate(self, hashrate):
        """
        Store the pool hashrate
        """
        # Update the 'realtime' (rt) record first
        rt_timestamp = datetime.now(timezone.utc)
        jdoc = {
            DOC_TYPE_FIELD: RT_POOL_HASHRATE_FIELD,
            TIMESTAMP_FIELD: rt_timestamp,
            HASHRATE_FIELD: hashrate
        }
        existing = self.db.find_one(self.mining_col, {
              DOC_TYPE_FIELD: RT_POOL_HASHRATE_FIELD,
        })
        if existing:
            self.db.update_one(
                self.mining_col, {OBJECT_ID_FIELD: existing[OBJECT_ID_FIELD]},
                {'$set': {HASHRATE_FIELD: hashrate, TIMESTAMP_FIELD: rt_timestamp}})
            print(f'Updated existing real-time pool hashrate ({hashrate}) record')
        else:
            self.db.insert_one(self.mining_col, jdoc)
            print(f'Created new real-time pool hashrate ({hashrate}) record')

        # Update the historical, hourly record next
        timestamp = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        jdoc = {
            DOC_TYPE_FIELD: POOL_HASHRATE_FIELD,
            TIMESTAMP_FIELD: timestamp,
            HASHRATE_FIELD: hashrate
        }
        existing = self.db.find_one(self.mining_col, {
            DOC_TYPE_FIELD: POOL_HASHRATE_FIELD,
            TIMESTAMP_FIELD: timestamp
        })
        if existing:
            self.db.update_one(
                self.mining_col, {OBJECT_ID_FIELD: existing[OBJECT_ID_FIELD]},
                {'$set': {HASHRATE_FIELD: hashrate }})
            print(f'Updated existing pool hashrate ({hashrate}) record')
        else:
            self.db.insert_one(self.mining_col, jdoc)
            print(f'Created new real-time pool hashrate ({hashrate}) record')


    def add_share_found(self, timestamp, miner, ip_addr, effort):
        """
        Create a JSON document and pass it to the Db4eDb to be added to the backend database
        """
        jdoc = {
            DOC_TYPE_FIELD: SHARE_FOUND_EVENT_FIELD,
            TIMESTAMP_FIELD: timestamp,
            MINER_FIELD: miner,
            IP_ADDR_FIELD: ip_addr,
            EFFORT_FIELD: effort
        }
        self.db.insert_uniq_by_timestamp(self.mining_col, jdoc)
        print(f'New share found record', { MINER_FIELD: miner })


    def add_share_position(self, timestamp, position):
        """
        Store the share position
        """
        # TODO update P2Pool to stop including the timestamp
        timestamp = datetime.now(timezone.utc)
        jdoc = {
            DOC_TYPE_FIELD: SHARE_POSITION_FIELD,
            TIMESTAMP_FIELD: timestamp,
            SHARE_POSITION_FIELD : position
        }
        existing = self.db.find_one(
            self.mining_col, {DOC_TYPE_FIELD: SHARE_POSITION_FIELD})
        if existing:
            self.db.update_one(
                self.mining_col, {OBJECT_ID_FIELD: existing[OBJECT_ID_FIELD]},
                {'$set': {TIMESTAMP_FIELD: timestamp, SHARE_POSITION_FIELD: position}})
            print(f'Updated share position ({position}) record')
        else:
            self.db.insert_one(self.mining_col, jdoc)
            print(f'Created a new share position ({position}) record')


    def add_sidechain_hashrate(self, hashrate):
        """
        Store the sidechain hashrate
        """
        # Update the 'realtime' (rt) record first
        rt_timestamp = datetime.now(timezone.utc)
        jdoc = {
            DOC_TYPE_FIELD: RT_SIDECHAIN_HASHRATE_FIELD,
            TIMESTAMP_FIELD: rt_timestamp,
            HASHRATE_FIELD: hashrate
        }
        existing = self.db.find_one(self.mining_col, {
            DOC_TYPE_FIELD: RT_SIDECHAIN_HASHRATE_FIELD,
        })
        if existing:
            self.db.update_one(
                self.mining_col, {OBJECT_ID_FIELD: existing[OBJECT_ID_FIELD]},
                {'$set': {HASHRATE_FIELD: hashrate, TIMESTAMP_FIELD: rt_timestamp}})
            print(f'Updated existing real-time sidechain hashrate ({hashrate}) record')
        else:
            self.db.insert_one(self.mining_col, jdoc)
            print(f'Created new real-time sidechain hashrate ({hashrate}) record')

        # Update the historical, hourly record next
        timestamp = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        jdoc = {
            DOC_TYPE_FIELD: SIDECHAIN_HASHRATE_FIELD,
            TIMESTAMP_FIELD: timestamp,
            HASHRATE_FIELD: hashrate
        }
        existing = self.db.find_one(self.mining_col, {
            DOC_TYPE_FIELD: SIDECHAIN_HASHRATE_FIELD,
            TIMESTAMP_FIELD: timestamp
        })
        if existing:
            self.db.update_one(
                self.mining_col, {OBJECT_ID_FIELD: existing[OBJECT_ID_FIELD]},
                {'$set': {HASHRATE_FIELD: hashrate }})
            print(f'Updated existing sidechain hashrate ({hashrate}) record')
        else:
            self.db.insert_one(self.mining_col, jdoc)
            print(f'Created new real-time sidechain hashrate ({hashrate}) record')


    def add_sidechain_miners(self, num_miners):
        """
        Store the number of unique wallets on the sidechain
        """
        timestamp = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        jdoc = {
            DOC_TYPE_FIELD: SIDECHAIN_MINERS_FIELD,
            TIMESTAMP_FIELD: timestamp,
            SIDECHAIN_MINERS_FIELD: num_miners
        }
        existing = self.db.find_one(self.mining_col, {
            DOC_TYPE_FIELD: SIDECHAIN_MINERS_FIELD,
            TIMESTAMP_FIELD: timestamp
        })
        if existing:
            self.db.update_one(
                self.mining_col, {OBJECT_ID_FIELD: existing[OBJECT_ID_FIELD]},
                {'$set': {SIDECHAIN_MINERS_FIELD: num_miners}})
            print(f'Updated existing sidechain miners ({num_miners}) record')
        else:
            self.db.insert_one(self.mining_col, jdoc)
            print(f'Updated existing sidechain miners ({num_miners}) record')


    def add_to_wallet(self, amount):
        # CAREFUL with datatypes here!!!
        amount = amount.to_decimal()
        balance = self.get_wallet_balance().to_decimal() # This call ensures the DB record exists
        new_balance = Decimal128(amount + balance)
        dbRec = self.db.find_one(self.mining_col, {DOC_TYPE_FIELD: WALLET_BALANCE_FIELD})
        self.db.update_one(
            self.mining_col, {OBJECT_ID_FIELD: dbRec[OBJECT_ID_FIELD]},
            {'$set': {WALLET_BALANCE_FIELD: new_balance}})
        print(f'Updated XMR Wallet balance ({new_balance}) record')


    def add_xmr_payment(self, timestamp, payment):
        jdoc = {
            DOC_TYPE_FIELD: XMR_PAYMENT_FIELD,
            TIMESTAMP_FIELD: timestamp,
            XMR_PAYMENT_FIELD: payment
        }
        if self.db.insert_uniq_by_timestamp(self.mining_col, jdoc):
            self.add_to_wallet(payment)
        print(f'New XMR payment ({payment}) record')


    def get_docs(self, doc_type):
        dbCursor = self.db.find_many(self.mining_col, {DOC_TYPE_FIELD: doc_type})
        return dbCursor


    def get_mainchain_hashrate(self):
        record = self.db.find_one(
            self.mining_col, {DOC_TYPE_FIELD: RT_MAINCHAIN_HASHRATE_FIELD})
        if record:
            return record

        # Create a new doc if it doesn't already exist
        jdoc = {
            DOC_TYPE_FIELD: RT_MAINCHAIN_HASHRATE_FIELD,
            TIMESTAMP_FIELD: None,
            HASHRATE_FIELD: None
        }
        self.db.insert_one(self.mining_col, jdoc)
        print(f'Created new (rt_mainchain_hashrate) record')
        return None


    def get_pool_hashrate(self):
        record = self.db.find_one(
            self.mining_col, {DOC_TYPE_FIELD: RT_POOL_HASHRATE_FIELD})
        if record:
            return record

        # Create a new doc if it doesn't already exist
        jdoc = {
            DOC_TYPE_FIELD: RT_POOL_HASHRATE_FIELD,
            TIMESTAMP_FIELD: None,
            HASHRATE_FIELD: None
        }
        self.db.insert_one(self.mining_col, jdoc)
        print(f'Created new (rt_pool_hashrate) record')
        return None


    def get_share_position(self):
        record = self.db.find_one(
            self.mining_col, {DOC_TYPE_FIELD: SHARE_POSITION_FIELD})
        if record:
            return record

        jdoc = {
            DOC_TYPE_FIELD: SHARE_POSITION_FIELD,
            TIMESTAMP_FIELD: None,
            SHARE_POSITION_FIELD: None
        }
        self.db.insert_one(self.mining_col, jdoc)
        print(f'Created a new (share_position) record')


    def get_shares(self):
        dbCursor = self.db.find_many(
            self.mining_col, {DOC_TYPE_FIELD: SHARE_FOUND_EVENT_FIELD})
        resDict = {}
        for share in dbCursor:
            timestamp = share[TIMESTAMP_FIELD]
            miner = share[MINER_FIELD]
            resDict[timestamp] = miner
        return resDict


    def get_sidechain_hashrate(self):
        record = self.db.find_one(
            self.mining_col, {DOC_TYPE_FIELD: RT_SIDECHAIN_HASHRATE_FIELD})
        if record:
            return record

        # Create a new doc if it doesn't already exist
        jdoc = {
            DOC_TYPE_FIELD: RT_SIDECHAIN_HASHRATE_FIELD,
            TIMESTAMP_FIELD: None,
            HASHRATE_FIELD: None
        }
        self.db.insert_one(self.mining_col, jdoc)
        print(f'Created new (rt_sidechain_hashrate) record')
        return None            


    def get_wallet_balance(self):
        record = self.db.find_one(
            self.mining_col, {DOC_TYPE_FIELD: WALLET_BALANCE_FIELD})

        if record:
            return record[WALLET_BALANCE_FIELD]

        jdoc = {DOC_TYPE_FIELD: WALLET_BALANCE_FIELD,
                WALLET_BALANCE_FIELD: Decimal128('0') }
        self.db.insert_one(self.mining_col, jdoc)
        print(f'Created a new (wallet_balance) record with balance (0)')
        return Decimal128('0')
  

    def get_miners(self):
        dbCursor = self.db.find_many(
            self.mining_col, {DOC_TYPE_FIELD: MINER_FIELD})
        resDict = {}
        for miner in dbCursor:
            instance = miner[INSTANCE_FIELD]
            hashrate = miner[HASHRATE_FIELD]
            timestamp = miner[TIMESTAMP_FIELD]
            active = miner[ACTIVE_FIELD]
            resDict[instance] = {
                INSTANCE_FIELD: instance,
                HASHRATE_FIELD: hashrate,
                TIMESTAMP_FIELD: timestamp,
                ACTIVE_FIELD: active,
            }     
        return resDict
  

    def get_xmr_payments(self):
        payments_cursor = self.db.find_many(
            self.mining_col, {DOC_TYPE_FIELD: XMR_PAYMENT_FIELD})
        payments_dict = {}
        for payment in payments_cursor:
            timestamp = payment[TIMESTAMP_FIELD]
            payment = payment[XMR_PAYMENT_FIELD]
            payments_dict[timestamp] = payment
        return payments_dict


    def update_miner(self, instance, hashrate):
        timestamp = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        jdoc = {
            DOC_TYPE_FIELD: MINER_FIELD,
            INSTANCE_FIELD: instance,
            HASHRATE_FIELD: hashrate,
            TIMESTAMP_FIELD: timestamp,
            ACTIVE_FIELD: True
        }
        existing = self.db.find_one(self.mining_col, {
            DOC_TYPE_FIELD: MINER_FIELD,
            INSTANCE_FIELD: instance,
            TIMESTAMP_FIELD: timestamp
        })
        if existing:
            self.db.update_one(
                self.mining_col, {OBJECT_ID_FIELD: existing[OBJECT_ID_FIELD]}, 
                {'$set': {HASHRATE_FIELD: hashrate}})
            print(f'Updated existing ({timestamp}) miner ({instance}) hashrate ({hashrate}) record')
        else:
            self.db.insert_one(self.mining_col, jdoc)
            print(f'Created a new ({timestamp}) miner ({instance}) hashrate ({hashrate}) record')