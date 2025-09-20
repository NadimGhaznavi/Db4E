"""
db4e/MiningDb.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""


# Supporting modules
from bson.decimal128 import Decimal128
from decimal import Decimal
from datetime import datetime, timezone

# Import DB4E modules
from db4e.Modules.Db4ELogger import Db4ELogger
from db4e.Modules.DbMgr import DbMgr

from db4e.Constants.DDef import DDef
from db4e.Constants.DMongo import DMongo
from db4e.Constants.DMining import DMining
from db4e.Constants.DModule import DModule
from db4e.Constants.DDebug import DDebug

DDebug.FUNCTION = True


class MiningDb():


    def __init__(self, db: DbMgr, log_file: str):
        self.db = db
        self.mining_col = DDef.MINING_COL
        self.log = Db4ELogger(db4e_module=DModule.MINING_DB, log_file=log_file)
    

    def add_block_found(self, timestamp, chain):
        """
        Block found record
        """
        if DDebug.FUNCTION:
            self.log.debug(f"MiningDb:add_block_found(): {chain}")
        jdoc = {
            DMongo.DOC_TYPE: DMining.BLOCK_FOUND_EVENT,
            DMongo.CHAIN: chain,
            DMongo.TIMESTAMP: timestamp
        }
        self.db.insert_uniq_by_timestamp(self.mining_col, jdoc)
        self.log.info(f'Creating a new {timestamp} block found event record')


    def add_chain_hashrate(self, chain, hashrate):
        """
        Historical and real-time chain hashrate record
        """
        if DDebug.FUNCTION:
            self.log.debug(f"MiningDb:add_chain_hashrate()")

        # Update the 'realtime' (rt) record first
        rt_timestamp = datetime.now(timezone.utc)
        jdoc = {
            DMongo.DOC_TYPE: DMining.RT_HASHRATE,
            DMongo.CHAIN: chain,
            DMongo.TIMESTAMP: rt_timestamp,
            DMining.HASHRATE: hashrate
        }

        existing = self.db.find_one(self.mining_col, {
            DMongo.DOC_TYPE: DMining.RT_HASHRATE, DMongo.CHAIN: chain })
        
        if existing:
            self.db.update_one(
                self.mining_col, { DMongo.OBJECT_ID: existing[DMongo.OBJECT_ID] }, 
                { DMining.HASHRATE: hashrate, DMongo.TIMESTAMP: rt_timestamp })
            self.log.info(f'Updated existing real-time {chain} hashrate ({hashrate}) record')

        else:
            self.db.insert_one(self.mining_col, jdoc)
            self.log.info(f'Created new real-time {chain} hashrate ({hashrate}) record')

        # Update the historical, hourly record
        timestamp = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        jdoc = {
            DMongo.DOC_TYPE: DMining.HASHRATE,
            DMongo.CHAIN: chain,
            DMongo.TIMESTAMP: timestamp,
            DMining.HASHRATE: hashrate
        }

        existing = self.db.find_one(self.mining_col, {
            DMongo.DOC_TYPE: DMining.HASHRATE, DMongo.CHAIN: chain, 
            DMongo.TIMESTAMP: timestamp
        })

        if existing:
            self.db.update_one(
                self.mining_col, {DMongo.OBJECT_ID: existing[DMongo.OBJECT_ID]},
                {DMining.HASHRATE: hashrate })
            self.log.info(f'Updated existing historical {chain} hashrate ({hashrate}) record')

        else:
            self.db.insert_one(self.mining_col, jdoc)
            self.log.info(f'Created new historical {chain} hashrate ({hashrate}) record')


    def add_chain_miners(self, chain, num_miners):
        """
        Store the number of unique wallets on the sidechain
        """
        if DDebug.FUNCTION:
            print(f"MiningDb:add_sidechain_miners")
        timestamp = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        jdoc = {
            DMongo.DOC_TYPE: DMining.MINERS,
            DMongo.CHAIN: chain,
            DMongo.TIMESTAMP: timestamp,
            DMongo.MINERS: num_miners
        }
        existing = self.db.find_one(self.mining_col, {
            DMongo.DOC_TYPE: DMining.MINERS, DMongo.CHAIN: chain,
            DMongo.TIMESTAMP: timestamp
        })
        if existing:
            self.db.update_one(
                self.mining_col, {DMongo.OBJECT_ID: existing[DMongo.OBJECT_ID]},
                {DMining.MINERS: num_miners})
            self.log.info(f'Updated existing {chain} miners ({num_miners}) record')
        else:
            self.db.insert_one(self.mining_col, jdoc)
            self.log.info(f'Created new {chain} miners ({num_miners}) record')


    def add_pool_hashrate(self, chain, hashrate):
        """
        Store the pool hashrate
        """
        if DDebug.FUNCTION:
            print(f"MiningDb:add_pool_hashrate()")        
        # Update the 'realtime' (rt) record first
        rt_timestamp = datetime.now(timezone.utc)
        jdoc = {
            DMongo.DOC_TYPE: DMining.RT_POOL_HASHRATE,
            DMongo.CHAIN: chain,
            DMongo.TIMESTAMP: rt_timestamp,
            DMongo.HASHRATE: hashrate
        }
        existing = self.db.find_one(self.mining_col, {
              DMongo.DOC_TYPE: DMining.RT_POOL_HASHRATE,
        })
        if existing:
            self.db.update_one(
                self.mining_col, {DMongo.OBJECT_ID: existing[DMongo.OBJECT_ID]},
                {DMining.HASHRATE: hashrate, DMongo.TIMESTAMP: rt_timestamp})
            print(f'Updated existing real-time pool hashrate ({hashrate}) record')
        else:
            self.db.insert_one(self.mining_col, jdoc)
            print(f'Created new real-time pool hashrate ({hashrate}) record')

        # Update the historical, hourly record next
        timestamp = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        jdoc = {
            DMongo.DOC_TYPE: DMining.POOL_HASHRATE,
            DMongo.CHAIN: chain,
            DMongo.TIMESTAMP: timestamp,
            DMongo.HASHRATE: hashrate
        }
        existing = self.db.find_one(self.mining_col, {
            DMongo.DOC_TYPE: DMining.POOL_HASHRATE,
            DMongo.CHAIN: chain,
            DMongo.TIMESTAMP: timestamp
        })
        if existing:
            self.db.update_one(
                self.mining_col, {DMongo.OBJECT_ID: existing[DMongo.OBJECT_ID]},
                {DMining.HASHRATE: hashrate })
            print(f'Updated existing pool hashrate ({hashrate}) record')
        else:
            self.db.insert_one(self.mining_col, jdoc)
            print(f'Created new real-time pool hashrate ({hashrate}) record')


    def add_share_found(self, chain, timestamp, miner, ip_addr, effort):
        """
        Create a JSON document and pass it to the Db4eDb to be added to the backend database
        """
        if DDebug.FUNCTION:
            print(f"MiningDb:add_share_found()")
        jdoc = {
            DMongo.DOC_TYPE: DMining.SHARE_FOUND_EVENT,
            DMongo.TIMESTAMP: timestamp,
            DMongo.MINER: miner,
            DMongo.CHAIN: chain,
            DMongo.IP_ADDR: ip_addr,
            DMining.EFFORT: effort
        }
        self.db.insert_uniq_by_timestamp(self.mining_col, jdoc)
        print(f'New share found record', { DMining.MINER: miner })


    def add_share_position(self, chain, timestamp, position):
        """
        Store the share position
        """
        if DDebug.FUNCTION:
            print(f"MiningDb:add_share_position")
        # TODO update P2Pool to stop including the timestamp
        timestamp = datetime.now(timezone.utc)
        jdoc = {
            DMongo.DOC_TYPE: DMining.SHARE_POSITION,
            DMongo.CHAIN: chain,
            DMongo.TIMESTAMP: timestamp,
            DMining.SHARE_POSITION : position
        }
        existing = self.db.find_one(
            self.mining_col, {DMongo.DOC_TYPE: DMining.SHARE_POSITION})
        if existing:
            self.db.update_one(
                self.mining_col, {DMongo.OBJECT_ID: existing[DMongo.OBJECT_ID]},
                {'$set': {DMongo.TIMESTAMP: timestamp, DMining.SHARE_POSITION: position}})
            print(f'Updated share position ({position}) record')
        else:
            self.db.insert_one(self.mining_col, jdoc)
            print(f'Created a new share position ({position}) record')


    def add_to_wallet(self, amount):
        if DDebug.FUNCTION:
            print(f"MiningDb:add_to_wallet()")
        # CAREFUL with datatypes here!!!
        amount = amount.to_decimal()
        balance = self.get_wallet_balance().to_decimal() # This call ensures the DB record exists
        new_balance = Decimal128(amount + balance)
        dbRec = self.db.find_one(self.mining_col, {DMongo.DOC_TYPE: DMining.WALLET_BALANCE})
        self.db.update_one(
            self.mining_col, {DMongo.OBJECT_ID: dbRec[DMongo.OBJECT_ID]},
            {'$set': {DMining.WALLET_BALANCE: new_balance}})
        print(f'Updated XMR Wallet balance ({new_balance}) record')


    def add_xmr_payment(self, timestamp, payment):
        if DDebug.FUNCTION:
            print(f"MiningDb:add_xmr_payment()")
        jdoc = {
            DMongo.DOC_TYPE: DMining.XMR_PAYMENT,
            DMongo.TIMESTAMP: timestamp,
            DMining.XMR_PAYMENT: payment
        }
        if self.db.insert_uniq_by_timestamp(self.mining_col, jdoc):
            self.add_to_wallet(payment)
        print(f'New XMR payment ({payment}) record')


    def get_docs(self, doc_type):
        if DDebug.FUNCTION:
            print(f"MiningDb:get_docs()")
        dbCursor = self.db.find_many(self.mining_col, {DMongo.DOC_TYPE: doc_type})
        return dbCursor


    def get_mainchain_hashrate(self):
        if DDebug.FUNCTION:
            print(f"MiningDb:get_mainchain_hashrate()")        
        record = self.db.find_one(
            self.mining_col, {DMongo.DOC_TYPE: DMining.RT_MAINCHAIN_HASHRATE})
        if record:
            return record

        # Create a new doc if it doesn't already exist
        jdoc = {
            DMongo.DOC_TYPE: DMining.RT_MAINCHAIN_HASHRATE,
            DMongo.TIMESTAMP: None,
            DMining.HASHRATE: None
        }
        self.db.insert_one(self.mining_col, jdoc)
        print(f'Created new (rt_mainchain_hashrate) record')
        return None


    def get_pool_hashrate(self):
        if DDebug.FUNCTION:
            print(f"MiningDb:get_pool_hashrate()")
        record = self.db.find_one(
            self.mining_col, {DMongo.DOC_TYPE: DMining.RT_POOL_HASHRATE})
        if record:
            return record

        # Create a new doc if it doesn't already exist
        jdoc = {
            DMongo.DOC_TYPE: DMining.RT_POOL_HASHRATE,
            DMongo.TIMESTAMP: None,
            DMining.HASHRATE: None
        }
        self.db.insert_one(self.mining_col, jdoc)
        print(f'Created new (rt_pool_hashrate) record')
        return None


    def get_share_position(self):
        if DDebug.FUNCTION:
            print(f"MiningDb:get_share_position()")
        record = self.db.find_one(
            self.mining_col, {DMongo.DOC_TYPE: DMining.SHARE_POSITION})
        if record:
            return record

        jdoc = {
            DMongo.DOC_TYPE: DMining.SHARE_POSITION,
            DMongo.TIMESTAMP: None,
            DMining.SHARE_POSITION: None
        }
        self.db.insert_one(self.mining_col, jdoc)
        print(f'Created a new (share_position) record')


    def get_shares(self):
        if DDebug.FUNCTION:
            print(f"MiningDb:get_shares()")
        dbCursor = self.db.find_many(
            self.mining_col, {DMongo.DOC_TYPE: DMining.SHARE_FOUND_EVENT})
        resDict = {}
        for share in dbCursor:
            timestamp = share[DMongo.TIMESTAMP]
            miner = share[DMining.MINER]
            resDict[timestamp] = miner
        return resDict


    def get_sidechain_hashrate(self):
        if DDebug.FUNCTION:
            print(f"MiningDb:get_sidechain_hashrate()")
        record = self.db.find_one(
            self.mining_col, {DMongo.DOC_TYPE: DMining.RT_SIDECHAIN_HASHRATE})
        if record:
            return record

        # Create a new doc if it doesn't already exist
        jdoc = {
            DMongo.DOC_TYPE: DMining.RT_SIDECHAIN_HASHRATE,
            DMongo.TIMESTAMP: None,
            DMining.HASHRATE: None
        }
        self.db.insert_one(self.mining_col, jdoc)
        print(f'Created new (rt_sidechain_hashrate) record')
        return None            


    def get_wallet_balance(self):
        if DDebug.FUNCTION:
            print(f"MiningDb:get_wallet_balance()")
        record = self.db.find_one(
            self.mining_col, {DMongo.DOC_TYPE: DMining.WALLET_BALANCE})

        if record:
            return record[DMining.WALLET_BALANCE]

        jdoc = {DMongo.DOC_TYPE: DMining.WALLET_BALANCE,
                DMining.WALLET_BALANCE: Decimal128('0') }
        self.db.insert_one(self.mining_col, jdoc)
        print(f'Created a new (wallet_balance) record with balance (0)')
        return Decimal128('0')
  

    def get_miners(self):
        if DDebug.FUNCTION:
            print(f"MiningDb:get_miners()")
        dbCursor = self.db.find_many(
            self.mining_col, {DMongo.DOC_TYPE: DMining.MINER})
        resDict = {}
        for miner in dbCursor:
            instance = miner[DMining.INSTANCE]
            hashrate = miner[DMining.HASHRATE]
            timestamp = miner[DMongo.TIMESTAMP]
            active = miner[DMining.ACTIVE]
            resDict[instance] = {
                DMining.INSTANCE: instance,
                DMining.HASHRATE: hashrate,
                DMongo.TIMESTAMP: timestamp,
                DMining.ACTIVE: active,
            }     
        return resDict
  

    def get_xmr_payments(self):
        if DDebug.FUNCTION:
            print(f"MiningDb:get_xmr_payments()")
        payments_cursor = self.db.find_many(
            self.mining_col, {DMongo.DOC_TYPE: DMining.XMR_PAYMENT})
        payments_dict = {}
        for payment in payments_cursor:
            timestamp = payment[DMongo.TIMESTAMP]
            payment = payment[DMining.XMR_PAYMENT]
            payments_dict[timestamp] = payment
        return payments_dict


    def update_miner(self, instance, hashrate):
        if DDebug.FUNCTION:
            print(f"MiningDb:update_miner()")
        timestamp = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        jdoc = {
            DMongo.DOC_TYPE: DMining.MINER,
            DMining.INSTANCE: instance,
            DMining.HASHRATE: hashrate,
            DMongo.TIMESTAMP: timestamp,
            DMining.ACTIVE: True
        }
        existing = self.db.find_one(self.mining_col, {
            DMongo.DOC_TYPE: DMining.MINER,
            DMining.INSTANCE: instance,
            DMongo.TIMESTAMP: timestamp
        })
        if existing:
            self.db.update_one(
                self.mining_col, {DMongo.OBJECT_ID: existing[DMongo.OBJECT_ID]}, 
                {'$set': {DMining.HASHRATE: hashrate}})
            print(f'Updated existing ({timestamp}) miner ({instance}) hashrate ({hashrate}) record')
        else:
            self.db.insert_one(self.mining_col, jdoc)
            print(f'Created a new ({timestamp}) miner ({instance}) hashrate ({hashrate}) record')