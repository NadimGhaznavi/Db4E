from __future__ import annotations
import os
import platform
from pathlib import Path
import tomllib
import tomli_w

from db4e.constants.DDir import DDir
from db4e.constants.DFile import DFile
from db4e.constants.DField import DField
from db4e.constants.DLabel import DLabel
from db4e.constants.DDef import DDef
from db4e.constants.DElem import DElem


class BootstrapMgr:
    """
    Handles reading and writing the user's bootstrap configuration file.

    This file (~/.db4e on Linux/macOS, %USERPROFILE%\\.db4e on Windows)
    contains minimal information needed to locate and initialize the SQLite DB.
    """

    def __init__(self):
        self._config_path = Path.home() / DFile.DOT_DB4E
        self._config = {}
        if self._config_path.exists():
            self._config = self._load()

    def _load(self) -> dict:
        with self._config_path.open("rb") as f:
            return tomllib.load(f)

    def _save(self):
        with self._config_path.open("wb") as f:
            tomli_w.dump(self._config, f)

        if platform.system() != DLabel.WINDOWS:
            try:
                os.chmod(self._config_path, 0o600)
            except Exception:
                pass

    def get_dir(self, aDir: str) -> str | None:
        if aDir == DDir.DB:
            if not self.is_initialized():
                raise RuntimeError("BootstrapMgr not initialized")
            return os.path.join(self._config.get(DField.VENDOR_DIR), DDef.DB_DIR)

        elif aDir == DElem.DB4E:
            return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        elif aDir == DDir.INSTALL:
            return os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
            )

        elif aDir == DDir.TEMPLATE:
            return os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    DElem.DB4E,
                    DDef.TEMPLATES_DIR,
                )
            )

        elif aDir == DDir.LOGROTATE:
            if not self.is_initialized():
                raise RuntimeError("BootstrapMgr not initialized")
            return os.path.join(self._config.get(DField.VENDOR_DIR), DDef.LOGROTATE)

        elif aDir == DElem.MONEROD:
            return DElem.MONEROD + "-" + DDef.MONEROD_VERSION

        elif aDir == DElem.P2POOL:
            return DElem.P2POOL + "-" + DDef.P2POOL_VERSION

        elif aDir == DDir.VENDOR:
            if not self.is_initialized():
                raise RuntimeError("BootstrapMgr not initialized")
            return self._config.get(DField.VENDOR_DIR)

        elif aDir == DElem.XMRIG:
            return DElem.XMRIG + "-" + DDef.XMRIG_VERSION

        else:
            raise ValueError(f"BootstrapMgr:get_dir(): No handler for {aDir}")

    def get_file(self, aFile: str) -> str | None:
        if not self.is_initialized():
            return None

        if aFile == DFile.PYTHON:
            python = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    "..",
                    "..",
                    "..",
                    DDir.BIN,
                    DDef.PYTHON,
                )
            )
            return python

    def get_logrotate_template(self, elem_type):
        if not self.is_initialized():
            return None

        tmpl_dir = self.get_dir(DDir.TEMPLATE)

        if elem_type == DElem.DB4E:
            return os.path.abspath(
                os.path.join(
                    tmpl_dir,
                    DElem.DB4E,
                    DDef.CONF_DIR,
                    DElem.DB4E + "-" + DDef.LOGROTATE + DDef.CONF_SUFFIX,
                )
            )

        elif elem_type == DElem.P2POOL or elem_type == DElem.P2POOL_INTERNAL:
            return os.path.abspath(
                os.path.join(
                    tmpl_dir,
                    DElem.P2POOL,
                    DDef.CONF_DIR,
                    DElem.P2POOL + "-" + DDef.LOGROTATE + DDef.CONF_SUFFIX,
                )
            )

        elif elem_type == DElem.XMRIG:
            return os.path.abspath(
                os.path.join(
                    tmpl_dir,
                    DElem.XMRIG,
                    DDef.CONF_DIR,
                    DElem.XMRIG + "-" + DDef.LOGROTATE + DDef.CONF_SUFFIX,
                )
            )

    def get_template(self, elem_type):
        tmpl_dir = self.get_dir(DDir.TEMPLATE)

        # Get a monerod startup template
        if elem_type == DElem.MONEROD:
            monerod_dir = self.get_dir(DElem.MONEROD)
            tmpl_file = os.path.join(
                tmpl_dir, monerod_dir, DDef.CONF_DIR, DDef.MONEROD_CONFIG
            )

        # Get a P2Pool startup template
        elif elem_type == DElem.P2POOL:
            p2pool_dir = self.get_dir(DElem.P2POOL)
            tmpl_file = os.path.join(
                tmpl_dir, p2pool_dir, DDef.CONF_DIR, DDef.P2POOL_CONFIG
            )

        # Get a XMRig startup template
        elif elem_type == DElem.XMRIG:
            xmrig_dir = self.get_dir(DElem.XMRIG)
            tmpl_file = os.path.join(
                tmpl_dir, xmrig_dir, DDef.CONF_DIR, DDef.XMRIG_CONFIG
            )
        # Catch unsupported template requests
        else:
            raise ValueError(f"DeplMgr:get_template(): No handler for {elem_type}")

        return tmpl_file

    def initialize(self, vendor_dir: str):
        vendor_dir_path = Path(vendor_dir).expanduser().resolve()
        vendor_dir_path.mkdir(parents=True, exist_ok=True)
        self._config[DField.VENDOR_DIR] = str(vendor_dir_path)
        self._save()

    def is_initialized(self) -> bool:
        return self._config_path.exists() and DField.VENDOR_DIR in self._config

    def __repr__(self):
        return f"BootstrapMgr(vendor_dir={self.get_vendor_dir()})"
