#!/usr/bin/python3
"""
bin/db4e-gui.py
"""

# Import supporting modules
import os
import sys
import urwid
from datetime import datetime, timedelta

# The directory that this script is in
script_dir = os.path.dirname(__file__)
# DB4E modules are in the lib_dir
lib_dir = script_dir + '/../lib/'

# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure',
  lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from P2Pool.P2Pool import P2Pool
from P2PoolPaymentCsv.P2PoolPaymentCsv import P2PoolPaymentCsv
from BlocksFoundCsv.BlocksFoundCsv import BlocksFoundCsv
from SharesFoundCsv.SharesFoundCsv import SharesFoundCsv
from SharesFoundByHostCsv.SharesFoundByHostCsv import SharesFoundByHostCsv
from Db4eDb.Db4eDb import Db4eDb
from MiningDb.MiningDb import MiningDb
from Db4eLog.Db4eLog import Db4eLog

def get_hashrates_header():
  hashrates_header = \
    "{:<11}".format('Element') + \
    "{:<12}".format(' Hashrate') + \
    "{:>9}".format('Updated')
  return hashrates_header

def get_mainchain_hashrate():
  db = MiningDb()
  mainchain_hashrate = db.get_mainchain_hashrate()
  status = \
    "{:<11}".format('Mainchain:') + \
    "{:>12}".format(mainchain_hashrate['hashrate']) + \
    "{:>9}".format(mainchain_hashrate['timestamp'])
  return status

def get_pool_hashrate():
  db = MiningDb()
  pool_hashrate = db.get_pool_hashrate()
  status = \
    "{:<11}".format('Pool:') + \
    "{:>12}".format(pool_hashrate['hashrate']) + \
    "{:>9}".format(pool_hashrate['timestamp'])
  return status

def get_share_position():
  db = MiningDb()
  share_position = db.get_share_position()
  return 'Updated: ' + share_position['timestamp'] + '\n' + \
    share_position['position']

def get_shares():
  db = MiningDb()
  shares = db.get_shares()
  timestamps = []
  for timestamp in shares.keys():
    timestamps.append(timestamp)
  timestamps.sort()
  timestamps = timestamps[-14:len(timestamps)]
  shares_str = ''
  for timestamp in timestamps:
    # Timezone from UTC 
    est_timestamp = timestamp - timedelta(hours=5)
    cur_date = datetime.strftime(est_timestamp, "%m-%d")
    cur_time = datetime.strftime(est_timestamp, "%H:%M")
    shares_str += \
      "{:<7}".format(cur_date) + \
      "{:<7}".format(cur_time) + \
      str(shares[timestamp]) + '\n'
  return shares_str[0:-1]

def get_shares_header():
  return \
    "{:<7}".format('Date') + \
    "{:<7}".format('Time') + \
    "{:<14}".format('Worker') 

def get_sidechain_hashrate():
  db = MiningDb()
  sidechain_hashrate = db.get_sidechain_hashrate()
  status = \
    "{:<11}".format('Sidechain:') + \
    "{:>12}".format(sidechain_hashrate['hashrate']) + \
    "{:>9}".format(sidechain_hashrate['timestamp'])
  return status

def get_wallet_balance():
  db = MiningDb()
  return str(db.get_wallet_balance()) + ' XMR'

def get_workers():
  db = MiningDb()
  return db.get_workers()

def get_worker_header():
  worker_header = \
    "{:<3}".format(' ') + \
    "{:<8}".format('Worker') + \
    "{:<9}".format('Hashrate') + \
    "{:>6}".format('Updated')
  return worker_header

def get_worker_data():
  workers = get_workers()
  new_data = ''
  count = 1
  for aHost in workers.keys():
    worker_name = workers[aHost]['worker_name']
    hashrate = workers[aHost]['hashrate']
    timestamp = workers[aHost]['timestamp']
    active = workers[aHost]['active']
    # If the worker is not active, skip it
    if not active:
      continue
    new_data = new_data + \
      str(count) + '. ' + \
      "{:<7}".format(worker_name) + \
      "{:>5}".format(str(round(hashrate))) + ' H/s ' + \
      "{:>7}".format(str(timestamp)) + '\n'
    count += 1
  # Chop off the final newline (\n)
  new_data = new_data[0:-1]
  return ('table text', new_data)

def get_xmr_payments():
  db = MiningDb()
  payouts = db.get_xmr_payments()
  timestamps = []
  for timestamp in payouts.keys():
    timestamps.append(timestamp)
  timestamps.sort()
  timestamps = timestamps[-11:len(timestamps)]
  payments = ''
  for timestamp in timestamps:
    # Timezone from UTC 
    est_timestamp = timestamp - timedelta(hours=5)
    cur_date = datetime.strftime(est_timestamp, "%m-%d")
    cur_time = datetime.strftime(est_timestamp, "%H:%M")
    payments += \
      "{:<7}".format(cur_date) + \
      "{:<7}".format(cur_time) + \
      str(payouts[timestamp]) + '\n'
  return payments[0:-1]

def get_xmr_payments_header():
  return \
    "{:<7}".format('Date') + \
    "{:<7}".format('Time') + \
    "{:<14}".format('Payment') 

# Handle key presses
def handle_input(key):
  if key == 'R' or key == 'r':
    refresh(main_loop, '')

  if key == 'Q' or key == 'q':
    raise urwid.ExitMainLoop()

def refresh(_loop, _data):
  main_loop.draw_screen()
  timestamp = f"{datetime.now().strftime('%Y-%m-%d %H:%M')} "

  header_timestamp.base_widget.set_text(timestamp)
  wallet_balance_widget.set_text(get_wallet_balance())
  worker_table_widget.set_text(get_worker_data())
  payments_widget.set_text(get_xmr_payments())
  position_widget.set_text(get_share_position())
  shares_widget.set_text(get_shares())
  sidechain_hashrate_widget.set_text(get_sidechain_hashrate())
  mainchain_hashrate_widget.set_text(get_mainchain_hashrate())
  pool_hashrate_widget.set_text(get_pool_hashrate())
  main_loop.set_alarm_in(60, refresh)

### Palette
palette = [
  ('titlebar', 'dark red', ''),
  ('green bold', 'dark green,bold', ''),
  ('quit button', 'dark red', ''),
  ('table header', 'dark blue,bold', ''),
  ('table text', 'dark blue', ''),
  ('headers', 'white,bold', ''),
  ('change ', 'dark green', ''),
  ('change negative', 'dark red', '')
]

### GUI Header
header_timestamp_widget = urwid.Text(u'Timestamp', 'right')
header_timestamp = urwid.AttrMap(header_timestamp_widget, 'titlebar')
header_text_widget = urwid.Text(u' Database 4 Everything', 'left')
header_text = urwid.AttrMap(header_text_widget, 'titlebar')
gui_header = urwid.Columns([header_text, header_timestamp])

### Wallet Balance
wallet_balance_widget = urwid.Text(get_wallet_balance())
wallet_balance_padding = urwid.Padding(wallet_balance_widget, left=1, right=1)
wallet_balance_attrmap = urwid.AttrMap(wallet_balance_padding, 'table text')
wallet_balance = urwid.LineBox(wallet_balance_attrmap, title="Mining Wallet Balance", title_align='left', title_attr='green bold')

### Worker table
worker_table_header = urwid.Text(get_worker_header())
worker_table_header_padding = urwid.Padding(worker_table_header, left=1, right=1)
worker_table_header_attrmap = urwid.AttrMap(worker_table_header_padding, 'table header')
worker_table_widget = urwid.Text(get_worker_data())
worker_table_padding = urwid.Padding(worker_table_widget, left=1, right=1)
worker_table_attrmap = urwid.AttrMap(worker_table_padding, 'table text')
worker_table_pile = urwid.Pile([worker_table_header_attrmap, worker_table_attrmap])
worker_table = urwid.LineBox(worker_table_pile, title='Workers', title_attr='green bold', title_align='left')

### XMR Payments
payments_header_widget = urwid.Text(get_xmr_payments_header())
payments_header_padding = urwid.Padding(payments_header_widget, left=1, right=1)
payments_header = urwid.AttrMap(payments_header_padding, 'table header')
payments_widget = urwid.Text(get_xmr_payments())
payments_padding = urwid.Padding(payments_widget, left=1, right=1)
payments_attrmap = urwid.AttrMap(payments_padding, 'table text')
payments_pile = urwid.Pile([payments_header, payments_attrmap])
payments = urwid.LineBox(payments_pile, title='XMR Payments', title_align='left', title_attr='green bold')

### Left GUI pane
left_gui_pane = urwid.Pile([wallet_balance, worker_table, payments])

### Share position
position_widget = urwid.Text(get_share_position())
position_padding = urwid.Padding(position_widget, left=1, right=1)
position_attrmap = urwid.AttrMap(position_padding, 'table text')
position = urwid.LineBox(position_attrmap, title='Share Position(s)', title_align='left', title_attr='green bold')

### Shares list
## Header
shares_header_widget = urwid.Text(get_shares_header())
shares_header_padding = urwid.Padding(shares_header_widget, left=1, right=1)
shares_header = urwid.AttrMap(shares_header_padding, 'table header')
## Shares
shares_widget = urwid.Text(get_shares())
shares_padding = urwid.Padding(shares_widget, left=1, right=1)
shares = urwid.AttrMap(shares_padding, 'table text')
shares_pile = urwid.Pile([shares_header, shares])
shares = urwid.LineBox(shares_pile, title='Shares', title_align='left', title_attr='green bold')

### Hashrates
## Header
hashrates_header_widget = urwid.Text(get_hashrates_header())
hashrates_header_padding = urwid.Padding(hashrates_header_widget, left=1, right=1)
hashrates_header = urwid.AttrMap(hashrates_header_padding, 'table header')
## Mainchain hashrate
mainchain_hashrate_widget = urwid.Text(get_mainchain_hashrate())
mainchain_hashrate_padding = urwid.Padding(mainchain_hashrate_widget, left=1, right=1)
mainchain_hashrate = urwid.AttrMap(mainchain_hashrate_padding, 'table text')
## Sidechain hashrate
sidechain_hashrate_widget = urwid.Text(get_sidechain_hashrate())
sidechain_hashrate_padding = urwid.Padding(sidechain_hashrate_widget, left=1, right=1)
sidechain_hashrate = urwid.AttrMap(sidechain_hashrate_padding, 'table text')
## Pool hashrate
pool_hashrate_widget = urwid.Text(get_pool_hashrate())
pool_hashrate_padding = urwid.Padding(pool_hashrate_widget, left=1, right=1)
pool_hashrate = urwid.AttrMap(pool_hashrate_padding, 'table text')
# Hashrates pile
hashrates_pile = urwid.Pile([hashrates_header, mainchain_hashrate, sidechain_hashrate, pool_hashrate])
# Hashrates linebox
hashrates = urwid.LineBox(hashrates_pile, title='Hashrates', title_align='left', title_attr='green bold')

### Right GUI pane
right_gui_pane = urwid.Pile([position, shares, hashrates])

### Main GUI screen
gui_screen = urwid.Columns([left_gui_pane, right_gui_pane])

#worker_table_filler = urwid.Filler(worker_table, valign='top')
worker_table_filler = urwid.Filler(gui_screen, valign='top')
worker_table_padding = urwid.Padding(worker_table_filler, left=1, right=1)
worker_table_box = urwid.LineBox(worker_table_padding)

### Footer
gui_footer = urwid.Text([
    u'Press (', ('green bold', u'R'), u') to manually refresh. ',
    u'Press (', ('quit button', u'Q'), u') to quit.'
])

### GUI Frame
layout = urwid.Frame(header=gui_header, body=worker_table_box, footer=gui_footer)

### Main Loop
main_loop = urwid.MainLoop(layout, palette, unhandled_input=handle_input)
main_loop.set_alarm_in(0, refresh)
main_loop.run()



    