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
import uvicorn
import os
import asyncio

from db4e.mgr.BootstrapMgr import BootstrapMgr

from db4e.constants.DLabel import DLabel
from db4e.constants.DFile import DFile
from db4e.constants.DDef import DDef
from db4e.constants.DElem import DElem
from db4e.constants.DDir import DDir
from db4e.constants.DField import DField
from db4e.constants.DUvicorn import DUvicorn


class APIMgr:

    def __init__(self, bs_mgr: BootstrapMgr):
        self.bs_mgr = bs_mgr
        self.app = FastAPI(title=DLabel.DB4E_LONG)
        self._register_routes()

        config = uvicorn.Config(
            self.app,
            host=DDef.ANY_IP,
            port=DDef.API_PORT,
            log_config=self.log_config(),
            access_log=False,
        )
        self.server = uvicorn.Server(config)

    def log_config(self):
        # Configure the log file
        vendor_dir = self.bs_mgr.get_dir(DDir.VENDOR)
        log_file = os.path.join(vendor_dir, DElem.DB4E, DDef.LOG_DIR, DFile.UVICORN_LOG)
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "%(asctime)s %(message)s",
                    "use_colors": False,
                },
            },
            "handlers": {
                "file": {
                    "formatter": "default",
                    "class": "logging.FileHandler",
                    "filename": log_file,
                },
            },
            "loggers": {
                "uvicorn.error": {"handlers": ["file"], "level": "INFO"},
                "uvicorn.access": {"handlers": ["file"], "level": "INFO"},
            },
        }

    async def serve(self):
        await self.server.serve()

    async def shutdown(self):
        await self.server.shutdown()

    def _register_routes(self):

        @self.app.get("/")
        async def read_root():
            return {"message": "Welcome to Db4E API"}

        @self.app.get("/ping")
        async def ping():
            return {"message": "pong"}
