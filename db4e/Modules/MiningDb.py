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
from db4e.Modules.OpsDb import OpsETL
from db4e.Modules.XMRigRemote import XMRigRemote

from db4e.Constants.DDef import DDef
from db4e.Constants.DMongo import DMongo
from db4e.Constants.DMining import DMining
from db4e.Constants.DModule import DModule
from db4e.Constants.DDebug import DDebug
from db4e.Constants.DField import DField
from db4e.Constants.DElem import DElem
from db4e.Constants.DLabel import DLabel




DDebug.FUNCTION = True


class MiningDb():


    def __init__(self, db: DbMgr, ops_etl: OpsETL, log_file=None):
        self.db = db
        self.ops_etl = ops_etl
        self.mining_col = DDef.MINING_COL
        if log_file:
            self.log = Db4ELogger(db4e_module=DModule.MINING_DB, log_file=log_file)
    

    def add_block_found(self, timestamp, chain, instance):
        """
        Block found record
        """
        jdoc = {
            DMongo.DOC_TYPE: DMining.BLOCK_FOUND_EVENT,
            DMongo.CHAIN: chain,
            DMongo.INSTANCE: instance,
            DMongo.TIMESTAMP: timestamp
        }
        self.db.insert_uniq_by_timestamp(self.mining_col, jdoc)
        self.log.info(f"Creating a new ({chain}) block found event record")


    def add_chain_hashrate(self, chain, instance, hashrate, unit):
        """
        Historical and real-time chain hashrate record
        """
        # Convert the hashrate to a float
        hashrate = float(hashrate)

        # Update the "realttime" (rt) record first
        rt_timestamp = datetime.now(timezone.utc)
        jdoc = {
            DMongo.DOC_TYPE: DMining.RT_HASHRATE,
            DMongo.CHAIN: chain,
            DMongo.INSTANCE: instance,
            DMongo.TIMESTAMP: rt_timestamp,
            DMining.HASHRATE: hashrate,
            DMining.UNIT: unit
        }

        existing = self.db.find_one(self.mining_col, {
            DMongo.DOC_TYPE: DMining.RT_HASHRATE, DMongo.CHAIN: chain })
        
        if existing:
            self.db.update_one(
                self.mining_col, { DMongo.OBJECT_ID: existing[DMongo.OBJECT_ID] }, 
                { DMining.HASHRATE: hashrate, DMongo.TIMESTAMP: rt_timestamp, DMongo.INSTANCE: instance})
            self.log.debug(f"Updated existing ({chain}) real-time {chain} hashrate ({hashrate}) record")

        else:
            self.db.insert_one(self.mining_col, jdoc)
            self.log.info(f"Created new ({chain})real-time hashrate ({hashrate}) record")

        # Update the historical, hourly record
        timestamp = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        jdoc = {
            DMongo.DOC_TYPE: DMining.HASHRATE,
            DMongo.CHAIN: chain,
            DMongo.TIMESTAMP: timestamp,
            DMongo.INSTANCE: instance,
            DMining.HASHRATE: hashrate,
            DMining.UNIT: unit
        }

        existing = self.db.find_one(self.mining_col, {
            DMongo.DOC_TYPE: DMining.HASHRATE, DMongo.CHAIN: chain, 
            DMongo.TIMESTAMP: timestamp, DMongo.INSTANCE: instance
        })

        if existing:
            self.db.update_one(
                self.mining_col, {DMongo.OBJECT_ID: existing[DMongo.OBJECT_ID]},
                {DMining.HASHRATE: hashrate })
            self.log.debug(f"Updated existing ({chain}) historical hashrate ({hashrate}) record")

        else:
            self.db.insert_one(self.mining_col, jdoc)
            self.log.info(f"Created new ({chain}) historical hashrate ({hashrate}) record")


    def add_chain_miners(self, chain, num_miners):
        """
        Store the number of unique wallets on the sidechain
        """
        # Convert the num_miners to an int
        num_miners = int(num_miners)

        # Update the historical, hourly record
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
            self.log.debug(f"Updated existing {chain} miners ({num_miners}) record")
        else:
            self.db.insert_one(self.mining_col, jdoc)
            self.log.info(f"Created new {chain} miners ({num_miners}) record")


    def add_miner_hashrate(
            self, chain, miner_name, ip_addr, hashrate, uptime, timestamp, p2pool_instance):
        """
        Store the miner hashrate
        """
        # The miner hashrate reported by P2Pool when it is first started is extremely
        # high. If this event happens to occur just before the beginning of the hour,
        # Then this value is recorded, which throws off the overall miner hashrate.
        #
        # Don't record the miner hashrate if the upstream P2Pool has been running
        # for less than 3 minutes.
        minutes = self.ops_etl.get_uptime(elem_type=DElem.P2POOL, instance=p2pool_instance)
        if minutes is None or minutes < 3:
            return

        # Convert the hashrate to a float
        hashrate = float(hashrate)

        # Historical, hourly miner hashrate
        timestamp = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        jdoc = {
            DMongo.DOC_TYPE: DMining.MINER_HASHRATE,
            DMongo.CHAIN: chain,
            DMongo.TIMESTAMP: timestamp,
            DMining.MINER: miner_name,  
            DMongo.IP_ADDR: ip_addr,
            DMining.HASHRATE: hashrate,
        }

        existing = self.db.find_one(self.mining_col, {
            DMongo.DOC_TYPE: DMining.MINER_HASHRATE,
            DMongo.CHAIN: chain,
            DMining.MINER: miner_name,
            DMongo.TIMESTAMP: timestamp
        })

        if existing:
            self.db.update_one(
                self.mining_col, {DMongo.OBJECT_ID: existing[DMongo.OBJECT_ID]},
                {DMining.HASHRATE: hashrate, DMongo.IP_ADDR: ip_addr})
            self.log.debug(f"Updated existing ({chain}) historical miner ({miner_name}) hashrate ({hashrate}) record")
        else:
            self.db.insert_one(self.mining_col, jdoc)
            self.log.info(f"Created new ({chain}) historical miner ({miner_name}) hashrate ({hashrate}) record")
        
        # Real-time, miner hashrate
        rt_timestamp = datetime.now(timezone.utc)
        jdoc = {
            DMongo.DOC_TYPE: DMining.RT_MINER_HASHRATE,
            DMongo.CHAIN: chain,
            DMongo.TIMESTAMP: rt_timestamp,
            DMongo.IP_ADDR: ip_addr,
            DMining.MINER: miner_name,
            DMining.HASHRATE: hashrate,
            DMongo.UPTIME: uptime,
        }

        existing = self.db.find_one(self.mining_col, {
            DMongo.DOC_TYPE: DMining.RT_MINER_HASHRATE,
            DMongo.CHAIN: chain,
            DMining.MINER: miner_name,
        })

        if existing:
            self.db.update_one(
                self.mining_col, {DMongo.OBJECT_ID: existing[DMongo.OBJECT_ID] },
                {DMining.HASHRATE: hashrate, DMongo.IP_ADDR: ip_addr, DMongo.TIMESTAMP: rt_timestamp, DMongo.UPTIME: uptime})
            self.log.debug(f"Updated existing ({chain}) real-time miner ({miner_name}) hashrate ({hashrate}) record")
        else:
            self.db.insert_one(self.mining_col, jdoc)
            self.log.info(f"Created new ({chain}) real-time miner ({miner_name}) hashrate ({hashrate}) record")
                          


    def add_pool_hashrate(self, chain, instance, hashrate, unit):
        """
        Store the pool hashrate
        """
        # Convert the hashrate to a float
        hashrate = float(hashrate)

        # Update the "realtime" (rt) record first
        rt_timestamp = datetime.now(timezone.utc)
        jdoc = {
            DMongo.DOC_TYPE: DMining.RT_POOL_HASHRATE,
            DMongo.CHAIN: chain,
            DMining.INSTANCE: instance,
            DMongo.TIMESTAMP: rt_timestamp,
            DMongo.HASHRATE: hashrate,
            DMining.UNIT: unit
        }
        existing = self.db.find_one(self.mining_col, {
              DMongo.DOC_TYPE: DMining.RT_POOL_HASHRATE,
        })
        if existing:
            self.db.update_one(
                self.mining_col, {DMongo.OBJECT_ID: existing[DMongo.OBJECT_ID]},
                {DMining.HASHRATE: hashrate, DMongo.TIMESTAMP: rt_timestamp})
            self.log.debug(f"Updated existing ({chain}) real-time pool hashrate ({hashrate}) record")
        else:
            self.db.insert_one(self.mining_col, jdoc)
            self.log.info(f"Created new ({chain}) real-time pool hashrate ({hashrate}) record")

        # Update the historical, hourly record next
        timestamp = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        jdoc = {
            DMongo.DOC_TYPE: DMining.POOL_HASHRATE,
            DMongo.CHAIN: chain,
            DMining.INSTANCE: instance,
            DMongo.TIMESTAMP: timestamp,
            DMongo.HASHRATE: hashrate,
            DMining.UNIT: unit
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
            self.log.debug(f"Updated existing ({chain}) historical pool hashrate ({hashrate}) record")
        else:
            self.db.insert_one(self.mining_col, jdoc)
            self.log.info(f"Created new ({chain}) historical pool hashrate ({hashrate}) record")


    def add_share_found(self, chain, timestamp, miner, ip_addr, effort):
        """
        Create a JSON document and pass it to the Db4eDb to be added to the backend database
        """
        # Convert the effort to a float
        effort = float(effort)

        jdoc = {
            DMongo.DOC_TYPE: DMining.SHARE_FOUND_EVENT,
            DMongo.TIMESTAMP: timestamp,
            DMongo.MINER: miner,
            DMongo.CHAIN: chain,
            DMongo.IP_ADDR: ip_addr,
            DMining.EFFORT: effort
        }
        self.db.insert_uniq_by_timestamp(self.mining_col, jdoc)
        self.log.info(f"New ({chain}) share found by miner ({miner}) record", { DMining.MINER: miner })


    def add_share_position(self, chain, timestamp, position):
        """
        Store the share position
        """
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
                {DMongo.TIMESTAMP: timestamp, DMining.SHARE_POSITION: position})
            self.log.debug(f"Updated ({chain}) share position ({position}) record")

        else:
            self.db.insert_one(self.mining_col, jdoc)
            self.log.info(f"Created a new ({chain}) share position ({position}) record")


    def add_to_wallet(self, amount):
        # CAREFUL with datatypes here!!!
        amount = amount.to_decimal()
        balance = self.get_wallet_balance().to_decimal() # This call ensures the DB record exists
        new_balance = Decimal128(amount + balance)
        dbRec = self.db.find_one(self.mining_col, {DMongo.DOC_TYPE: DMining.WALLET_BALANCE})
        self.db.update_one(
            self.mining_col, {DMongo.OBJECT_ID: dbRec[DMongo.OBJECT_ID]},
            {DMining.WALLET_BALANCE: new_balance})
        self.log.info(f"Added {amount} to wallet balance. New balance: {new_balance}")


    def add_xmr_payment(self, chain, timestamp, payment):
        jdoc = {
            DMongo.DOC_TYPE: DMining.XMR_PAYMENT,
            DMongo.CHAIN: chain,
            DMongo.TIMESTAMP: timestamp,
            DMining.XMR_PAYMENT: payment
        }
        if self.db.insert_uniq_by_timestamp(self.mining_col, jdoc):
            self.add_to_wallet(payment)
        self.log.info(f"Added new ({chain}) XMR payment ({payment}) record)")


    def get_block_found_events(self, instance):
        return self.db.find_many(
            self.mining_col, 
            { DMongo.DOC_TYPE: DMining.BLOCK_FOUND_EVENT, DMongo.INSTANCE: instance },
            { DMongo.TIMESTAMP: 1 })


    def get_chain_hashrate(self, instance):
        return self.db.find_one(
            self.mining_col, 
            { DMongo.DOC_TYPE: DMining.RT_HASHRATE, DMongo.INSTANCE: instance })
    

    def get_chain_hashrates(self, instance):
        return self.db.find_many(
            self.mining_col, 
            { DMongo.DOC_TYPE: DMining.HASHRATE, DMongo.INSTANCE: instance },
            { DMongo.TIMESTAMP: 1 })
    

    def get_miner_hashrate(self, miner):
        return self.db.find_one(
            self.mining_col,
            { DMongo.DOC_TYPE: DMining.RT_MINER_HASHRATE, DMining.MINER: miner})


    def get_miner_hashrates(self, miner):
        return self.db.find_many(
            self.mining_col,
            { DMongo.DOC_TYPE: DMining.MINER_HASHRATE, DMining.MINER: miner},
            { DMongo.TIMESTAMP: 1 })


    def get_miner_uptime(self, miner):
        return self.db.find_one(
            self.mining_col,
            { DMongo.DOC_TYPE: DMining.RT_MINER_HASHRATE, DMining.MINER: miner})


    def get_pool_hashrate(self, instance):
        return self.db.find_one(
            self.mining_col, {DMongo.DOC_TYPE: DMining.RT_POOL_HASHRATE, DMongo.INSTANCE: instance})


    def get_pool_hashrates(self, instance):
        return self.db.find_many(
            self.mining_col, 
            { DMongo.DOC_TYPE: DMining.POOL_HASHRATE, DMongo.INSTANCE: instance },
            { DMongo.TIMESTAMP: 1 })


    def get_xmrigs_remote(self):
        recs = self.db.find_many(self.mining_col, {
            DMongo.DOC_TYPE: DMining.RT_MINER_HASHRATE})
        recs_list = []
        for aRec in recs:
            new_rec = {
                DField.ELEMENT_TYPE: DElem.XMRIG_REMOTE,
                DField.OBJECT_ID: aRec[DMongo.OBJECT_ID],
                DField.COMPONENTS: [
                    {
                        DField.FIELD: DField.INSTANCE,
                        DField.LABEL: DLabel.INSTANCE,
                        DField.VALUE: aRec[DMining.MINER]
                    },
                    {
                        DField.FIELD: DField.IP_ADDR,
                        DField.LABEL: DLabel.IP_ADDR,
                        DField.VALUE: aRec[DMongo.IP_ADDR]
                    },
                    {
                        DField.FIELD: DField.REMOTE,
                        DField.LABEL: DLabel.REMOTE,
                        DField.VALUE: True
                    },
                    {
                        DField.FIELD: DField.HASHRATE,
                        DField.LABEL: DLabel.HASHRATE,
                        DField.VALUE: aRec[DMining.HASHRATE]
                    },
                    {
                        DField.FIELD: DField.TIMESTAMP,
                        DField.LABEL: DLabel.TIMESTAMP,
                        DField.VALUE: aRec[DMongo.TIMESTAMP]
                    },
                    {
                        DField.FIELD: DField.UPTIME,
                        DField.LABEL: DLabel.UPTIME,
                        DField.VALUE: aRec[DMongo.UPTIME]
                    }
                ],
            }
            recs_list.append(new_rec)
        return recs_list


    def get_share_position(self):
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


    def get_shares(self):
        dbCursor = self.db.find_many(
            self.mining_col, {DMongo.DOC_TYPE: DMining.SHARE_FOUND_EVENT})
        resDict = {}
        for share in dbCursor:
            timestamp = share[DMongo.TIMESTAMP]
            miner = share[DMining.MINER]
            resDict[timestamp] = miner
        return resDict


    def get_wallet_balance(self):
        record = self.db.find_one(
            self.mining_col, {DMongo.DOC_TYPE: DMining.WALLET_BALANCE})

        if record:
            return record[DMining.WALLET_BALANCE]

        jdoc = {DMongo.DOC_TYPE: DMining.WALLET_BALANCE,
                DMining.WALLET_BALANCE: Decimal128("0") }
        self.db.insert_one(self.mining_col, jdoc)
        return Decimal128("0")
  

    def get_miners(self):
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


    def get_rt_miner_rec(self, instance):
        return self.db.find_one(
            self.mining_col, {DMongo.DOC_TYPE: DMining.RT_MINER_HASHRATE, 
                              DMining.MINER: instance})
  

    def get_xmr_payments(self):
        payments_cursor = self.db.find_many(
            self.mining_col, {DMongo.DOC_TYPE: DMining.XMR_PAYMENT})
        payments_dict = {}
        for payment in payments_cursor:
            timestamp = payment[DMongo.TIMESTAMP]
            payment = payment[DMining.XMR_PAYMENT]
            payments_dict[timestamp] = payment
        return payments_dict


