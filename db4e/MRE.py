

import traceback

from db4e.util.Db4ESystemD import Db4ESystemD
from db4e.db.SQLDb import SQLDb
from db4e.db.OpsDb import OpsDb

from db4e.constants.DField import DField as FIELD
from db4e.constants.DSystemD import DSystemD as SYSTEMD



LOG = "/tmp/mre.log"


class MRE:
    def __init__(self):
        sd = Db4ESystemD(ops_db=OpsDb(sql_db=SQLDb(db_type=FIELD.MRE)), log_file=LOG)

        try:
            sd.service_name(service_name="p2pool@Main", service_type=SYSTEMD.SOCKET_SUFFIX)
            sd.restart()

        except Exception as e:
            print(f"ERROR: {e}")
            print(f"STACKTRACE: {traceback.format_exc()}")


def main():
    mre = MRE()


if __name__ == "__main__":
    main()