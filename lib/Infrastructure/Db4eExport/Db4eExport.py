"""
lib/Infrastructure/Db4eExport/Db4eExport.py
"""

# Import supporting modules
import os, sys
from datetime import datetime

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from Db4eGit.Db4eGit import Db4eGit
from Db4eConfig.Db4eConfig import Db4eConfig

class Db4eExport():
  """
  Helper class for exporting data from the DB4E backend database.
  """

  def __init__(self, log_function, in_file=None, datapoints=None, units=None):
    self.log = log_function

    self._in_file = in_file
    self._datapoints = datapoints
    self._units = units

    config = Db4eConfig()
    self._export_dir = config.config['export']['export_dir']
    self._template_dir = config.config['export']['template_dir']
    self._web_dir = config.config['export']['web_dir']

    self.git = Db4eGit()
    
  def export_short(self):
    # Generate a shorter version of the CSV file, last num_datapoints
    in_file = self._in_file
    export_dir = self._export_dir
    
    units = self._units
    datapoints = self._datapoints
    part_name = f"_{datapoints}{units}.csv"
    
    out_file = self._in_file.replace('.csv', part_name)
    
    out_handle = open(os.path.join(export_dir, out_file), 'w')
    in_handle = open(os.path.join(export_dir, in_file), 'r')
    
    in_lines = in_handle.readlines()
    out_handle.write(in_lines[0])  # Write the header line

    # Get the last num_datapoints from the long file
    for line in in_lines[-datapoints:]:
      out_handle.write(line)
    
    # Close the files
    in_handle.close()
    out_handle.close()
    
    # Push the new short file to the git repository
    self.git.push(out_file, 'New truncated data export')
    self.log(f"  Exported file: {out_file}")

    # Generate a new markdown file
    self.gen_md()

  def gen_md(self):
    # Template filename
    in_file = self._in_file.replace('.csv', '.tmpl')
    out_file = self._in_file.replace('.csv', '.md')
    in_handle = open(os.path.join(self._template_dir, in_file), 'r')
    out_handle = open(os.path.join(self._web_dir, out_file), 'w')

    # Get the current date and time for the markdown file
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    datetime_str = now.strftime("%Y-%m-%d %H:%M")

    # Read the template file
    in_lines = in_handle.readlines()
    for line in in_lines:
      # Replace the placeholders in the template with the actual values
      line = line.replace('[[DATE]]', date_str)
      line = line.replace('[[DATETIME]]', datetime_str)
      out_handle.write(line)
    
    # Close the files
    in_handle.close()
    out_handle.close()

    # Push the new markdown file to the git repository
    self.git.push(out_file, 'New markdown export')
    self.log(f"  Exported file: {out_file}")
    
      
