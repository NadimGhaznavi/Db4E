"""
db4e/elem/Db4E.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0

A class representing the deployment of Db4E
"""

import os, grp, getpass
from db4e.recs.monero.LocalMonero import LocalMonero
from db4e.constants.DSQL import DCol
from db4e.constants.DElem import DElem
from db4e.constants.DField import DField
from db4e.constants.DDef import DDef


class Db4E(LocalMonero):

    def __init__(self, rec=None):
        super().__init__()
        self._donation_wallet = DDef.DONATION_WALLET
        self._db4e_group = None
        self._db4e_user = None
        self._install_dir = None
        self._primary_server = DField.DISABLE
        self._primary_remote = DField.DISABLE
        self._user_wallet = ""
        self._vendor_dir = None
        self._instance_map = {}
        # There is only one Db4E deployment
        self.instance(DElem.DB4E)
        # Set the effective user and group IDs
        self.set_effective_identity()
        # Set the install directory
        self.install_dir(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        )
        # Set the primary server to DISABLE by default
        self.primary_server(DField.DISABLE)
        # Enable by default
        self.enabled(True)
        if rec:
            self.from_rec(rec)

    def from_rec(self, rec):
        super().from_rec(rec)
        self._donation_wallet = rec[DCol.DONATION_WALLET]
        self._db4e_group = rec[DCol.DB4E_GROUP]
        self._db4e_user = rec[DCol.DB4E_USER]
        self._install_dir = rec[DCol.INSTALL_DIR]
        self._primary_server = rec[DCol.PRIMARY_SERVER]
        self._primary_remote = rec[DCol.PRIMARY_REMOTE]
        self._user_wallet = rec[DCol.USER_WALLET]
        self._vendor_dir = rec[DCol.VENDOR_DIR]

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                DCol.DONATION_WALLET: self._donation_wallet,
                DCol.DB4E_GROUP: self._db4e_group,
                DCol.DB4E_USER: self._db4e_user,
                DCol.INSTALL_DIR: self._install_dir,
                DCol.PRIMARY_SERVER: self._primary_server,
                DCol.PRIMARY_REMOTE: self._primary_remote,
                DCol.USER_WALLET: self._user_wallet,
                DCol.VENDOR_DIR: self._vendor_dir,
            }
        )
        return data

    ## Attribute get/set methods

    def donation_wallet(self, donation_wallet=None):
        if donation_wallet is not None:
            self._donation_wallet = donation_wallet
        return self._donation_wallet

    def db4e_group(self, group=None):
        if group is not None:
            self._db4e_group = group
        return self._db4e_group

    def db4e_user(self, user=None):
        if user is not None:
            self._db4e_user = user
        return self._db4e_user

    def install_dir(self, install_dir=None):
        if install_dir is not None:
            self._install_dir = install_dir
        return self._install_dir

    def primary_server(self, primary_server=None):
        if primary_server is not None:
            self._primary_server = primary_server
        return self._primary_server

    def primary_remote(self, primary_remote=None):
        if primary_remote is not None:
            self._primary_remote = primary_remote
        return self._primary_remote

    def user_wallet(self, user_wallet=None):
        if user_wallet is not None:
            self._user_wallet = user_wallet
        return self._user_wallet

    def vendor_dir(self, vendor_dir=None):
        if vendor_dir is not None:
            self._vendor_dir = vendor_dir
        return self._vendor_dir

    # Instance map: Used to construct the primary server radioset
    def instance_map(self, map=None):
        if map:
            self._instance_map = map
        return self._instance_map

    # Set the Db4E user and group based on who is running this app
    def set_effective_identity(self):
        """Set the Db4E user and group based on who is running this app"""
        # User account
        user = getpass.getuser()
        # User's group
        effective_gid = os.getegid()
        group_entry = grp.getgrgid(effective_gid)
        group = group_entry.gr_name
        self.db4e_user(user)
        self.db4e_group(group)
