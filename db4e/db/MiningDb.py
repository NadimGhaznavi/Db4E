# db4e/MiningDb.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

# Supporting modules
from datetime import datetime

# Mining record classes
from db4e.recs.mining.BlockFoundEvent import BlockFoundEvent
from db4e.recs.mining.ChainHashrate import ChainHashrate
from db4e.recs.mining.ChainMiners import ChainMiners
from db4e.recs.mining.MinerHashrate import MinerHashrate
from db4e.recs.mining.PoolHashrate import PoolHashrate
from db4e.recs.mining.ShareFoundEvent import ShareFoundEvent
from db4e.recs.mining.SharePosition import SharePosition
from db4e.recs.mining.XMRPayment import XMRPayment


# The module that interfaces with SQLite3
from db4e.db.SQLDb import SQLDb
from db4e.db.BaseDb import BaseDb, CLASS_TO_TABLE_MAP


# Db4E logging module
from db4e.util.Db4ELogger import Db4ELogger

# Constants
from db4e.constants.DModule import DModule
from db4e.constants.DSQL import DCol, MINING_TABLE_LIST, HOURLY_MINING_TABLE_LIST


class MiningDb(BaseDb):
    """
    Mining database access layer.

    Stores and retrieves mining telemetry such as hashrates, shares,
    and payments across multiple mining-related tables.
    """

    def __init__(self, sql_db: SQLDb, log_file=None):
        """
        Initialize the mining database manager.

        :param sql_db: Initialized SQL database wrapper.
        :type sql_db: SQLDb
        :param log_file: Optional log file path.
        :type log_file: str or None
        """
        super().__init__(sql_db=sql_db, log_file=log_file)

    def add_hourly_data(self, data):
        """
        Add timestamp data for hourly records.

        :param data: Row dictionary to update in-place.
        :type data: dict
        :return: The same dictionary with timestamp fields added.
        :rtype: dict
        """
        now = datetime.now()
        data.update(
            {
                DCol.UPDATED_YEAR: now.year,
                DCol.UPDATED_MONTH: now.month,
                DCol.UPDATED_DAY: now.day,
                DCol.UPDATED_HOUR: now.hour,
            }
        )
        return data

    def add_updated_hourly_ts_column(self, table_name):
        """
        Add a computed hourly ``updated_ts`` column and index to a table.

        :param table_name: Target table name.
        :type table_name: str
        """
        # Avoid raising an exception because the column already exists
        try:
            self.sql_db.executescript(
                f"""
                ALTER TABLE {table_name}
                ADD COLUMN updated_ts INTEGER
                    GENERATED ALWAYS AS (
                        (strftime('%s', 
                            printf('%04d-%02d-%02d %02d:00:00',
                                updated_y, updated_mo, updated_d, updated_h
                            )
                        ))
                    ) VIRTUAL;
                """
            )
        except:
            pass

        index = f"idx_{table_name}_updated_ts"
        self.sql_db.executescript(
            f"""
                CREATE INDEX IF NOT EXISTS {index}
                ON {table_name}(updated_ts);    
            """
        )

    def insert_constrained_one(self, mining_object):
        """
        Insert or update an hourly mining record using its unique constraints.

        :param mining_object: Mining record instance to insert.
        :type mining_object: object
        :return: The same object with its ``id`` populated.
        :rtype: object
        """
        self.check_initialized()
        data = mining_object.to_dict()
        data = self.add_hourly_data(data)
        table_name = CLASS_TO_TABLE_MAP[type(mining_object)]
        constraint_cols = mining_object.constraints()
        columns = sorted(data.keys())
        placeholders = ", ".join(["?"] * len(columns))
        update_clause = ", ".join(
            [f"{col} = excluded.{col}" for col in columns if col not in constraint_cols]
        )
        sql = f"""
            INSERT INTO {table_name} ({", ".join(columns)})
            VALUES ({placeholders})
            ON CONFLICT ({", ".join(constraint_cols)}) DO UPDATE SET {update_clause}
        """
        values = tuple(data[col] for col in columns)
        object_id = self.sql_db.execute_insert_one(sql=sql, values=values)
        mining_object.id(object_id)
        return mining_object

    ## Add functions for mining records
    def add_block_found(self, chain):
        """
        Store a block-found event.

        :param chain: Chain identifier.
        :type chain: str
        """
        self.check_initialized()
        block_found_event = BlockFoundEvent(chain=chain)
        self.insert_one(block_found_event)

    def add_chain_hashrate(self, chain, hashrate, units):
        """
        Store historical hourly chain hashrate.

        :param chain: Chain identifier.
        :type chain: str
        :param hashrate: Hashrate value.
        :type hashrate: float
        :param units: Hashrate units.
        :type units: str
        """
        self.check_initialized()
        chain_hashrate = ChainHashrate(chain=chain, hashrate=hashrate, units=units)
        self.insert_constrained_one(chain_hashrate)

    def add_chain_miners(self, chain, num_miners):
        """
        Store historical hourly number of miners.

        :param chain: Chain identifier.
        :type chain: str
        :param num_miners: Count of miners.
        :type num_miners: int
        """
        self.check_initialized()
        chain_miners = ChainMiners(chain=chain, num_miners=num_miners)
        self.insert_constrained_one(chain_miners)

    def add_miner_hashrate(self, miner_name, chain, pool, hashrate, units):
        """
        Store the miner hashrate.

        :param miner_name: Miner identifier.
        :type miner_name: str
        :param chain: Chain identifier.
        :type chain: str
        :param pool: Pool identifier.
        :type pool: str
        :param hashrate: Hashrate value.
        :type hashrate: float
        :param units: Hashrate units.
        :type units: str
        """
        # TODO
        #
        # The miner hashrate reported by P2Pool when it is first started is extremely
        # high. If this event happens to occur just before the beginning of the hour,
        # Then this value is recorded, which throws off the overall miner hashrate.
        #
        # Don't record the miner hashrate if the upstream P2Pool has been running
        # for less than 3 minutes.
        #
        # Similarly, if the miner has just started, it will also report an very high
        # and inaccurate hashrate. Don't record the miner hashrate if the miner has been
        # running for less than 3 minutes.

        # Historical, hourly miner hashrate
        self.check_initialized()
        miner_hashrate = MinerHashrate(
            miner=miner_name,
            chain=chain,
            pool=pool,
            hashrate=hashrate,
            units=units,
        )
        self.insert_constrained_one(miner_hashrate)

    def add_pool_hashrate(self, chain, pool, hashrate, unit):
        """
        Store the pool hashrate.

        :param chain: Chain identifier.
        :type chain: str
        :param pool: Pool identifier.
        :type pool: str
        :param hashrate: Hashrate value.
        :type hashrate: float
        :param unit: Hashrate units.
        :type unit: str
        """
        self.check_initialized()
        pool_hashrate = PoolHashrate(
            chain=chain, pool=pool, hashrate=hashrate, units=unit
        )
        self.insert_constrained_one(pool_hashrate)

    def add_share_found(self, miner, effort, chain, pool):
        """
        Store a share-found event.

        :param miner: Miner identifier.
        :type miner: str
        :param effort: Effort value.
        :type effort: float
        :param chain: Chain identifier.
        :type chain: str
        :param pool: Pool identifier.
        :type pool: str
        """
        self.check_initialized()
        share_found_event = ShareFoundEvent(
            miner=miner, effort=effort, chain=chain, pool=pool
        )
        self.insert_one(share_found_event)

    def add_share_position(self, chain, pool, position):
        """
        Store the share position.

        :param chain: Chain identifier.
        :type chain: str
        :param pool: Pool identifier.
        :type pool: str
        :param position: Share position.
        :type position: int
        """
        self.check_initialized()
        share_position = SharePosition(chain=chain, pool=pool, position=position)
        self.insert_constrained_one(share_position)

    def add_to_wallet(self, amount):
        """
        Placeholder for wallet balance updates.

        :param amount: Amount to add.
        :type amount: float
        """
        # CAREFUL with datatypes here!!!
        self.check_initialized()
        # TODO

    def add_xmr_payment(self, chain, payment, pool):
        """
        Store an XMR payment.

        :param chain: Chain identifier.
        :type chain: str
        :param payment: Payment value.
        :type payment: float
        :param pool: Pool identifier.
        :type pool: str
        """
        self.check_initialized()
        xmr_payment = XMRPayment(chain=chain, payment=payment, pool=pool)
        self.insert_one(xmr_payment)

    def get_block_found_events(self, chain=None):
        """
        Fetch block-found events, optionally filtered by chain.
        """
        self.check_initialized()

    def get_chain_hashrate(self, instance):
        """
        Fetch the latest chain hashrate for an instance.
        """
        self.check_initialized()

    def get_chain_hashrates(self, instance):
        """
        Fetch historical chain hashrates for an instance.
        """
        self.check_initialized()

    def get_miner_hashrate(self, miner):
        """
        Fetch the latest miner hashrate for a miner.
        """
        self.check_initialized()

    def get_miner_hashrates(self, miner):
        """
        Fetch historical miner hashrates for a miner.
        """
        self.check_initialized()

    def get_miner_uptime(self, miner):
        """
        Fetch miner uptime details.
        """
        self.check_initialized()

    def get_payments(self):
        """
        Fetch payment records.
        """
        self.check_initialized()

    def get_pool_hashrate(self, instance):
        """
        Fetch the latest pool hashrate for an instance.
        """
        self.check_initialized()

    def get_pool_hashrates(self, instance):
        """
        Fetch historical pool hashrates for an instance.
        """
        self.check_initialized()

    def get_share_found_events(self, pool=None, miner=None):
        """
        Fetch share-found events, optionally filtered by pool or miner.
        """
        self.check_initialized()

    def get_xmrigs_remote(self):
        """
        Fetch remote XMRig records.
        """
        self.check_initialized()

    def get_share_position(self):
        """
        Fetch current share positions.
        """
        self.check_initialized()

    def get_shares(self):
        """
        Fetch share records.
        """
        self.check_initialized()

    def get_wallet_balance(self):
        """
        Fetch wallet balance.
        """
        self.check_initialized()

    def get_miners(self):
        """
        Fetch miner records.
        """
        self.check_initialized()

    def get_xmr_payments(self):
        """
        Fetch XMR payment records.
        """
        self.check_initialized()

    def _init_db(self):
        """
        Initialize mining tables in the SQLite database.
        """
        self.sql_db.executescript(
            """
            CREATE TABLE IF NOT EXISTS block_found_event (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chain TEXT,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );

            CREATE TABLE IF NOT EXISTS chain_hashrate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chain TEXT,
                hashrate REAL,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                UNIQUE (chain, updated_y, updated_mo, updated_d, updated_h)
            );

            CREATE TABLE IF NOT EXISTS chain_miners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chain TEXT,
                miners INTEGER,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                UNIQUE (chain, updated_y, updated_mo, updated_d, updated_h)
            );

            CREATE TABLE IF NOT EXISTS miner_hashrate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                miner TEXT,
                chain TEXT,
                pool TEXT,
                hashrate REAL,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                UNIQUE (miner, chain, pool, updated_y, updated_mo, updated_d, updated_h)
            );

            CREATE TABLE IF NOT EXISTS pool_hashrate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chain TEXT,
                pool TEXT,
                hashrate REAL,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                UNIQUE (chain, pool, updated_y, updated_mo, updated_d, updated_h)
            );

            CREATE TABLE IF NOT EXISTS share_found_event (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                miner TEXT,
                chain TEXT,
                pool TEXT,
                effort REAL,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );

            CREATE TABLE IF NOT EXISTS share_position (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chain TEXT,
                pool TEXT,
                share_position INTEGER,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER,
                UNIQUE (chain, pool)
            );

            CREATE TABLE IF NOT EXISTS xmr_payment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chain TEXT,
                pool TEXT,
                piconero REAL,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );
            """
        )

        # Add an hourly updated_ts column to the hourly mining tables
        for table in HOURLY_MINING_TABLE_LIST:
            self.add_updated_hourly_ts_column(table)

        # Add an updated_ts column to the remaining mining tables
        for table in MINING_TABLE_LIST:
            if table not in HOURLY_MINING_TABLE_LIST:
                self.add_updated_ts_column(table)
