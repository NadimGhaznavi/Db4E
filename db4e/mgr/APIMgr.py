# db4e/mgr/APIMgr.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    Website: https://db4e.osoyalce.com/
#    License: GPL 3.0

from fastapi import FastAPI, HTTPException, Query, Request
import uvicorn
import os
import asyncio
import logging
import traceback


from db4e.mgr.BootstrapMgr import BootstrapMgr
from db4e.mgr.DeplMgr import DeplMgr

from db4e.recs.monero.Db4E import Db4E
from db4e.recs.monero.MoneroD import MoneroD
from db4e.recs.monero.MoneroDRemote import MoneroDRemote
from db4e.recs.monero.P2Pool import P2Pool
from db4e.recs.monero.P2PoolRemote import P2PoolRemote
from db4e.recs.monero.P2PoolInternal import P2PoolInternal
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
    """
    API manager that exposes deployment operations via FastAPI.
    """

    def __init__(self, bs_mgr: BootstrapMgr, depl_mgr: DeplMgr):
        """
        Initialize the API manager and configure the Uvicorn server.

        :param bs_mgr: Bootstrap manager for directory access.
        :type bs_mgr: BootstrapMgr
        :param sql_db: SQL database wrapper (unused directly here).
        :type sql_db: SQLDb
        :param depl_mgr: Deployment manager for handling requests.
        :type depl_mgr: DeplMgr
        """
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

    def factory(self, table_name, elem_rec):
        """
        Build a deployment object from a table name and record payload.

        :param table_name: Deployment table name.
        :type table_name: str
        :param elem_rec: Deployment record payload.
        :type elem_rec: dict
        :return: Deployment object instance.
        :rtype: object
        """
        if table_name == DTable.DB4E:
            depl_obj = Db4E(elem_rec)
        elif table_name == DTable.MONEROD:
            depl_obj = MoneroD(elem_rec)
        elif table_name == DTable.MONEROD_REMOTE:
            depl_obj = MoneroDRemote(elem_rec)
        elif table_name == DTable.P2POOL:
            depl_obj = P2Pool(elem_rec)
        elif table_name == DTable.P2POOL_REMOTE:
            depl_obj = P2PoolRemote(elem_rec)
        elif table_name == DTable.P2POOL_INTERNAL:
            depl_obj = P2PoolInternal(elem_rec)
        elif table_name == DTable.XMRIG:
            depl_obj = XMRig(elem_rec)
        else:
            raise ValueError(
                f"Unrecognized element record type {table_name}/{elem_rec}"
            )

        return depl_obj

    def log_config(self):
        """
        Build the Uvicorn logging configuration.

        :return: Logging configuration dictionary.
        :rtype: dict
        """
        # Configure the log file
        log_file = os.path.join(
            DDef.DB4E_INSTALL_DIR, DElem.DB4E, DDef.LOG_DIR, DFile.UVICORN_LOG
        )
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
        """
        Start the Uvicorn server.
        """
        try:
            await self.server.serve()

        except asyncio.CancelledError:
            pass

        except Exception as e:
            self.log.critical(f"ERROR: {e}")
            self.log.critical(f"STACKTRACE: {traceback.format_exc()}")

    async def shutdown(self):
        """
        Stop the Uvicorn server.
        """
        await self.server.shutdown()

    def _register_routes(self):
        """
        Register FastAPI route handlers.
        """

        @self.app.get("/")
        async def read_root():
            """
            Root health check endpoint.
            """
            return {"message": "Welcome to Db4E API"}

        # New deployment request
        @self.app.post("/add/{table_name}")
        async def add_deployment(table_name: str, request: Request):
            """
            Process a new deployment request.
            """
            payload = await request.json()
            table_name = payload.get(DSync.TABLE_NAME)
            elem_rec = payload.get(DSync.ELEMENT)
            if table_name not in ELEM_TABLE_LIST:
                raise HTTPException(status_code=400, detail="Invalid deployment type")
            depl_obj = self.factory(table_name=table_name, elem_rec=elem_rec)
            self.log.info(
                f"Received new deployment request: {table_name}/{depl_obj.instance()}"
            )
            self.depl_mgr.add_deployment(depl_obj)

        # Delete deployment request
        @self.app.post("/delete/{table_name}")
        async def delete_deployment(table_name: str, request: Request):
            """
            Process a delete deployment request.
            """
            payload = await request.json()
            table_name = payload.get(DSync.TABLE_NAME)
            elem = payload.get(DSync.ELEMENT)
            if table_name not in ELEM_TABLE_LIST:
                raise HTTPException(status_code=400, detail="Invalid deployment type")
            self.log.info(f"Received delete deployment request: {elem}")
            self.depl_mgr.delete_deployment(elem)

        # Disable deployment
        @self.app.post("/disable")
        async def disable_deployment(request: Request):
            """
            Process an disable deployment request.
            """
            self.log.debug(f"Received request: {request}")
            payload = await request.json()
            elem_rec = payload.get(DSync.ELEMENT)
            table_name = payload.get(DSync.TABLE_NAME)
            if table_name not in ELEM_TABLE_LIST:
                raise HTTPException(status_code=400, detail="Invalid deployment type")
            depl_obj = self.factory(table_name=table_name, elem_rec=elem_rec)
            self.log.info(
                f"Received disable deployment request: {table_name}/{elem_rec}"
            )
            self.depl_mgr.disable_deployment(elem=depl_obj, elem_type=table_name)

        # Enable deployment
        @self.app.post("/enable")
        async def enable_deployment(request: Request):
            """
            Process an enable deployment request.
            """
            self.log.debug(f"Received request: {request}")
            payload = await request.json()
            elem_rec = payload.get(DSync.ELEMENT)
            table_name = payload.get(DSync.TABLE_NAME)
            if table_name not in ELEM_TABLE_LIST:
                raise HTTPException(status_code=400, detail="Invalid deployment type")
            depl_obj = self.factory(table_name=table_name, elem_rec=elem_rec)
            self.log.info(
                f"Received enable deployment request: {table_name}/{elem_rec}"
            )
            self.depl_mgr.enable_deployment(elem=depl_obj, elem_type=table_name)

        # Ping/Pong to test connectivity
        @self.app.post("/ping")
        async def ping(request: Request):
            """
            Ping/Pong connectivity test.
            """
            self.log.debug(f"Received request: {request}")
            await request.json()
            # Do nothing

        # Update deployment request
        @self.app.post("/update/{table_name}")
        async def update_deployment(table_name: str, request: Request):
            """
            Process an update deployment request.
            """
            payload = await request.json()
            table_name = payload.get(DSync.TABLE_NAME)
            elem_rec = payload.get(DSync.ELEMENT)
            if table_name not in ELEM_TABLE_LIST:
                raise HTTPException(status_code=400, detail="Invalid deployment type")
            depl_obj = self.factory(table_name=table_name, elem_rec=elem_rec)
            self.log.info(
                f"Received update deployment request: {table_name}/{elem_rec}"
            )
            try:
                self.depl_mgr.update_deployment(depl_obj)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"{depl_obj.to_dict()}")
