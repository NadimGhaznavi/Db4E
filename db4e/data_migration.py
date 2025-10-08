from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.MiningDb import MiningDb

from db4e.Constants.DMining import DMining
from db4e.Constants.DMongo import DMongo

from datetime import datetime, timedelta

db = DbMgr()


def modify_block_found_events_2():
    recs = db.find_many(col_name="mining", filter={"doc_type": "block_found_event"})
    for rec in recs:
        new_rec = {
            DMongo.DOC_TYPE: "block_found_event",
            DMongo.CHAIN: "minisidechain",
            DMongo.POOL: rec[DMongo.INSTANCE],
            DMongo.TIMESTAMP: rec[DMongo.TIMESTAMP],
        }
        db.delete_one("mining", {DMongo.OBJECT_ID: rec[DMongo.OBJECT_ID]})
        db.insert_one("mining", new_rec)


def migrate_block_found_events():
    recs = db.find_many(col_name="tmp", filter={"doc_type": "block_found_event"})

    for rec in recs:
        new_rec = {
            DMongo.DOC_TYPE: "block_found_event",
            DMongo.TIMESTAMP: rec[DMongo.TIMESTAMP],
            DMongo.INSTANCE: "Mini"
        }
        db.insert_one("mining", new_rec)


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


def migrate_share_found_events():
    recs = db.find_many(col_name="tmp", filter={"doc_type": "share_found_event"})
    for rec in recs:
        new_rec = {
            DMongo.DOC_TYPE: "share_found_event",
            DMongo.TIMESTAMP: rec[DMongo.TIMESTAMP],
            DMongo.MINER: rec["worker"],
            DMongo.CHAIN: "minisidechain",
            DMongo.IP_ADDR: rec[DMongo.IP_ADDR],
            DMining.EFFORT: rec[DMining.EFFORT],
            DMongo.POOL: "Sally"
        }
        db.insert_one("mining", new_rec)

def modify_miner_hashrates():
    recs = db.find_many(col_name="mining", filter={"doc_type": "miner_hashrate"})
    for rec in recs:
        new_field = {
            DMongo.POOL: "Sally"
        }
        db.update_one("mining", {DMongo.OBJECT_ID: rec[DMongo.OBJECT_ID]}, new_field)


def modify_xmr_payment():
    recs = db.find_many(col_name="mining", filter={"doc_type": "xmr_payment"})
    for rec in recs:
        new_field = {
            DMongo.POOL: "Sally"
        }
        db.update_one("mining", {DMongo.OBJECT_ID: rec[DMongo.OBJECT_ID]}, new_field)




#modify_pool_hashrates()
#migrate_pool_hashrates()
#migrate_block_found_events()
#modify_block_found_events_2()
#migrate_share_found_events()
#modify_miner_hashrates()