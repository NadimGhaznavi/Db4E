from db4e.db.OpsDb import OpsDb


class OpsETL:

    def __init__(self, ops_db: OpsDb):
        self.ops_db = ops_db

    def add_remote_xmrig_deployment(self, xmrig):
        pass

    def get_ops_summary(self):
        pass

    def get_uptime(self, elem_type, instance):
        pass
