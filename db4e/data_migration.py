from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.MiningDb import MiningDb

from db4e.Constants.DMining import DMining
from db4e.Constants.DMongo import DMongo



db = DbMgr()



recs = db.find_many("tmp", {"doc_type": "miner_hashrate"})
new_recs = []

for rec in recs:
    db.insert_one("mining", rec)


