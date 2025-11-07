"""
db4e/mgr/APIMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from fastapi import FastAPI, HTTPException, Query, Request
import uvicorn
import os
import asyncio
import logging

from db4e.mgr.BootstrapMgr import BootstrapMgr
from db4e.mgr.DeplMgr import DeplMgr

from db4e.recs.monero.MoneroD import MoneroD
from db4e.recs.monero.MoneroDRemote import MoneroDRemote
from db4e.recs.monero.P2Pool import P2Pool
from db4e.recs.monero.P2PoolRemote import P2PoolRemote
from db4e.recs.monero.XMRig import XMRig

from db4e.db.SQLDb import SQLDb


from db4e.constants.DLabel import DLabel
from db4e.constants.DFile import DFile
from db4e.constants.DDef import DDef
from db4e.constants.DElem import DElem
from db4e.constants.DDir import DDir
from db4e.constants.DSQL import DTable, ELEM_TABLE_LIST
from db4e.constants.DSync import DSync


class APIMgr:

    def __init__(self, bs_mgr: BootstrapMgr, sql_db: SQLDb, depl_mgr: DeplMgr):
        self.bs_mgr = bs_mgr
        self.depl_mgr = depl_mgr
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

        logging.config.dictConfig(self.log_config())
        self.log = logging.getLogger("uvicorn.error")

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
        try:
            await self.server.serve()
        except asyncio.CancelledError:
            pass

    async def shutdown(self):
        await self.server.shutdown()

    def _register_routes(self):

        @self.app.get("/")
        async def read_root():
            return {"message": "Welcome to Db4E API"}

        # New deployment request
        @self.app.post("/add/{elem_type}")
        async def add_deployment(elem_type: str, request: Request):
            """
            Process a new deployment request.
            """
            payload = await request.json()
            table_name = payload.get(DSync.TABLE_NAME)
            elem_rec = payload.get(DSync.ELEMENT)

            self.log.info(f"Received new deployment request: {elem_type} -- {elem_rec}")

            if table_name not in ELEM_TABLE_LIST:
                raise HTTPException(status_code=400, detail="Invalid deployment type")

            depl_obj = None
            if table_name == DTable.MONEROD:
                depl_obj = MoneroD(elem_rec)
            elif table_name == DTable.MONEROD_REMOTE:
                depl_obj = MoneroDRemote(elem_rec)
            elif table_name == DTable.P2POOL:
                depl_obj = P2Pool(elem_rec)
            elif table_name == DTable.P2POOL_REMOTE:
                depl_obj = P2PoolRemote(elem_rec)
            elif table_name == DTable.XMRIG:
                depl_obj = XMRig(elem_rec)

            self.depl_mgr.add_deployment(depl_obj)

            return {"message": "New deployment request accepted"}
