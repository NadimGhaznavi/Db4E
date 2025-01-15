"""
lib/Mining/SharesFoundByHostCsv/SharesFoundByHostCsv.py
"""

import os, sys
import datetime

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

class SharesFoundByHostCsv():

  def __init__(self, log_function):
    startup = Db4eStartup()
    self._debug = startup.debug()
    self.log_msg = log_function

  def new_shares_found_by_host_csv(self):
    if self._debug == 9:
      self.log_msg("SharesFoundByHostCsv.new_shares_found_by_host_csv()")
    db = MiningDb()
    shares_found = db.get_docs('share_found_event')
    
    kermit_dict = {}
    sally_dict = {}
    paris_dict = {}
    maia_dict = {}
    bingo_dict = {}
    brat_dict = {}
    phoebe_dict = {}

    first_event = True
    first_day = None
    last_day = None
    
    hosts = ['kermit', 'sally', 'paris', 'maia', 'bingo', 'brat', 'phoebe']

    dicts = {}
    for aHost in hosts:
      dicts[aHost] = {}

    #self.log_msg(f"{str(dicts)}")
    
    for event in shares_found:
      #timestamp = event['timestamp'].strftime("%Y-%m-%d")
      timestamp = event['timestamp']
      worker = event['worker']

      timestamp = timestamp.replace(hour=0, minute=0,second=0,microsecond=0)

      if first_event:
        first_day = timestamp
        last_day = timestamp
        first_event = False

      if timestamp < first_day:
        first_day = timestamp

      if timestamp > last_day:
        last_day = timestamp

      for aHost in hosts:
        if aHost == worker:
          if timestamp not in dicts[aHost]:
            dicts[aHost][timestamp] = 1
          else:
            dicts[aHost][timestamp] = dicts[aHost][timestamp] + 1

    self.log_msg(f"First day      : {first_day}")
    self.log_msg(f"Last day       : {last_day}")
    num_days = (last_day - first_day).days

    self.log_msg(f"Number of days : {num_days}")

    csv_data = {}
    cur_day = first_day
    for day_num in range(num_days):
      day_dict = {}
      for aHost in hosts:
        day_dict[aHost] = 0
      csv_data[cur_day] = day_dict
      cur_day = cur_day + datetime.timedelta(days=1)
      
    cur_day = first_day
    for day_num in range(num_days):

      for aHost in hosts:
        for host_day in dicts[aHost]:
          if host_day == cur_day:
            csv_data[cur_day][aHost] = csv_data[cur_day][aHost] + 1
      cur_day = cur_day + datetime.timedelta(days=1)

    for csv_day in csv_data:
      row = (f"{csv_day}")
      for aHost in hosts:
        row = row + ',' + str(csv_data[csv_day][aHost])
      print(row)
    sys.exit(0)

    startup = Db4eStartup()
    csv_filename = startup.shares_found_csv()
    try:
      csv_handle = open(csv_filename, 'w')
    except:
      self.log(f"ERROR: Unable to open Shares Found CSV ({csv_filename})")

    csv_handle.write("Date,Shares Found\n")
    for key in key_list:
      csv_handle.write(str(key) + "," + str(shares_found_dict[key]) + "\n")
    
    csv_handle.close()
      
    db4e_git = Db4eGit()
    db4e_git.push(csv_filename, 'Updated Shares Found')
    self.log(f"  Shares Found CSV : {csv_filename}")
