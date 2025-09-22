from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.MiningDb import MiningDb

from db4e.Constants.DMining import DMining
from db4e.Constants.DMongo import DMongo



db = DbMgr()



recs = db.find_many("tmp", {"doc_type": "pool_hashrate"})
new_recs = []

for rec in recs:
    hashrate, units = rec[DMining.HASHRATE].split(" ")
    #db.delete_one("mining", {DMongo.OBJECT_ID: rec[DMongo.OBJECT_ID]})
    new_rec = ({
        DMongo.DOC_TYPE: DMining.POOL_HASHRATE,
        DMongo.TIMESTAMP: rec[DMongo.TIMESTAMP],
        DMining.HASHRATE: hashrate,
        DMongo.CHAIN: rec[DMongo.CHAIN],
        DMining.UNIT: units
    })
    print(new_rec)
    db.insert_one("mining", new_rec)

for rec in new_recs:
    #db.insert_one("mining", rec)
    print(rec)


