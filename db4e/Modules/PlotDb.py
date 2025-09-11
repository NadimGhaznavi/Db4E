"""
Modules/PlotDb.py

Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Modules.DbMgr import DbMgr



class PlotDb:

    def __init__(self):
        self.db = DbMgr()
        self.chain = None
        self.metric = None


    def get_initial_data(self):
        pass


