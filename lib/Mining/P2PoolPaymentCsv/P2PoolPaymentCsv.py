"""
lib/Mining/P2PoolPaymentCsv/P2PoolPaymentCsv.py
"""

import os, sys
import datetime
from bson.decimal128 import Decimal128
from decimal import Decimal

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure',
  lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from Db4eConfig.Db4eConfig import Db4eConfig
from MiningDb.MiningDb import MiningDb
from Db4eGit.Db4eGit import Db4eGit

DB_DOC_TYPE = 'xmr_payment'

class P2PoolPaymentCsv():

  def __init__(self, log_function):
    self.log = log_function
    config = Db4eConfig()
    self._debug        = config.config['db4e']['debug']
    install_dir        = config.config['db4e']['install']
    export_dir         = config.config['export']['export_dir']
    p2pool_payouts_csv = config.config['export']['p2pool_payouts_csv']
    self._csv_filename = os.path.join(export_dir, p2pool_payouts_csv)
    self._csv_daily_filename = os.path.join(export_dir, p2pool_payouts_csv.replace('.csv', '_daily.csv'))
    self.git = Db4eGit(install_dir)

  def new_p2pool_payment_csv(self):
    if self._debug == 9:
      self.log("P2PoolPaymentCsv.new_p2pool_payment_csv()")
    db = MiningDb()
    payouts = db.get_docs('xmr_payment')
    if self._debug == 9:
      self.log("P2PoolPaymentCsv.new_p2pool_payment_csv()")
      self.log(f"  payouts         : ({payouts})")

    payouts_list = []
    for payout in payouts:
      if self._debug == 9:
        self.log("P2PoolPaymentCsv.new_p2pool_payment_csv()")
        self.log(f"  payout         : ({payout})")

      timestamp = payout['timestamp'].date()
      payment = Decimal(payout['payment'].to_decimal())
      payouts_list.append([timestamp, payment])

    payouts_list.sort()

    cur_date = ""
    new_dict = {}
    earliest_date = ""
    latest_date = ""
    first_time = True
    for x in payouts_list:
      if self._debug == 9:
        self.log("P2PoolPaymentCsv.new_p2pool_payment_csv()")
        self.log(f"  payout         : ({x})")

      cur_date = x[0]
      if first_time:
        earliest_date = cur_date
        latest_date = cur_date
        first_time = False

      if cur_date < earliest_date:
        earliest_date = cur_date

      if cur_date > latest_date:
        latest_date = cur_date

      cur_amount = Decimal128(str(x[1])).to_decimal()
      if cur_date in new_dict.keys():
        new_dict[cur_date] = new_dict[cur_date] + cur_amount
      else:
        new_dict[cur_date] = cur_amount

    dates = []
    for x in range(int((latest_date - earliest_date).days)+1):
      date = earliest_date + datetime.timedelta(days=x)
      dates.append(date)

    for day in dates:
      if day not in new_dict.keys():
        new_dict[day] = 0

    dates.sort()

    # Create the Cumulative and Daily P2Pool Payouts CSV files
    csv_filename = self._csv_filename
    csv_daily_filename = self._csv_daily_filename
    
    try:
      csv_handle = open(csv_filename, 'w')
    except:
      self.log(f"ERROR: Unable to open P2Pool Payouts CSV ({csv_filename})")
    try:
      csv_daily_handle = open(csv_daily_filename, 'w')
    except:
      self.log(f"ERROR: Unable to open P2Pool Payouts CSV ({csv_daily_filename})")

    
    csv_header = "Date,Total\n"
    csv_handle.write(csv_header)
    csv_daily_handle.write(csv_header)
    total = Decimal128("0").to_decimal()
    for day in dates:
      total = total + new_dict[day]
      rounded_total = round(total, 4)
      daily = new_dict[day]
      csv_handle.write(str(day) + "," + str(rounded_total) + "\n")
      csv_daily_handle.write(str(day) + "," + str(daily) + "\n")
    csv_handle.close()
    csv_daily_handle.close()
    
    # Create a shorter version of the Cumulative CSV files, last 30 days
    short_csv_filename = csv_filename.replace('.csv', '_short.csv')
    csv_short_handle = open(short_csv_filename, 'w')
    csv_short_handle.write(csv_header)
    # Get the last 30 days of data
    csv_handle = open(csv_filename, 'r')
    lines = csv_handle.readlines()
    datapoints = 30  # 30 days of data
    for line in lines[-datapoints:]:
      csv_short_handle.write(line)
    csv_short_handle.close()
    csv_handle.close()

    # Create a shorter version of the Daily CSV files, last 30 days
    short_csv_daily_filename = csv_daily_filename.replace('.csv', '_short.csv')
    csv_short_handle = open(short_csv_daily_filename, 'w')
    csv_short_handle.write(csv_header)
    # Get the last 30 days of data
    csv_handle = open(csv_daily_filename, 'r')
    lines = csv_handle.readlines()
    datapoints = 30  # 30 days of data
    for line in lines[-datapoints:]:
      csv_short_handle.write(line)
    csv_short_handle.close()
    csv_handle.close()

    # Push the CSV file to the git repository
    db4e_git = Db4eGit()
    db4e_git.push(csv_filename, 'Updated P2Pool Payouts')
    db4e_git.push(short_csv_filename, 'Updated P2Pool Payouts')
    db4e_git.push(csv_daily_filename, 'Updated P2Pool Payouts Daily')
    db4e_git.push(short_csv_daily_filename, 'Updated P2Pool Payouts Daily')

    # Log the CSV file paths
    self.log(f"  Payouts CSV      : {csv_filename}")
    self.log(f"  Payouts CSV      : {short_csv_filename}")
    self.log(f"  Payouts CSV      : {csv_daily_filename}")
    self.log(f"  Payouts CSV      : {short_csv_daily_filename}")
    
