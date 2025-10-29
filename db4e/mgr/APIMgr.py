"""
db4e/mgr/APIMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from fastapi import FastAPI, HTTPException

from db4e.constants.DLabel import DLabel


class APIMgr:

    def __init__(self):
        self.app = FastAPI(title=DLabel.DB4E_LONG)
        self._register_routes()

    def _register_routes(self):

        @self.app.get("/")
        async def read_root():
            return {"message": "Welcome to Db4E API"}
        
        @self.app.get("/ping")
        async def ping():
            return {"message": "pong"}