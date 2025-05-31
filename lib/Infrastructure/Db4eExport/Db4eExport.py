"""
lib/Infrastructure/Db4eExport/Db4eExport.py
"""

# Import supporting modules
import os, sys

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from Db4eGit.Db4eGit import Db4eGit

class Db4eExport():
  """
  Helper class for exporting data from the DB4E backend database.
  """

  def __init__(self, log_function):
    self._in_file = None
    self._datapoints = None
    self._units = None
    self.log = log_function

  def in_file(self, in_file=None):
    if in_file is not None:
      self._in_file = in_file
    return self._in_file
  
  def datapoints(self, datapoints=None):
    if datapoints is not None:
      self._datapoints = datapoints
    return self._datapoints
  
  def units(self, units=None):
    if units is not None:
      self._units = units
    return self._units
      
  def export_short(self):
    # Generate a shorter version of the CSV file, last num_datapoints
    datapoints = self._datapoints
    in_file = self._in_file
    units = self._units
    part_name = f"_{datapoints}{units}.csv"
    out_file = self._in_file.replace('.csv', part_name)
    out_handle = open(out_file, 'w')

    # Open the long CSV file and write the header to the short file
    in_file = self._in_file
    in_handle = open(in_file, 'r')
    in_lines = in_handle.readlines()
    out_handle.write(in_lines[0])  # Write the header line

    # Get the last num_datapoints from the long file
    for line in in_lines[-datapoints:]:
      out_handle.write(line)
    
    # Close the files
    in_handle.close()
    out_handle.close()
    
    # Push the new short file to the git repository
    git = Db4eGit()
    git.push(out_file, 'New truncated data export')
    self.log(f"  New export file: {out_file}")

