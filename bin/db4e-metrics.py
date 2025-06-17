"""
bin/db4e-metrics.py

This is program collects GitHub insights traffic data which only
goes back 14 days. After that GitHub ages the data out.


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

import os
import requests
import sys

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

from Db4eConfig.Db4eConfig import Db4eConfig
from Db4eLogger.Db4eLogger import Db4eLogger
from Db4eDb.Db4eDb import Db4eDb

# Function to fetch data from GitHub API
def fetch_data(endpoint, db4e_log):
    url = "https://api.github.com" + endpoint
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_PAT}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        db4e_log.error(f"GitHub API request failed: {response.status_code} - {response.text}")

# Get a logger
db4e_log = Db4eLogger('db4e-metrics.sh')

# Get a config object
ini = Db4eConfig()
metrics_col_name = ini.config['db']['metrics_collection']

# Get the metrics collection
db4e_db = Db4eDb()
metrics_col = db4e_db.get_collection(metrics_col_name)

# setup env variables
GITHUB_PAT = os.getenv("TRAFFIC_ACTION_TOKEN")
GITHUB_OWNER = os.getenv("TRAFFIC_ACTION_OWNER")
GITHUB_REPO = os.environ["TRAFFIC_ACTION_REPO"]
# Make sure these are set
if not all([GITHUB_PAT, GITHUB_OWNER, GITHUB_REPO]):
    db4e_log.error('Missing one or more required environment variables.')

# Define API endpoint URLs
endpoints = [
    "/repos/{}/{}/traffic/clones".format(GITHUB_OWNER, GITHUB_REPO),
    "/repos/{}/{}/traffic/views".format(GITHUB_OWNER, GITHUB_REPO)
]

# Loop through the endpoints and fetch traffic data
for endpoint in endpoints:
    data = fetch_data(endpoint, db4e_log)
    # Handle case where GitHub returns an unexpected payload or rate limit error
    clone_data = data.get('clones', [])
    view_data = data.get('views', [])
    for rec in clone_data:
        rec['doc_type'] = 'daily_clones'
        db4e_db.insert_uniq_by_timestamp(metrics_col, rec)
    for rec in view_data:
        rec['doc_type'] = 'daily_views'
        db4e_db.insert_uniq_by_timestamp(metrics_col, rec)
