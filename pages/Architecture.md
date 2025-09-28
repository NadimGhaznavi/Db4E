---
title: Architecture
---

# Class Relationships

The diagrams below shows which classes are contained within another class and which classes contain a reference to an external class.

## App Replationships

![App Relationships](/images/App-Relationships.png)

## Server Relationships

![Server Relationships](/images/Server-Relationships.png)

---

# Mining Data Origins

**Db4E** creates records in Mongo based on events that are discovered in the *P2Pool* log file and by querying the *P2Pool* API. This sections details the precise origins of the data.

## Overview

* [Block Found Event](#Block_Found_Event)

---

## Block Found Event

*Block Found Events* occur when a new block is found. *Block Found Event* records are created as follows:

1. *Block Found Events* are detected in the `P2PoolWatcher:is_block_found()` method.
2. `P2PoolWatcher:is_block_found()` calls `MiningDb:add_block_found()`.
3. `MiningDb:add_block_found()` calls `DbMgr:insert_uniq_by_timestamp()`.
4. `DbMgr:insert_uniq_by_timestamp()` calls `pymongo.MongoClient.collection.insert_one()`.


### Log Line

Sample *P2Pool* log line:

```
NOTICE  2025-09-27 17:26:49.7653 P2Pool BLOCK FOUND: main chain block at height 3509363 was mined by someone else in this p2pool
```

### Record Description

Field      | Data Type  | Description    
-----------|------------|-------------------
_id        | ObjectId   | Primary key
doc_type   | String     | Type of document
chain      | String     | Chain name (mainchain, minisidechain, nanosidechain)
instance   | String     | Deployment name
timestamp  | Datetime   | Timestamp of event

### Sample Mongo record:

```
{
  "_id": {
    "$oid": "68d8504043ef942cf44728a2"
  },
  "doc_type": "block_found_event",
  "chain": "mainchain",
  "instance": "Main",
  "timestamp": {
    "$date": "2025-09-27T20:59:00.000Z"
  }
}
```

---

## Chain Hashrate

The *Chain Hash

# Donation QR Code

![Donation QR Code](/images/qr_code.png)
