"""
db4e/Modules/Db4E.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

A class representing the deployment of Db4E
"""
import os, grp, getpass

from db4e.Modules.LocalSoftwareSystem import LocalSoftwareSystem
from db4e.Modules.Components import (
    DonationWallet, Db4eGroup, InstallDir, Db4eUser, UserWallet, VendorDir,
    PrimaryServer, Instance)
from db4e.Constants.DField import DField
from db4e.Constants.DElem import DElem
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DDef import DDef



class Db4E(LocalSoftwareSystem):


    def __init__(self, rec=None):
        super().__init__()
        self._elem_type = DElem.DB4E
        self.name = DLabel.DB4E

        self.add_component(DField.DONATION_WALLET, DonationWallet())
        self.add_component(DField.GROUP, Db4eGroup())
        self.add_component(DField.INSTALL_DIR, InstallDir())
        self.add_component(DField.INSTANCE, Instance())
        self.add_component(DField.PRIMARY_SERVER, PrimaryServer())
        self.add_component(DField.USER, Db4eUser())
        self.add_component(DField.USER_WALLET, UserWallet())
        self.add_component(DField.VENDOR_DIR, VendorDir())
        
        self.donation_wallet = self.components[DField.DONATION_WALLET]
        self.group = self.components[DField.GROUP]
        self.install_dir = self.components[DField.INSTALL_DIR]
        self.instance = self.components[DField.INSTANCE]
        self.primary_server = self.components[DField.PRIMARY_SERVER]
        self.user = self.components[DField.USER]
        self.user_wallet = self.components[DField.USER_WALLET]
        self.vendor_dir = self.components[DField.VENDOR_DIR]

        self.donation_wallet(DDef.DONATION_WALLET)
        self.instance(DElem.DB4E)
        self.set_effective_identity()
        self.set_install_dir()
        self.enable()

        self._instance_map = {}

        if rec:
            self.from_rec(rec)


    def instance_map(self, map=None):
        if map:
            self._instance_map = map
        return self._instance_map


    def set_effective_identity(self):
        """Set the Db4E user and group based on who is running this app"""
        # User account
        user = getpass.getuser()
        # User's group
        effective_gid = os.getegid()
        group_entry = grp.getgrgid(effective_gid)
        group = group_entry.gr_name
        self.user(user)
        self.group(group)


    def set_install_dir(self):
        self.install_dir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
