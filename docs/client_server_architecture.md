
# Architecture Flow

```
  [ Textual UI or Remote Client ]
                ↓
          Inserts OP Record
         into Mongo 'ops' collection
                ↓
     [DeploymentMgr on any server]
      polls 'ops' for new entries
                ↓
     Executes operation → updates 'depl'
                ↓
     Marks op as done / logs result
```

---

# OpQueue Class

```python
class OpQueue:
    def __init__(self, db: Db4eDb):
        self.db = db

    def add_op(self, op_type: str, target_id: ObjectId, meta: dict):
        """Insert a new operation request."""
        op_doc = {
            "target_id": target_id,
            "type": op_type,  # e.g. "enable", "disable", "delete"
            "meta": meta,
            "created": datetime.utcnow(),
            "ack": False,
            "result": None,
            "log": [],
        }
        self.db.insert_one(self.col_name, op_doc)

    def get_pending_ops(self) -> list[dict]:
        """Get all unacknowledged ops."""
        return self.db.find_many(self.col_name, {"ack": False})

    def mark_op_complete(self.col_name, op_id: ObjectId, result: str, log: list[str]):
        self.db.update_one(self.col_name, {
            "$set": {
                "ack": True,
                "result": result,
                "completed": datetime.utcnow()
            },
            "$push": {"log": {"$each": log}}
        })
```

---

# Mongosh Implementation

## 🎯 Goal: Update a document

- Set ack = true
- Set result = "success"
- Set completed = <now>
- Append log entries: ["started", "completed without error"]

## 🧱 Sample document before update:

Assume your ops collection has a document like this:

```
{
  _id: ObjectId("66a034a28fc81b7c1a4977e3"),
  target_id: ObjectId("66a033a28fc81b7c1a4977e2"),
  type: "enable",
  meta: {},
  created: ISODate("2025-07-19T12:00:00Z"),
  ack: false,
  result: null,
  log: []
}
```

## ✅ Update using mongosh:

```
db.ops.updateOne(
  { _id: ObjectId("66a034a28fc81b7c1a4977e3") },
  {
    $set: {
      ack: true,
      result: "success",
      completed: new Date()
    },
    $push: {
      log: { $each: ["started", "completed without error"] }
    }
  }
)
```

## 🔍 After Update

Once the update has been completed, the document will look like:

```
{
  _id: ObjectId("66a034a28fc81b7c1a4977e3"),
  target_id: ObjectId("66a033a28fc81b7c1a4977e2"),
  type: "enable",
  meta: {},
  created: ISODate("2025-07-19T12:00:00Z"),
  ack: true,
  result: "success",
  completed: ISODate("2025-07-19T14:30:00Z"), // current time
  log: ["started", "completed without error"]
}
```

## 🧠 Summary:

- $set modifies scalar fields (ack, result, completed)
- $push with $each adds multiple values to an array (log)
- They are top-level operators inside the same update document

---

## 🧪 Overview

- MongoDB used as the shared coordination layer
- Server polls for new ops, processes them, and marks them complete
- Client submits ops with metadata

## Python + pymongo

No external packages needed besides pymongo

## 🔧 Prerequisites

`pip install pymongo`

You’ll also need a local or remote MongoDB instance running.

## 📁 Structure

```
pgsql
Copy
Edit
mre/
├── server.py
└── client.py
```

### ✅ server.py

```python
# server.py
import time
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

client = MongoClient("mongodb://localhost:27017")
db = client["demo_db"]
ops = db["ops"]

def process_op(op):
    print(f"🛠️ Processing op {op['transaction_id']}...")
    time.sleep(2)  # Simulate work
    result = f"Processed op {op['type']} for target {op['target_id']}"
    log = ["Started processing", "Finished successfully"]
    ops.update_one(
        {"transaction_id": op["transaction_id"]},
        {
            "$set": {
                "ack": True,
                "result": result,
                "completed": datetime.utcnow()
            },
            "$push": {
                "log": {"$each": log}
            }
        }
    )
    print(f"✅ Completed op {op['transaction_id']}")

def poll_loop():
    while True:
        pending = ops.find({"ack": False}).sort("created", 1)
        for op in pending:
            process_op(op)
        time.sleep(5)

if __name__ == "__main__":
    print("🔁 Server is polling for ops...")
    poll_loop()

```

### ✅ client.py

```python
# client.py
import uuid
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017")
db = client["demo_db"]
ops = db["ops"]

def submit_op(op_type: str, target_id: ObjectId, agent_id: str):
    transaction_id = str(uuid.uuid4())
    op_doc = {
        "transaction_id": transaction_id,
        "type": op_type,
        "target_id": target_id,
        "agent_id": agent_id,
        "meta": {},
        "ack": False,
        "result": None,
        "log": [],
        "created": datetime.utcnow()
    }
    ops.insert_one(op_doc)
    print(f"📤 Submitted op {transaction_id}")

if __name__ == "__main__":
    # Create a fake target
    target_id = ObjectId()
    agent_id = "client-1"
    
    submit_op("enable", target_id, agent_id)
```

### 🧪 To run it:

In one terminal:

```bash
python server.py
```

In another terminal:

```bash
python client.py
```

You’ll see the server detect and process the op, with logs and result updated.

### 🧼 Optional: View Result in mongosh

```
use demo_db
db.ops.find().pretty()
```

## Alternative Implementation

```python

from pymongo import MongoClient
from datetime import datetime

class JobQueue:
    def __init__(self, db_name="job_queue_db", collection_name="jobs"):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def enqueue_job(self, payload):
        job = {
            "payload": payload,
            "status": "pending",
            "created_at": datetime.now(),
            "attempts": 0,
        }
        self.collection.insert_one(job)
        print(f"Job enqueued: {job['_id']}")

    def get_and_process_job(self):
        job = self.collection.find_one_and_update(
            {"status": "pending"},
            {"$set": {"status": "processing", "updated_at": datetime.now(), "$inc": {"attempts": 1}}},
            return_document=True
        )
        if job:
            print(f"Processing job: {job['_id']} with payload: {job['payload']}")
            try:
                # Simulate job processing
                # time.sleep(2)
                # if random.random() < 0.1:
                #     raise Exception("Simulated error")

                self.collection.update_one(
                    {"_id": job["_id"]},
                    {"$set": {"status": "completed", "updated_at": datetime.now()}}
                )
                print(f"Job {job['_id']} completed.")
            except Exception as e:
                self.collection.update_one(
                    {"_id": job["_id"]},
                    {"$set": {"status": "failed", "error": str(e), "updated_at": datetime.now()}}
                )
                print(f"Job {job['_id']} failed: {e}")
        else:
            print("No pending jobs.")

# Example Usage:
# queue = JobQueue()
# queue.enqueue_job({"task": "send_email", "recipient": "test@example.com"})
# queue.get_and_process_job()
```