from db4e.Modules.OpsDb import OpsETL
from db4e.Modules.OpsDb import OpsDb
from db4e.Modules.DbMgr import DbMgr

db = DbMgr()
ops_db = OpsDb(db)
ops_etl = OpsETL(ops_db)


ops_etl.get_ops_summary()

