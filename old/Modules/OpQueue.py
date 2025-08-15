import uuid
from datetime import datetime

from db4e.Modules.ConfigMgr import Config
from db4e.Modules.DbMgr import DbMgr
from db4e.Constants.Defaults import OPS_COL_DEFAULT

class OpQueue:
    def __init__(self, db: DbMgr):
        self.col_name = OPS_COL_DEFAULT
        self.db = db

    def add_op(self, op_type: str, target_id: ObjectId, meta: dict, agent_id: str | None = None) -> str:
        """Insert a new operation request with a unique transaction ID."""
        transaction_id = str(uuid.uuid4())
        op_doc = {
            "transaction_id": transaction_id,
            "target_id": target_id,
            "type": op_type,  # e.g. "enable", "disable", "delete"
            "meta": meta,
            "agent_id": agent_id,
            "created": datetime.utcnow(),
            "ack": False,
            "result": None,
            "log": [],
        }
        self.db.insert_one(self.col_name, op_doc)
        return transaction_id  # return it so caller can track it

    def get_pending_ops(self) -> list[dict]:
        """Get all unacknowledged ops."""
        return self.db.find_many(col_name=self.col_name, filter={"ack": False})

    def mark_op_complete(self, transaction_id: str, result: str, log: list[str]):
        self.db.update_one(
            col_name=self.col_name, filter={"transaction_id": transaction_id}, 
            new_values={
                    "ack": True,
                    "result": result,
                    "completed": datetime.utcnow()
            } push_va
            
            "$push": {"log": {"$each": log}}
            )
