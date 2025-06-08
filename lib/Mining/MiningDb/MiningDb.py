"""
lib/Mining/MiningDb/MiningDb.py
"""

# Supporting modules
import os, sys
from bson.decimal128 import Decimal128
from decimal import Decimal
from datetime import datetime

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure',
  lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from Db4eDb.Db4eDb import Db4eDb 
from Db4eConfig.Db4eConfig import Db4eConfig
from Db4eLogger.Db4eLogger import Db4eLogger

class MiningDb():

  def __init__(self):
    self._db = Db4eDb()
    self.log = Db4eLogger('MiningDb')
    
  def add_block_found(self, timestamp):
    """
    Create a JSON document and pass it to the Db4eDb to be added to the backend database
    """
    jdoc = {
      'doc_type': 'block_found_event',
      'timestamp': timestamp
    }
    db = self.db()
    db.insert_uniq_one('mining', jdoc)
    self.log.debug(f'Creating a new {timestamp} block found event record')

  def add_mainchain_hashrate(self, hashrate):
    """
    Store the mainchain hashrate
    """
    db = self.db().db()
    mining_col = db['mining']
    ## Add a "realtime" JSON doc
    myquery = {'doc_type': 'rt_mainchain_hashrate'}
    rt_timestamp = datetime.now().strftime("%H:%M")
    new_values = { "$set": {'timestamp': rt_timestamp, 'hashrate': hashrate}}
    # Initial the JSON doc i.e. create it if it doesn't exist
    self.get_mainchain_hashrate()
    mining_col.update_one(myquery, new_values)
    ## Add an hourly "historical" JSON doc
    timestamp = datetime.now().strftime("%Y-%m-%d %H")
    hourly_doc = mining_col.find_one({'doc_type': 'mainchain_hashrate', 'timestamp': timestamp})
    if hourly_doc:
      # Update the existing hourly doc
      new_values = { "$set": {'hashrate': hashrate}}
      mining_col.update_one({'_id': hourly_doc['_id']}, new_values)
      self.log.debug(f'Updated mainchain hourly ({timestamp}) hashrate ({hashrate}) record')
    else:
      # Create a new hourly doc
      hourly_doc = {
        'doc_type': 'mainchain_hashrate',
        'timestamp': timestamp,
        'hashrate': hashrate
      }
      mining_col.insert_one(hourly_doc)
      self.log.debug(f'New mainchain hourly ({timestamp}) hashrate ({hashrate} GH/s) record')
    
  def add_pool_hashrate(self, hashrate):
    """
    Store the pool hashrate
    """
    db = self.db().db()
    mining_col = db['mining']
    ## Add a "realtime" JSON doc
    myquery = {'doc_type': 'rt_pool_hashrate'}
    rt_timestamp = datetime.now().strftime("%H:%M")
    new_values = { "$set": {'timestamp': rt_timestamp, 'hashrate': hashrate}}
    # Initial the JSON doc i.e. create it if it doesn't exist
    self.get_pool_hashrate()
    mining_col.update_one(myquery, new_values)
    ## Add an hourly "historical" JSON doc
    timestamp = datetime.now().strftime("%Y-%m-%d %H")
    hourly_doc = mining_col.find_one({'doc_type': 'pool_hashrate', 'timestamp': timestamp})
    if hourly_doc:
      # Update the existing hourly doc
      new_values = { "$set": {'hashrate': hashrate}}
      mining_col.update_one({'_id': hourly_doc['_id']}, new_values)
      self.log.debug(f'Updated pool hourly ({timestamp}) hashrate ({hashrate}) record')
    else:
      # Create a new hourly doc
      hourly_doc = {
        'doc_type': 'pool_hashrate',
        'timestamp': timestamp,
        'hashrate': hashrate
      }
      mining_col.insert_one(hourly_doc)
      self.log.debug(f'New pool hourly ({timestamp}) hashrate ({hashrate} KH/s) record')
    
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
    db = self.db()
    db.insert_uniq_one('mining', jdoc)
    self.log.debug(f'New share found record', { 'miner': worker})

  def add_share_position(self, timestamp, position):
    """
    Store the share position
    """
    db = self.db().db()
    mining_col = db['mining']
    myquery = {'doc_type': 'share_position'}
    new_values = { "$set": {'timestamp': timestamp, 'position':position}}
    # Initialize the JSON doc i.e. create it if it doesn't exist
    self.get_share_position()
    mining_col.update_one(myquery, new_values)
    self.log.debug('Updated share position record')

  def add_sidechain_hashrate(self, hashrate):
    """
    Store the sidechain hashrate
    """
    db = self.db().db()
    mining_col = db['mining']
    ## Add a "realtime" JSON doc
    myquery = {'doc_type': 'rt_sidechain_hashrate'}
    rt_timestamp = datetime.now().strftime("%H:%M")
    new_values = { "$set": {'timestamp': rt_timestamp, 'hashrate': hashrate}}
    # Initialize the JSON doc i.e. create it if it doesn't exist
    self.get_sidechain_hashrate()
    mining_col.update_one(myquery, new_values)
    ## Add an hourly "historical" JSON doc
    timestamp = datetime.now().strftime("%Y-%m-%d %H")
    hourly_doc = mining_col.find_one({'doc_type': 'sidechain_hashrate', 'timestamp': timestamp})
    if hourly_doc:
      # Update the existing hourly doc
      new_values = { "$set": {'hashrate': hashrate}}
      mining_col.update_one({'_id': hourly_doc['_id']}, new_values)
      self.log.debug(f'Updated sidechain hourly ({timestamp}) hashrate ({hashrate}) record')
    else:
      # Create a new hourly doc
      hourly_doc = {
        'doc_type': 'sidechain_hashrate',
        'timestamp': timestamp,
        'hashrate': hashrate
      }
      mining_col.insert_one(hourly_doc)
      self.log.debug(f'New pool hourly ({timestamp}) hashrate record ({hashrate} MH/s)')

  def add_sidechain_miners(self, num_miners):
    """
    Store the sidechain hashrate
    """
    db = self.db().db()
    mining_col = db['mining']
    # Add an hourly "historical" JSON doc
    timestamp = datetime.now().strftime("%Y-%m-%d %H")
    hourly_doc = mining_col.find_one({'doc_type': 'sidechain_miners', 'timestamp': timestamp})
    if hourly_doc:
      # Update the existing hourly doc
      new_values = { "$set": {'num_miners': num_miners}}
      mining_col.update_one({'_id': hourly_doc['_id']}, new_values)
      self.log.debug(f'Updated hourly ({timestamp} sidechain miners ({num_miners}) record')
    else:
      # Create a new hourly doc
      hourly_doc = {
        'doc_type': 'sidechain_miners',
        'timestamp': timestamp,
        'sidechain_miners': num_miners
      }
      mining_col.insert_one(hourly_doc)
      self.log.debug(f'Updated hourly ({timestamp} sidechain miners ({num_miners}) record')

  def add_to_wallet(self, amount):
    db = self.db().db()
    mining_col = db['mining']
    myquery = {'doc_type': 'wallet_balance'}
    # get_wallet_balance() returns a "decimal" datatype 
    balance = self.get_wallet_balance()
    # Convert 'amount' to the "decimal" datatype
    amount = amount.to_decimal()
    new_balance = Decimal128(amount + balance)
    new_values = { "$set": {'balance': new_balance}}
    mining_col.update_one(myquery, new_values)
    self.log.debug(f'Updated XMR Wallet balance ({new_balance}) record')

  def add_xmr_payment(self, timestamp, payment):
    jdoc = {
      'doc_type': 'xmr_payment',
      'timestamp': timestamp,
      'payment': payment
    }
    db = self.db()
    db.insert_uniq_one('mining', jdoc)
    self.log.debug(f'New XMR payment ({payment}) record')

  def db(self):
    return self._db
  
  def get_docs(self, doc_type):
    db = self.db()
    db_cursor = db.get_docs('mining', doc_type)
    return db_cursor
  
  def get_mainchain_hashrate(self):
    db = self.db().db()
    mining_col = db['mining']
    mainchain_hashrate = mining_col.find_one({'doc_type': 'rt_mainchain_hashrate'})
    if not mainchain_hashrate:
      # Create a new doc if it doesn't already exist
      mainchain_hashrate = {
        'doc_type': 'rt_mainchain_hashrate',
        'timestamp': 'n/a',
        'hashrate': 'n/a'
      }
      mining_col.insert_one(mainchain_hashrate)
    return mainchain_hashrate

  def get_pool_hashrate(self):
    db = self.db().db()
    mining_col = db['mining']
    pool_hashrate = mining_col.find_one({'doc_type': 'rt_pool_hashrate'})
    if not pool_hashrate:
      # Create a new doc if it doesn't already exist
      pool_hashrate = {
        'doc_type': 'rt_pool_hashrate',
        'timestamp': 'n/a',
        'hashrate': 'n/a'
      }
      mining_col.insert_one(pool_hashrate)
    return pool_hashrate

  def get_share_position(self):
    db = self.db().db()
    mining_col = db['mining']
    share_position = mining_col.find_one({'doc_type': 'share_position'})
    if not share_position:
      # Create a new, empty doc to store the share position in a
      # round robin database type format
      share_position = {
        'doc_type': 'share_position',
        'timestamp': 'n/a',
        'position': 'n/a'
      }
      mining_col.insert_one(share_position)
    return share_position
  
  def get_shares(self):
    shares = self.get_docs('share_found_event')
    shares_dict = {}
    for share in shares:
      timestamp = share['timestamp']
      worker = share['worker']
      shares_dict[timestamp] = worker
    return shares_dict

  def get_sidechain_hashrate(self):
    db = self.db().db()
    mining_col = db['mining']
    sidechain_hashrate = mining_col.find_one({'doc_type': 'rt_sidechain_hashrate'})
    if not sidechain_hashrate:
      # Create a new doc if it doesn't already exist
      sidechain_hashrate = {
        'doc_type': 'rt_sidechain_hashrate',
        'timestamp': 'n/a',
        'hashrate': 'n/a'
      }
      mining_col.insert_one(sidechain_hashrate)
    return sidechain_hashrate

  def get_wallet_balance(self):
    db = self.db().db()
    mining_col = db['mining']
    balance = mining_col.find_one({'doc_type': 'wallet_balance'})
    if not balance:
      # The { doc_type: "wallet_balance", balance: <balance> } document does not exist, so
      # create it with a balance of zero.
      zero_value = Decimal128('0')
      balance = {
        'doc_type': 'wallet_balance',
        'balance': zero_value
      }
      mining_col.insert_one(balance)

    current_balance = balance['balance'].to_decimal()
    return current_balance
  
  def get_workers(self):
    workers = self.get_docs('worker')
    workers_dict = {}
    for worker in workers:
      worker_name = worker['worker_name']
      hashrate = worker['hashrate']
      timestamp = worker['timestamp']
      active = worker['active']

      workers_dict[worker_name] = {
        'worker_name': worker_name,
        'hashrate': hashrate,
        'timestamp': timestamp,
        'active': active,
      }     
    return workers_dict
  
  def get_xmr_payments(self):
    payments = self.get_docs('xmr_payment')
    payments_dict = {}
    for payment in payments:
      timestamp = payment['timestamp']
      payment = payment['payment']
      payments_dict[timestamp] = payment
    return payments_dict

  def update_worker(self, worker_name, hashrate):
    db = self.db().db()
    mining_col = db['mining']
    worker = mining_col.find_one({'doc_type': 'worker', 'worker_name': worker_name})
    timestamp = datetime.now().strftime("%H:%M")
    if not worker:
      # The document for this worker doesn't exist, create it.
      worker = {
        'doc_type': 'worker',
        'worker_name': worker_name,
        'hashrate': hashrate,
        'timestamp': timestamp,
        'active': True
      }
      mining_col.insert_one(worker)
    myquery = {'doc_type': 'worker', 'worker_name': worker_name}
    new_values = { "$set": {'hashrate': hashrate, 'timestamp': timestamp}}
    mining_col.update_one(myquery, new_values)
    worker_name = worker['worker_name']
    hashrate = worker['hashrate']
    self.log.debug(f'Updated miner ({worker_name}) hashrate ({hashrate} H/s) record')