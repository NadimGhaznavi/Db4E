"""
lib/MiningDb/MiningDb.py

This module is part of the Data Abstraction Layer. All *db4e* mining operations
that result in a database operation go through this module. This module, in turn,
communicates with the Db4eDb module to access MongoDB.


  This file is part of *db4e*, the *Database 4 Everything* project
  <https://github.com/NadimGhaznavi/db4e>, developed independently
  by Nadim-Daniel Ghaznavi. Copyright (c) 2024-2025 NadimGhaznavi
  <https://github.com/NadimGhaznavi/db4e>.
 
  This program is free software: you can redistribute it and/or 
  modify it under the terms of the GNU General Public License as 
  published by the Free Software Foundation, version 3.
 
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  General Public License for more details.

  You should have received a copy (LICENSE.txt) of the GNU General 
  Public License along with this program. If not, see 
  <http://www.gnu.org/licenses/>.
"""


# Supporting modules
import os, sys
from bson.decimal128 import Decimal128
from decimal import Decimal
from datetime import datetime, timezone

# Where the DB4E modules live
lib_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(lib_dir)

# Import DB4E modules
from Db4eDb.Db4eDb import Db4eDb 
from Db4eConfig.Db4eConfig import Db4eConfig
from Db4eLogger.Db4eLogger import Db4eLogger

class MiningDb():

  def __init__(self):
    self._db = Db4eDb()
    self.log = Db4eLogger('MiningDb')
    self._col = self._db.get_collection(self._db._db_collection)
    
  def add_block_found(self, timestamp):
    """
    Create a block found record
    """
    jdoc = {
      'doc_type': 'block_found_event',
      'timestamp': timestamp
    }
    self._db.insert_uniq_by_timestamp(self._col, jdoc)
    self.log.debug(f'Creating a new {timestamp} block found event record')

  def add_mainchain_hashrate(self, hashrate):
    """
    Store the mainchain hashrate
    """
    # Update the 'realtime' (rt) record first
    rt_timestamp = datetime.now(timezone.utc)
    jdoc = {
      'doc_type': 'rt_mainchain_hashrate',
      'timestamp': rt_timestamp,
      'hashrate': hashrate
    }
    existing = self._db.find_one(self._col, {
      'doc_type': 'rt_mainchain_hashrate',
    })
    if existing:
      self._db.update_one(self._col, {'_id': existing['_id']},
                          {'$set': {'hashrate': hashrate, 'timestamp': rt_timestamp}})
      self.log.debug(f'Updated existing real-time mainchain hashrate ({hashrate}) record')
    else:
      self._db.insert_one(self._col, jdoc)
      self.log.debug(f'Created new real-time mainchain hashrate ({hashrate}) record')

    # Update the historical, hourly record next
    timestamp = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    jdoc = {
      'doc_type': 'mainchain_hashrate',
      'timestamp': timestamp,
      'hashrate': hashrate
    }
    existing = self._db.find_one(self._col, {
      'doc_type': 'mainchain_hashrate',
      'timestamp': timestamp
    })
    if existing:
      self._db.update_one(self._col, {'_id': existing['_id']},
                          {'$set': {'hashrate': hashrate }})
      self.log.debug(f'Updated existing mainchain hashrate ({hashrate}) record')
    else:
      self._db.insert_one(self._col, jdoc)
      self.log.debug(f'Created new real-time mainchain hashrate ({hashrate}) record')
    
  def add_pool_hashrate(self, hashrate):
    """
    Store the pool hashrate
    """
    # Update the 'realtime' (rt) record first
    rt_timestamp = datetime.now(timezone.utc)
    jdoc = {
      'doc_type': 'rt_pool_hashrate',
      'timestamp': rt_timestamp,
      'hashrate': hashrate
    }
    existing = self._db.find_one(self._col, {
      'doc_type': 'rt_pool_hashrate',
    })
    if existing:
      self._db.update_one(self._col, {'_id': existing['_id']},
                          {'$set': {'hashrate': hashrate, 'timestamp': rt_timestamp}})
      self.log.debug(f'Updated existing real-time pool hashrate ({hashrate}) record')
    else:
      self._db.insert_one(self._col, jdoc)
      self.log.debug(f'Created new real-time pool hashrate ({hashrate}) record')

    # Update the historical, hourly record next
    timestamp = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    jdoc = {
      'doc_type': 'pool_hashrate',
      'timestamp': timestamp,
      'hashrate': hashrate
    }
    existing = self._db.find_one(self._col, {
      'doc_type': 'pool_hashrate',
      'timestamp': timestamp
    })
    if existing:
      self._db.update_one(self._col, {'_id': existing['_id']},
                          {'$set': {'hashrate': hashrate }})
      self.log.debug(f'Updated existing pool hashrate ({hashrate}) record')
    else:
      self._db.insert_one(self._col, jdoc)
      self.log.debug(f'Created new real-time pool hashrate ({hashrate}) record')
    
  def add_share_found(self, timestamp, worker, ip_addr, effort):
    """
    Create a JSON document and pass it to the Db4eDb to be added to the backend database
    """
    jdoc = {
      'doc_type': 'share_found_event',
      'timestamp': timestamp,
      'worker': worker,
      'ip_addr': ip_addr,
      'effort': effort
    }
    self._db.insert_uniq_by_timestamp(self._col, jdoc)
    self.log.debug(f'New share found record', { 'miner': worker })

  def add_share_position(self, timestamp, position):
    """
    Store the share position
    """
    # TODO update P2Pool to stop including the timestamp
    timestamp = datetime.now(timezone.utc)
    jdoc = {
      'doc_type': 'share_position',
      'timestamp': timestamp,
      'position' : position
    }
    existing = self._db.find_one(self._col, {'doc_type': 'share_position'})
    if existing:
      self._db.update_one(self._col, {'_id': existing['_id']},
                          {'$set': {'timestamp': timestamp,
                                    'position': position}})
      self.log.debug(f'Updated share position ({position}) record')
    else:
      self._db.insert_one(self._col, jdoc)
      self.log.debug(f'Created a new share position ({position}) record')

  def add_sidechain_hashrate(self, hashrate):
    """
    Store the sidechain hashrate
    """
    # Update the 'realtime' (rt) record first
    rt_timestamp = datetime.now(timezone.utc)
    jdoc = {
      'doc_type': 'rt_sidechain_hashrate',
      'timestamp': rt_timestamp,
      'hashrate': hashrate
    }
    existing = self._db.find_one(self._col, {
      'doc_type': 'rt_sidechain_hashrate',
    })
    if existing:
      self._db.update_one(self._col, {'_id': existing['_id']},
                          {'$set': {'hashrate': hashrate, 'timestamp': rt_timestamp}})
      self.log.debug(f'Updated existing real-time sidechain hashrate ({hashrate}) record')
    else:
      self._db.insert_one(self._col, jdoc)
      self.log.debug(f'Created new real-time sidechain hashrate ({hashrate}) record')

    # Update the historical, hourly record next
    timestamp = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    jdoc = {
      'doc_type': 'sidechain_hashrate',
      'timestamp': timestamp,
      'hashrate': hashrate
    }
    existing = self._db.find_one(self._col, {
      'doc_type': 'sidechain_hashrate',
      'timestamp': timestamp
    })
    if existing:
      self._db.update_one(self._col, {'_id': existing['_id']},
                          {'$set': {'hashrate': hashrate }})
      self.log.debug(f'Updated existing sidechain hashrate ({hashrate}) record')
    else:
      self._db.insert_one(self._col, jdoc)
      self.log.debug(f'Created new real-time sidechain hashrate ({hashrate}) record')

  def add_sidechain_miners(self, num_miners):
    """
    Store the number of unique wallets on the sidechain
    """
    timestamp = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    jdoc = {
      'doc_type': 'sidechain_miners',
      'timestamp': timestamp,
      'sidechain_miners': num_miners
    }
    existing = self._db.find_one(self._col, {
      'doc_type': 'sidechain_miners',
      'timestamp': timestamp
    })
    if existing:
      self._db.update_one(self._col, {'_id': existing['_id']},
                          {'$set': {'sidechain_miners': num_miners}})
      self.log.debug(f'Updated existing sidechain miners ({num_miners}) record')
    else:
      self._db.insert_one(self._col, jdoc)
      self.log.debug(f'Updated existing sidechain miners ({num_miners}) record')

  def add_to_wallet(self, amount):
    # CAREFUL with datatypes here!!!
    amount = amount.to_decimal()
    balance = self.get_wallet_balance().to_decimal() # This call ensures the DB record exists
    new_balance = Decimal128(amount + balance)
    dbRec = self._db.find_one(self._col, {'doc_type': 'wallet_balance'})
    self._db.update_one(self._col, {'_id': dbRec['_id']},
                        {'$set': {'balance': new_balance}})
    self.log.debug(f'Updated XMR Wallet balance ({new_balance}) record')

  def add_xmr_payment(self, timestamp, payment):
    jdoc = {
      'doc_type': 'xmr_payment',
      'timestamp': timestamp,
      'payment': payment
    }
    if self._db.insert_uniq_by_timestamp(self._col, jdoc):
      self.add_to_wallet(payment)

    self.log.debug(f'New XMR payment ({payment}) record')

  def get_docs(self, doc_type):
    dbCursor = self._db.find_many(self._col, {'doc_type': doc_type})
    return dbCursor
  
  def get_mainchain_hashrate(self):
    record = self._db.find_one(self._col, {'doc_type': 'rt_mainchain_hashrate'})
    if record:
      return record
    else:
      # Create a new doc if it doesn't already exist
      jdoc = {
        'doc_type': 'rt_mainchain_hashrate',
        'timestamp': None,
        'hashrate': None
      }
      self._db.insert_one(jdoc)
      self.log.debug(f'Created new (rt_mainchain_hashrate) record')
      return None

  def get_pool_hashrate(self):
    record = self._db.find_one(self._col, {'doc_type': 'rt_pool_hashrate'})
    if record:
      return record
    else:
      # Create a new doc if it doesn't already exist
      jdoc = {
        'doc_type': 'rt_pool_hashrate',
        'timestamp': None,
        'hashrate': None
      }
      self._db.insert_one(jdoc)
      self.log.debug(f'Created new (rt_pool_hashrate) record')
      return None

  def get_share_position(self):
    record = self._db.find_one(self._col, {'doc_type': 'share_position'})
    if not record:
      jdoc = {
        'doc_type': 'share_position',
        'timestamp': None,
        'position': None
      }
      self._db.insert_one(self._col, jdoc)
      self.log.debug(f'Created a new (share_position) record')
    else:
      return record
  
  def get_shares(self):
    dbCursor = self._db.find_many(self._col, {'doc_type': 'share_found_event'})
    resDict = {}
    for share in dbCursor:
      timestamp = share['timestamp']
      worker = share['worker']
      resDict[timestamp] = worker
    return resDict

  def get_sidechain_hashrate(self):
    record = self._db.find_one(self._col, {'doc_type': 'rt_sidechain_hashrate'})
    if record:
      return record
    else:
      # Create a new doc if it doesn't already exist
      jdoc = {
        'doc_type': 'rt_sidechain_hashrate',
        'timestamp': None,
        'hashrate': None
      }
      self._db.insert_one(jdoc)
      self.log.debug(f'Created new (rt_sidechain_hashrate) record')
      return None            

  def get_wallet_balance(self):
    record = self._db.find_one(self._col, {'doc_type': 'wallet_balance'})
    if not record:
      jdoc = {'doc_type': 'wallet_balance',
              'balance': Decimal128('0') }
      self._db.insert_one(self._col, jdoc)
      self.log.debug(f'Created a new (wallet_balance) record with balance (0)')
      return Decimal128('0')
    else:
      return record['balance']
  
  def get_workers(self):
    dbCursor = self._db.find_many(self._col, {'doc_type': 'worker'})
    resDict = {}
    for worker in dbCursor:
      worker_name = worker['worker_name']
      hashrate = worker['hashrate']
      timestamp = worker['timestamp']
      active = worker['active']
      resDict[worker_name] = {
        'worker_name': worker_name,
        'hashrate': hashrate,
        'timestamp': timestamp,
        'active': active,
      }     
    return resDict
  
  def get_xmr_payments(self):
    payments_cursor = self._db.find_many(self._col, {'doc_type': 'xmr_payment'})
    payments_dict = {}
    for payment in payments_cursor:
      timestamp = payment['timestamp']
      payment = payment['payment']
      payments_dict[timestamp] = payment
    return payments_dict

  def update_worker(self, worker_name, hashrate):
    timestamp = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    jdoc = {
      'doc_type': 'worker',
      'worker_name': worker_name,
      'hashrate': hashrate,
      'timestamp': timestamp,
      'active': True
    }
    existing = self._db.find_one(self._col, {
      'doc_type': 'worker',
      'worker_name': worker_name,
      'timestamp': timestamp
    })
    if existing:
      self._db.update_one(self._col, {'_id': existing['_id']}, 
                          {'$set': {'hashrate': hashrate}}
      )
      self.log.debug(f'Updated existing ({timestamp}) miner ({worker_name}) hashrate ({hashrate}) record')
    else:
      self._db.insert_one(self._col, jdoc)
      self.log.debug(f'Created a new ({timestamp}) miner ({worker_name}) hashrate ({hashrate}) record')