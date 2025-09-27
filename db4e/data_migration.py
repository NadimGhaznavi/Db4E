from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.MiningDb import MiningDb

from db4e.Constants.DMining import DMining
from db4e.Constants.DMongo import DMongo

from datetime import datetime, timedelta

db = DbMgr()




def migrate_pool_hashrates():
    recs = db.find_many(col_name="kermit", filter={"doc_type": "pool_hashrate"})

    for rec in recs:
        if type(rec[DMongo.TIMESTAMP]) == str:
            date_str, hour = rec[DMongo.TIMESTAMP].split(" ")
            hashrate, units = rec[DMining.HASHRATE].split(" ")

            datetime_object = datetime.strptime(date_str, "%Y-%m-%d")
            datetime_object = datetime_object + timedelta(hours=int(hour))

            new_rec = {
                DMongo.DOC_TYPE: DMining.POOL_HASHRATE,
                DMongo.TIMESTAMP: datetime_object,
                DMining.HASHRATE: float(hashrate),
                DMining.UNIT: units,
                DMongo.CHAIN: "minisidechain"
            }
            db.insert_one("mining", new_rec)
            print(new_rec)

def modify_pool_hashrates():
    recs = db.find_many(col_name="mining", filter={"doc_type": "pool_hashrate"})
    for rec in recs:
        if DMongo.INSTANCE in rec:
            continue
        if rec[DMongo.CHAIN] == "minisidechain":
            rec[DMongo.INSTANCE] = "Mini"
        elif rec[DMongo.CHAIN] == "mainchain":
            rec[DMongo.INSTANCE] = "Main"
        elif rec[DMongo.CHAIN] == "nanochain":
            rec[DMongo.INSTANCE] = "Nano"
        db.update_one("mining", {DMongo.OBJECT_ID: rec[DMongo.OBJECT_ID]}, rec)


modify_pool_hashrates()
#migrate_pool_hashrates()
# migrate_pool_hashrates()