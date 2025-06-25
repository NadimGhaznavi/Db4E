"""
bin/db4e-log-loader.py

This utility takes a file and appends it to another file in batches
with a 1 or more second delay between batches. 

The utility script is used to 'replay' P2Pool logs i.e. by using an 
old log as a source file and the actual P2Pool log as the destination 
file with db4e running and monitoring the log. This prevents db4e
from flooding MongoDB.

Use this for the case where db4e was down, but P2Pool was up so you 
have the old P2Pool logs, but you don't have the db4e records.


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
import time
import argparse
import sys
import os

def append_in_batches(src_file, dst_file, batch_size=1000, delay=1):
    """
    Append contents of src_file to dst_file in batches.

    Args:
        src_file (str): Path to the source log file.
        dst_file (str): Path to the destination file.
        batch_size (int): Number of lines per batch.
        delay (int or float): Sleep time between batches in seconds.
    """
    try:
        with open(src_file, 'r') as src:
            while True:
                lines = [src.readline() for _ in range(batch_size)]
                lines = [line for line in lines if line]  # EOF check
                if not lines:
                    break
                with open(dst_file, 'a') as dst:
                    dst.writelines(lines)
                time.sleep(delay)
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"\n⚠️ Error: {e}")
        for _ in range(7):
            print('.', end='', flush=True)
            time.sleep(1)
        print('\n   Maybe try the -h switch .......')
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Append source log to destination in batches.')
    parser.add_argument('-i', '--in_file', required=True, help='The source file to read from.')
    parser.add_argument('-o', '--out_file', required=True, help='The destination file to write to.')
    parser.add_argument('-b', '--batch', type=int, default=1000, help='Number of lines per batch (default: 1000).')
    parser.add_argument('-d', '--delay', type=int, default=1, help='Sleep time between batches in seconds (default: 1).')

    args = parser.parse_args()

    if not os.path.exists(args.in_file):
        print(f"❌ Input file not found: {args.in_file}")
        sys.exit(1)

    append_in_batches(args.in_file, args.out_file, args.batch, args.delay)

if __name__ == "__main__":
    main()
