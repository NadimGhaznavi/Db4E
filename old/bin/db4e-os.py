"""
bin/db4e-os.py

This is the db4e TUI; terminal user interface. It is used to manage
and deploy the db4e software as well as the Monero Blockchain daemon,
the P2Pool daemon, the XMRig miner and the db4e website GitHub 
repository


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

# Import supporting modules
import os, sys
import warnings
from urwid.widget.columns import ColumnsWarning

# Where the DB4E modules live
lib_dir = os.path.join(os.path.dirname(__file__), '..', 'lib')
sys.path.append(lib_dir)

# Import DB4E modules
from Db4eOSTui.Db4eOSTui import Db4eOSTui

# Needed, otherwise we get STDERR warnings being dumped into the TUI
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ColumnsWarning)

if __name__ == '__main__':
    Db4eOSTui().run()
