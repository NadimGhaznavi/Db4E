# db4e/util/FormChecker.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

from db4e.db.OpsDb import OpsDb
from db4e.db.DeplDb import DeplDb

from db4e.recs.monero.Db4E import Db4E
from db4e.recs.monero.MoneroD import MoneroD
from db4e.recs.monero.MoneroDRemote import MoneroDRemote
from db4e.recs.monero.P2Pool import P2Pool
from db4e.recs.monero.P2PoolRemote import P2PoolRemote
from db4e.recs.monero.P2PoolInternal import P2PoolInternal
from db4e.recs.monero.XMRig import XMRig

from db4e.constants.DStatus import DStatus
from db4e.constants.DField import DField
from db4e.constants.DLabel import DLabel
from db4e.constants.DElem import DElem


class FormChecker:
    """
    Validate deployment form data and log errors.
    """

    def __init__(self, ops_db: OpsDb, depl_db: DeplDb):
        """
        Initialize the form checker with database handles.

        :param ops_db: Operations database handle.
        :type ops_db: OpsDb
        :param depl_db: Deployment database handle.
        :type depl_db: DeplDb
        :return: None
        :rtype: None
        """
        self.ops_db = ops_db
        self.depl_db = depl_db

    def valid(self, depl_obj):
        """
        Validate a deployment object based on its class.

        :param depl_obj: Deployment object to validate.
        :type depl_obj: object
        :return: True if valid.
        :rtype: bool
        """
        depl_class = type(depl_obj)

        # Make sure we have all the required fields
        if depl_class == Db4E:
            return self.check_db4e_fields(depl_obj)
        elif depl_class == MoneroD:
            return self.check_monerod_fields(depl_obj)
        elif depl_class == MoneroDRemote:
            return self.check_monerod_remote_fields(depl_obj)
        elif depl_class == P2Pool or depl_class == P2PoolInternal:
            return self.check_p2pool_fields(depl_obj)
        elif depl_class == P2PoolRemote:
            return self.check_p2pool_remote_fields(depl_obj)
        elif depl_class == XMRig:
            return self.check_xmrig_fields(depl_obj)

    def check_db4e_fields(self, db4e: Db4E) -> bool:
        """
        Validate Db4E deployment fields.

        :param db4e: Db4E deployment object.
        :type db4e: Db4E
        :return: True if valid.
        :rtype: bool
        """
        required_fields = [
            (DLabel.USER_WALLET, db4e.user_wallet),
            (DLabel.VENDOR_DIR, db4e.vendor_dir),
        ]
        return self._check_fields(db4e, required_fields)

    def check_monerod_fields(self, monerod: MoneroD) -> bool:
        """
        Validate MoneroD deployment fields.

        :param monerod: MoneroD deployment object.
        :type monerod: MoneroD
        :return: True if valid.
        :rtype: bool
        """
        required_fields = [
            (DLabel.INSTANCE, monerod.instance),
            (DLabel.IN_PEERS, monerod.in_peers),
            (DLabel.P2P_BIND_PORT, monerod.p2p_bind_port),
            (DLabel.RPC_BIND_PORT, monerod.rpc_bind_port),
            (DLabel.ZMQ_PUB_PORT, monerod.zmq_pub_port),
            (DLabel.ZMQ_RPC_PORT, monerod.zmq_rpc_port),
            (DLabel.LOG_LEVEL, monerod.log_level),
            (DLabel.MAX_LOG_FILES, monerod.max_log_files),
            (DLabel.MAX_LOG_SIZE, monerod.max_log_size),
            (DLabel.PRIORITY_NODE_1, monerod.priority_node_1),
            (DLabel.PRIORITY_PORT_1, monerod.priority_port_1),
            (DLabel.PRIORITY_NODE_2, monerod.priority_node_2),
            (DLabel.PRIORITY_PORT_2, monerod.priority_port_2),
        ]
        return self._check_fields(monerod, required_fields)

    def check_monerod_remote_fields(self, monerod: MoneroDRemote) -> bool:
        """
        Validate MoneroDRemote deployment fields.

        :param monerod: MoneroDRemote deployment object.
        :type monerod: MoneroDRemote
        :return: True if valid.
        :rtype: bool
        """
        required_fields = [
            (DLabel.INSTANCE, monerod.instance),
            (DLabel.IP_ADDR, monerod.ip_addr),
            (DLabel.RPC_BIND_PORT, monerod.rpc_bind_port),
            (DLabel.ZMQ_PUB_PORT, monerod.zmq_pub_port),
        ]
        return self._check_fields(monerod, required_fields)

    def check_p2pool_fields(self, p2pool: P2Pool) -> bool:
        """
        Validate P2Pool deployment fields.

        :param p2pool: P2Pool deployment object.
        :type p2pool: P2Pool
        :return: True if valid.
        :rtype: bool
        """
        required_fields = [
            (DLabel.INSTANCE, p2pool.instance),
            (DLabel.IN_PEERS, p2pool.in_peers),
            (DLabel.P2P_PORT, p2pool.p2p_port),
            (DLabel.STRATUM_PORT, p2pool.stratum_port),
            (DLabel.LOG_LEVEL, p2pool.log_level),
        ]
        return self._check_fields(p2pool, required_fields)

    def check_p2pool_remote_fields(self, p2pool: P2PoolRemote) -> bool:
        """
        Validate P2PoolRemote deployment fields.

        :param p2pool: P2PoolRemote deployment object.
        :type p2pool: P2PoolRemote
        :return: True if valid.
        :rtype: bool
        """
        required_fields = [
            (DLabel.INSTANCE, p2pool.instance),
            (DLabel.IP_ADDR, p2pool.ip_addr),
            (DLabel.STRATUM_PORT, p2pool.stratum_port),
        ]
        return self._check_fields(p2pool, required_fields)

    def check_xmrig_fields(self, xmrig: XMRig) -> bool:
        """
        Validate XMRig deployment fields.

        :param xmrig: XMRig deployment object.
        :type xmrig: XMRig
        :return: True if valid.
        :rtype: bool
        """
        required_fields = [
            (DLabel.INSTANCE, xmrig.instance),
            (DLabel.NUM_THREADS, xmrig.num_threads),
            (DLabel.PARENT, xmrig.parent),
        ]
        return self._check_fields(xmrig, required_fields)

    def _check_fields(self, obj, required_fields):
        """
        Check a list of required fields for a deployment object.

        :param obj: Deployment object being checked.
        :type obj: object
        :param required_fields: List of (label, getter) pairs.
        :type required_fields: list
        :return: True if all required fields are present.
        :rtype: bool
        """
        valid_flag = True
        for label, method in required_fields:
            value = method()
            if value is None:
                self.ops_db.add_tui_log_line(
                    tracked_instance=obj.instance(),
                    tracked_type=obj.elem_type().lower(),
                    status=DStatus.ERROR,
                    operation=DField.NEW,
                    message=f"Missing required field",
                    details=label,
                )
                valid_flag = False
        return valid_flag

    def instance_exists(self, depl_obj) -> bool:
        """
        Check whether a deployment instance already exists.

        :param depl_obj: Deployment object to check.
        :type depl_obj: object
        :return: False if instance exists; otherwise None.
        :rtype: bool or None
        """
        depl_instance = depl_obj.instance()
        depl_class = type(depl_obj)

        # Check if an instance of the same basic type already exists
        instance_exists = False
        if depl_class == MoneroD or depl_class == MoneroDRemote:
            if self.depl_db.get_deployment(DElem.MONEROD, depl_instance):
                instance_exists = True
            elif self.depl_db.get_deployment(DElem.MONEROD_REMOTE, depl_instance):
                instance_exists = True
        elif depl_class == P2Pool or depl_class == P2PoolRemote:
            if self.depl_db.get_deployment(DElem.P2POOL, depl_instance):
                instance_exists = True
            elif self.depl_db.get_deployment(DElem.P2POOL_REMOTE, depl_instance):
                instance_exists = True
        elif depl_class == XMRig:
            if self.depl_db.get_deployment(DElem.XMRIG, depl_instance):
                instance_exists = True
            elif self.depl_db.get_deployment(DElem.XMRIG_REMOTE, depl_instance):
                instance_exists = True

        # If an instance of the same class exists, write to the console log.
        if instance_exists:
            self.ops_db.add_tui_log_line(
                tracked_instance=depl_obj.instance(),
                tracked_type=depl_obj.elem_type().lower(),
                status=DStatus.ERROR,
                operation=DField.NEW,
                message="A deployment with the same name exists",
            )
            return False
