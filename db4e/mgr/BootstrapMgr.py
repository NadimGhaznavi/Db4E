# db4e/mgr/BootstrapMgr.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    Website: https://db4e.osoyalce.com/
#    License: GPL 3.0

from __future__ import annotations
import os
import platform
from pathlib import Path
import tomllib
import tomli_w
import getpass

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
        """
        Initialize the bootstrap manager and load existing config if present.
        """
        # The non-root user creates the bootstrap file in /tmp,
        # The root user picks that up and creates a local version in
        # /root.
        cur_user = getpass.getuser()

        if cur_user == DField.ROOT:
            tmp_config = f"/{DDir.TMP}/{DFile.DOT_DB4E}"
            root_config = f"/{DField.ROOT}/{DFile.DOT_DB4E}"
            self._config_path = root_config

            # Config found in the /tmp directory
            if os.path.exists(tmp_config):
                # Load the config from the /tmp directory
                self._config = self._load(tmp_config)
                # Save the config to the /root directory
                self._save(root_config)
                # Delete the /tmp config
                os.unlink(tmp_config)

            elif os.path.exists(root_config):
                # Load the config
                self._config = self._load(root_config)

            else:
                raise RuntimeError("No bootstrap found in /tmp or /root")

        else:
            home_dir = Path.home()
            home_config = f"/{home_dir}/{DFile.DOT_DB4E}"
            self._config_path = home_config

            # Found a home config file, load it
            if os.path.exists(home_config):
                self._config = self._load(home_config)

    def _load(self, config_file: str) -> dict:
        """
        Load the bootstrap configuration from disk.

        :return: Parsed configuration dictionary.
        :rtype: dict
        """
        with open(config_file, "rb") as f:
            return tomllib.load(f)

    def _save(self):
        """
        Persist the bootstrap configuration to disk. Save it to the
        user's home directory and to /tmp (for pickup by the Db4E
        systemd service)
        """
        home_dir = Path.home()
        home_config = f"/{home_dir}/{DFile.DOT_DB4E}"
        tmp_config = f"/{DDir.TMP}/{DFile.DOT_DB4E}"

        with open(home_config, "wb") as f:
            tomli_w.dump(self._config, f)
        with open(tmp_config, "wb") as f:
            tomli_w.dump(self._config, f)

        if platform.system() != DLabel.WINDOWS:
            os.chmod(home_config, 0o600)
            os.chmod(tmp_config, 0o600)

    def get_dir(self, aDir: str) -> str | None:
        """
        Resolve key directories used by the application.

        :param aDir: Directory selector constant.
        :type aDir: str
        :return: Absolute or configured directory path.
        :rtype: str or None
        """
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
            return DElem.MONEROD

        elif aDir == DElem.P2POOL:
            return DElem.P2POOL

        elif aDir == DDir.VENDOR:
            if not self.is_initialized():
                raise RuntimeError("BootstrapMgr not initialized")
            return self._config.get(DField.VENDOR_DIR)

        elif aDir == DElem.XMRIG:
            return DElem.XMRIG

        else:
            raise ValueError(f"BootstrapMgr:get_dir(): No handler for {aDir}")

    def get_file(self, aFile: str) -> str | None:
        """
        Resolve key file paths used by the application.

        :param aFile: File selector constant.
        :type aFile: str
        :return: Absolute file path or None.
        :rtype: str or None
        """
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
        """
        Return the logrotate template path for a given element type.

        :param elem_type: Element type identifier.
        :type elem_type: str
        :return: Absolute template path or None.
        :rtype: str or None
        """
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
        """
        Return the startup template path for a given element type.

        :param elem_type: Element type identifier.
        :type elem_type: str
        :return: Template path.
        :rtype: str
        """
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
        """
        Initialize bootstrap configuration with a vendor directory.

        :param vendor_dir: Vendor directory to persist.
        :type vendor_dir: str
        """
        vendor_dir_path = Path(vendor_dir).expanduser().resolve()
        vendor_dir_path.mkdir(parents=True, exist_ok=True)
        self._config[DField.VENDOR_DIR] = str(vendor_dir_path)
        self._save()

    def is_initialized(self) -> bool:
        """
        Check whether the bootstrap configuration has been initialized.

        :return: True if initialized, otherwise False.
        :rtype: bool
        """
        return os.path.exists(self._config_path) and DField.VENDOR_DIR in self._config

    def __repr__(self):
        """
        Return a concise representation of the bootstrap manager.
        """
        return f"BootstrapMgr(vendor_dir={self.get_vendor_dir()})"
