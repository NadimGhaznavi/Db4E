"""
db4e/Modules/Db4e.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

A class representing the deployment of Db4E
"""
import os, grp, getpass

from db4e.Modules.SoftwareSystem import SoftwareSystem
from db4e.Modules.Components import (
    DonationWallet, Db4eGroup, InstallDir, Db4eUser, ObjectId, UserWallet, VendorDir)
from db4e.Constants.Fields import (
    DB4E_FIELD, DONATION_WALLET_FIELD, GROUP_FIELD, INSTALL_DIR_FIELD, USER_FIELD,
    USER_WALLET_FIELD, VENDOR_DIR_FIELD, OBJECT_ID_FIELD)
from db4e.Constants.Labels import (DB4E_LABEL)
from db4e.Constants.Defaults import (DONATION_WALLET_DEFAULT)


class Db4E(SoftwareSystem):


    def __init__(self, rec=None):
        super().__init__()
        self._elem_type = DB4E_FIELD
        self.name = DB4E_LABEL

        self.add_component(DONATION_WALLET_FIELD, DonationWallet())
        self.add_component(GROUP_FIELD, Db4eGroup())
        self.add_component(INSTALL_DIR_FIELD, InstallDir())
        self.add_component(OBJECT_ID_FIELD, ObjectId())
        self.add_component(USER_FIELD, Db4eUser())
        self.add_component(USER_WALLET_FIELD, UserWallet())
        self.add_component(VENDOR_DIR_FIELD, VendorDir())
        
        self.donation_wallet = self.components[DONATION_WALLET_FIELD]
        self.group = self.components[GROUP_FIELD]
        self.install_dir = self.components[INSTALL_DIR_FIELD]
        self.user = self.components[USER_FIELD]
        self.user_wallet = self.components[USER_WALLET_FIELD]
        self.vendor_dir = self.components[VENDOR_DIR_FIELD]

        self.donation_wallet.value = DONATION_WALLET_DEFAULT
        self.set_effective_identity()
        self.set_install_dir()

        if rec:
            self.from_rec(rec)


    def set_effective_identity(self):
        """Set the Db4E user and group based on who is running this app"""
        # User account
        user = getpass.getuser()
        # User's group
        effective_gid = os.getegid()
        group_entry = grp.getgrgid(effective_gid)
        group = group_entry.gr_name
        self.user.value = user
        self.group.value = group

    def set_install_dir(self):
        self.install_dir.value = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
