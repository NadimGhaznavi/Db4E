from db4e.Modules.DeplMgr import DeplMgr
from db4e.Modules.DbCache import DbCache
from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.MiningDb import MiningDb


from db4e.Constants.DElem import DElem
from db4e.Constants.DField import DField
from db4e.Constants.DLabel import DLabel




class mre:

    def __init__(self):
        self.db = DbMgr()
        self.mining_db = MiningDb(db=self.db)
        self.db_cache = DbCache(self.db, mining_db=self.mining_db)
        self.depl_mgr = DeplMgr(self.db, self.db_cache)

    def enable_test(self):

        p2pool = self.depl_mgr.get_deployment(DElem.INT_P2POOL, DLabel.MINI_CHAIN)

        print(p2pool.enabled())



if __name__ == "__main__":
    mre = mre()
    mre.enable_test()