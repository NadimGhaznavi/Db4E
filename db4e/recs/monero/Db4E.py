# db4e/elem/Db4E.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    Website: https://db4e.osoyalce.com/
#    License: GPL 3.0
#
# A class representing the deployment of Db4E

import os, grp, getpass
from db4e.recs.monero.LocalMonero import LocalMonero
from db4e.constants.DSQL import DCol
from db4e.constants.DElem import DElem
from db4e.constants.DField import DField
from db4e.constants.DDef import DDef


class Db4E(LocalMonero):
    """
    Record representing a Db4E deployment configuration.
    """

    def __init__(self, rec=None):
        """
        Initialize the Db4E record and optionally hydrate from a DB record.

        :param rec: Optional database record mapping.
        :type rec: dict or None
        :return: None
        :rtype: None
        """
        super().__init__()
        self._donation_wallet = DDef.DONATION_WALLET
        self._db4e_group = None
        self._db4e_user = None
        self._install_dir = None
        self._primary_server = DField.DISABLE
        self._primary_remote = DField.DISABLE
        self._user_wallet = ""
        self._vendor_dir = DDef.DB4E_INSTALL_DIR
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
        """
        Populate the object from a database record.

        :param rec: Database record mapping.
        :type rec: dict
        :return: None
        :rtype: None
        """
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
        """
        Return a dictionary representation of the record.

        :return: Dictionary with Db4E deployment fields.
        :rtype: dict
        """
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
        """
        Get or set the donation wallet address.

        :param donation_wallet: Optional wallet address to set.
        :type donation_wallet: str or None
        :return: Current donation wallet address.
        :rtype: str
        """
        if donation_wallet is not None:
            self._donation_wallet = donation_wallet
        return self._donation_wallet

    def db4e_group(self, group=None):
        """
        Get or set the Db4E group name.

        :param group: Optional group name to set.
        :type group: str or None
        :return: Current group name.
        :rtype: str or None
        """
        if group is not None:
            self._db4e_group = group
        return self._db4e_group

    def db4e_user(self, user=None):
        """
        Get or set the Db4E user name.

        :param user: Optional user name to set.
        :type user: str or None
        :return: Current user name.
        :rtype: str or None
        """
        if user is not None:
            self._db4e_user = user
        return self._db4e_user

    def install_dir(self, install_dir=None):
        """
        Get or set the install directory path.

        :param install_dir: Optional directory path to set.
        :type install_dir: str or None
        :return: Current install directory.
        :rtype: str or None
        """
        if install_dir is not None:
            self._install_dir = install_dir
        return self._install_dir

    def primary_server(self, primary_server=None):
        """
        Get or set the primary server flag or ID.

        :param primary_server: Optional value to set.
        :type primary_server: int or str or None
        :return: Current primary server value.
        :rtype: int or str or None
        """
        if primary_server is not None:
            self._primary_server = primary_server
        return self._primary_server

    def primary_remote(self, primary_remote=None):
        """
        Get or set the primary remote flag or ID.

        :param primary_remote: Optional value to set.
        :type primary_remote: int or str or None
        :return: Current primary remote value.
        :rtype: int or str or None
        """
        if primary_remote is not None:
            self._primary_remote = primary_remote
        return self._primary_remote

    def user_wallet(self, user_wallet=None):
        """
        Get or set the user wallet address.

        :param user_wallet: Optional wallet address to set.
        :type user_wallet: str or None
        :return: Current user wallet address.
        :rtype: str
        """
        if user_wallet is not None:
            self._user_wallet = user_wallet
        return self._user_wallet

    def vendor_dir(self, vendor_dir=None):
        """
        Get or set the vendor directory path.

        :param vendor_dir: Optional directory path to set.
        :type vendor_dir: str or None
        :return: Current vendor directory.
        :rtype: str or None
        """
        if vendor_dir is not None:
            self._vendor_dir = vendor_dir
        return self._vendor_dir

    # Instance map: Used to construct the primary server radioset
    def instance_map(self, map=None):
        """
        Get or set the instance map for radioset construction.

        :param map: Optional instance map to set.
        :type map: dict or None
        :return: Current instance map.
        :rtype: dict
        """
        if map:
            self._instance_map = map
        return self._instance_map

    # Set the Db4E user and group based on who is running this app
    def set_effective_identity(self):
        """
        Set the Db4E user and group based on the effective OS identity.

        :return: None
        :rtype: None
        """
        # User account
        user = getpass.getuser()
        # User's group
        effective_gid = os.getegid()
        group_entry = grp.getgrgid(effective_gid)
        group = group_entry.gr_name
        self.db4e_user(user)
        self.db4e_group(group)
