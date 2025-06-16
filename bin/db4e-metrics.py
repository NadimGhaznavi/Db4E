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
import json

### setup env variables
GITHUB_PAT = os.getenv("TRAFFIC_ACTION_TOKEN")
GITHUB_OWNER = os.getenv("TRAFFIC_ACTION_OWNER")
GITHUB_REPO = os.getenv["TRAFFIC_ACTION_REPO"]


# Define API endpoint URLs
endpoints = [
    "/repos/{}/{}/traffic/clones".format(GITHUB_OWNER, GITHUB_REPO),
    "/repos/{}/{}/traffic/popular/paths".format(GITHUB_OWNER, GITHUB_REPO),
    "/repos/{}/{}/traffic/popular/referrers".format(GITHUB_OWNER, GITHUB_REPO),
    "/repos/{}/{}/traffic/views".format(GITHUB_OWNER, GITHUB_REPO)
]

# Function to fetch data from GitHub API
def fetch_data(endpoint):
    url = "https://api.github.com" + endpoint
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_PAT}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

# Loop through the endpoints and fetch traffic data
for endpoint in endpoints:
    data = fetch_data(endpoint)
    json.dump(data)
