from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.MiningDb import MiningDb

from db4e.Constants.DMining import DMining
from db4e.Constants.DMongo import DMongo

from datetime import datetime, timedelta

db = DbMgr()



recs = db.find_many("tmp", {"doc_type": "pool_hashrate"})

for rec in recs:
    if type(rec[DMongo.TIMESTAMP]) == str:
        date_str, hour = rec[DMongo.TIMESTAMP].split(" ")
        hashrate, units = rec[DMining.HASHRATE].split(" ")
        #print(f"{date_str} -- {hour} -- {hashrate} -- {units}")

        datetime_object = datetime.strptime(date_str, "%Y-%m-%d")
        datetime_object = datetime_object + timedelta(hours=int(hour))

        #print(f"{datetime_object} -- {float(hashrate)} -- {units}")
        #print(f"{type(datetime_object)} -- {type(float(hashrate))} -- {type(units)}")

        new_rec = {
            DMongo.DOC_TYPE: DMining.POOL_HASHRATE,
            DMongo.TIMESTAMP: datetime_object,
            DMining.HASHRATE: float(hashrate),
            DMining.UNIT: units,
            DMongo.CHAIN: "minisidechain"
        }
        db.insert_one("mining", new_rec)



