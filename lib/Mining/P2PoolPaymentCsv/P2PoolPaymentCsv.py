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

from Db4eStartup.Db4eStartup import Db4eStartup
from MiningDb.MiningDb import MiningDb
from Db4eGit.Db4eGit import Db4eGit

class P2PoolPaymentCsv():

  def __init__(self, log_function):
    startup = Db4eStartup()
    self._debug = startup.debug()
    self.log = log_function

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

    startup = Db4eStartup()
    csv_filename = startup.p2pool_payouts_csv()
    try:
      csv_handle = open(csv_filename, 'w')
      # print(f"Preparing to write to CSV file ({csv_filename})")
    except:
      self.log(f"ERROR: Unable to open P2Pool Payouts CSV ({csv_filename})")

    csv_handle.write("Date,Total\n")
    # print("Date,Total") 
    total = Decimal128("0").to_decimal()
    for day in dates:
      total = total + new_dict[day]
      rounded_total = round(total, 4)
      # print(f"rounded_total: {rounded_total}")
      # print(f"{str(day)},{str(rounded_total)}")
      csv_handle.write(str(day) + "," + str(rounded_total) + "\n")
    
    csv_handle.close()
    db4e_git = Db4eGit()
    db4e_git.push(csv_filename, 'Updated P2Pool Payouts')
    self.log(f"  Payouts CSV      : {csv_filename}")
    
