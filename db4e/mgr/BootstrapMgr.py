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
from pathlib import Path
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

    This file (~/.db4e/bootstrap on Linux/macOS,
    %USERPROFILE%\\.db4e\bootstrap on Windows)
    contains minimal information needed to locate and initialize the
    SQLite DB.
    """

    def __init__(self):
        """
        Initialize the bootstrap manager and load existing config if
        present.
        """
        # This is either root, if this is the Db4E service, or the
        # non-root user who is running the TUI.
        self._cur_user = getpass.getuser()

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

            if self._cur_user == DField.ROOT:
                return os.path.join(DDef.DB4E_INSTALL_DIR, DDir.DB)

            else:
                home_dir = Path.home()
                return os.path.join(home_dir, DDir.DOT_DB4E)

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
            return os.path.join(DDef.DB4E_INSTALL_DIR, DDef.LOGROTATE)

        elif aDir == DElem.MONEROD:
            return DElem.MONEROD

        elif aDir == DElem.P2POOL:
            return DElem.P2POOL

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

    def __repr__(self):
        """
        Return a concise representation of the bootstrap manager.
        """
        return f"BootstrapMgr()"
