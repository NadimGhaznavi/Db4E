---
Title: Schema
---

# Introduction

This page details the backend SQLite Table structure used by Db4e. It's broken down into a section for each table. SQLite only has four datatypes; text, integer, real and blob.

---

# Tables

*Db4E* leans hard into SQLite3 to persist various kinds of information. These can be classified into three basic types:

Type        | Description
------------|------------------
Deployments | Information that describles the configuration of deployed components.
Operations  | Information about the start/stop times and runtimes of the deployed components.
Mining      | Information about mining such as hashrates, share found and block found events.

The rest of this document is dedicated to a detailed description of the specific SQLite tables.

- [Deployment Tables](#deployment_tables)
  - [Db4E Table](#db4e_table)
  - [Monero Table](#monero-table)
  - [Remote Monero Table](#remote_monero_table)
  - [P2Pool Table](#p2pool_table)
  - [Remote P2Pool Table](#remote_p2pool_table)
  - [Internal P2Pool Table](#internal_p2pool_table)
  - [XMRig Table](#xmrig_table)
  - [Remote XMRig Table](#remote_xmrig_table)

- [Operations Tables](#operations_tables)
  - [Current Uptime Table](#current_uptime_table)
  - [Total Uptime Table](#total_uptime_table)
  - [TUI Log Table](#tui_log_table)

- [Mining Tables](#mining_tables)
  - [Block Found Event Table](#block_found_event_table)
  - [Chain Hashrate Table](#chain_hashrate_table)
  - [Chain Miners Table](#chain_miners_table)
  - [Miner Hashrate Table](#miner_hashrate_table)
  - [Pool Hashrate Table](#pool_hashrate_table)
  - [Share Found Event Table](#share_found_event_table)
  - [Share Position Table](#shares_position_table)
  - [XMR Payments Table](#xmr_payments_table)


---

# Deployment Tables

This section details the *deployment tables*.

---

## Db4E Table

This table represents the *Db4E* software deployment on the *Db4E* server. This table will have only one row.

- Table name: `db4e`

Column          | Data Type | Description
----------------|-----------|-------------------------
id              | INTEGER   | The *primary key* for the table.
donation_wallet | TEXT      | The *Monero* donation wallet.
db4e_group      | TEXT      | The Linux group that the Db4E application runs as.
db4e_user       | TEXT      | The Linux group that the Db4E application runs as.
install_dir     | TEXT      | The base *venv* directory holding the PIP *Db4E* package.
instance        | TEXT      | The deployment name; `db4e`.
primary_server  | INTEGER   | A *foreign key* that points at the `monero` table's `id` column.
user_wallet     | TEXT      | The user's *Monero* wallet, where mining profits are directed.
vendor_dir      | TEXT      | The directory where *Db4E's* runtime filesystem artifacts are deployed.
updated_y       | INTEGER   | The year the record was updated
updated_mo      | INTEGER   | The month the record was updated
updated_d       | INTEGER   | The day the record was updated
updated_h       | INTEGER   | The hour the record was updated
updated_mi      | INTEGER   | The minute the record was updated
updated_s       | INTEGER   | The second the record was updated

---

## Monero Table

This table represents a *Monero* software deployment on the *Db4E* server. *Db4E* supports deploying multiple *Monero* deployments.

- Table name: `monerod`

Column          | Data Type | Description
----------------|-----------|-------------------------
id              | INTEGER   | The *primary key* for the table.
blockchain_dir  | TEXT      | The directory where the *Monero* blockchain is located.
config_file     | TEXT      | The path to the *Monero* configuration file.
enabled         | INTEGER   | 0 or 1, representing whether the *Monero* deployment is enabled.
in_peers        | INTEGER   | The number of incoming peer connections.
instance        | TEXT      | The deployment name.
ip_addr         | TEXT      | The *IP address* or *hostname* that hosts the *Monero* node.
log_file        | TEXT      | The path to the *Monero* log file.
log_level       | INTEGER   | The log level of the *Monero daemon*.
max_log_files   | INTEGER   | The maximum number of log files. These are rotated.
max_log_size    | INTEGER   | The maximum size of a log file in bytes.
out_peers       | INTEGER   | The number of outgoing peer connections.
p2p_bind_port   | INTEGER   | The *Monero P2P Bind Port* number.
priority_node_1 | TEXT      | The first priority node.
priority_node_2 | TEXT      | The second priority node.
priority_port_1 | INTEGER   | The first priority node's port number.
priority_port_2 | INTEGER   | The second priority node's port number.
rpc_bind_port   | INTEGER   | The *Monero RPC Bind Port* number.
show_time_stats | INTEGER   | 0 or 1 boolean; show time statistics option.
stdin_path      | TEXT      | The path to the *Monero* STDIN file.
version         | TEXT      | The version of the *Monero* software.
zmq_pub_port    | INTEGER   | The *Monero ZMQ Pub Port* number.
zmq_rpc_port    | INTEGER   | The *Monero ZMQ RPC Port* number.
updated_y       | INTEGER   | The year the record was updated
updated_mo      | INTEGER   | The month the record was updated
updated_d       | INTEGER   | The day the record was updated
updated_h       | INTEGER   | The hour the record was updated
updated_mi      | INTEGER   | The minute the record was updated
updated_s       | INTEGER   | The second the record was updated

---

## Remote Monero Table

This table represents a reference to a *Monero* deployment on a remote node. *Db4E* supports deploying multiple *Monero* deployments. This is a **reference**, *Db4E* does not operate on remote nodes.

- Table name: `monerod_remote`

Column          | Data Type | Description
----------------|-----------|-------------------------
id              | INTEGER   | The *primary key* for the table.
instance        | TEXT      | The deployment name.
rpc_bind_port   | INTEGER   | The *Monero RPC Bind Port* number.
ip_addr         | TEXT      | The hostname or IP address of the remote *Monero* node.
zmq_pub_port    | INTEGER   | The *Monero ZMQ Pub Port* number.
updated_y       | INTEGER   | The year the record was updated
updated_mo      | INTEGER   | The month the record was updated
updated_d       | INTEGER   | The day the record was updated
updated_h       | INTEGER   | The hour the record was updated
updated_mi      | INTEGER   | The minute the record was updated
updated_s       | INTEGER   | The second the record was updated

- The *Db4E* software does not operate on remote nodes. The `enabled` flag is used cascades down to local `p2pool` dployments that have their `parent` column set to the `id` column of this table.

---

## P2Pool Table

This table represents a *P2Pool* software deployment on the *Db4E* server. *Db4E* supports deploying multiple *P2Pool* deployments.

- Table name: `p2pool`

Column            | Data Type | Description
------------------|-----------|-------------------------
id                | INTEGER   | The *primary key* for the table.
any_ip            | TEXT      | The *IP address* that the *P2Pool* software listens on.
chain             | TEXT      | The *chain* name: `mainchain`, `minisidechain`, `nanosidechain`.
config_file       | TEXT      | The path to the *P2Pool* configuration file.
enabled           | INTEGER   | 0 or 1, representing whether the *P2Pool* deployment is enabled.
in_peers          | INTEGER   | The number of incoming peer connections.
instance          | TEXT      | The deployment name.
ip_addr           | TEXT      | The *IP address* that the *P2Pool* software listens on.
log_file          | TEXT      | The path to the *P2Pool* log file.
log_rotate_config | TEXT      | The path to the *P2Pool* log rotation configuration file.
max_log_files     | INTEGER   | The maximum number of log files. These are rotated.
max_log_size      | INTEGER   | The maximum size of a log file in bytes.
log_level         | INTEGER   | The log level of the *P2Pool daemon*.
out_peers         | INTEGER   | The number of outgoing peer connections.
p2p_port          | INTEGER   | The *P2Pool P2P Port* number.
parent            | INTEGER   | A *foreign key* that points at a `monerod` or `monerod_remote` table's `id` column.
stdin_path        | TEXT      | The path to the *P2Pool* STDIN file.
stratum_port      | INTEGER   | The *P2Pool Stratum Port* number.
user_wallet       | TEXT      | The user's *Monero* wallet, where mining payouts are directed.
version           | TEXT      | The version of the *P2Pool* software.
updated_y         | INTEGER   | The year the record was updated
updated_mo        | INTEGER   | The month the record was updated
updated_d         | INTEGER   | The day the record was updated
updated_h         | INTEGER   | The hour the record was updated
updated_mi        | INTEGER   | The minute the record was updated
updated_s         | INTEGER   | The second the record was updated

- For the `any_ip` column, a value of `0.0.0.0` is valid and means that the software will bind to all available network interfaces.
- For the `parent` column, a value of `-1` indicates that the parent is unset.

---

## Remote P2Pool Table

This table represents a reference to a *P2Pool* deployment on a remote node. *Db4E* supports deploying multiple *P2Pool* deployments. This is a **reference**, *Db4E* does not operate on remote nodes.

- Table name: `p2pool_remote`

Column          | Data Type | Description
----------------|-----------|-------------------------
id              | INTEGER   | The *primary key* for the table.
instance        | TEXT      | The deployment name.
ip_addr         | TEXT      | The hostname or IP address of the remote *P2Pool* node.
stratum_port    | INTEGER   | The *P2Pool Stratum Port* number.
updated_y       | INTEGER   | The year the record was updated
updated_mo      | INTEGER   | The month the record was updated
updated_d       | INTEGER   | The day the record was updated
updated_h       | INTEGER   | The hour the record was updated
updated_mi      | INTEGER   | The minute the record was updated
updated_s       | INTEGER   | The second the record was updated

- The *Db4E* software does not operate on remote nodes, so the `enabled` column is flag that represents whether or not the local `XMRig` deployments are *enabled* or not.

---

## Internal P2Pool Table

This table represents an *Internal P2Pool* software deployment on the *Db4E* server. *Db4E* deploys three internal *P2Pool* instances to collect *block found events*, *chain hashrate* and *active miners* data for the *Main*, *Mini* and *Nano* chains.

- Table name: `p2pool_internal`

Column            | Data Type | Description
------------------|-----------|-------------------------
id                | INTEGER   | The *primary key* for the table.
any_ip            | TEXT      | The *IP address* that the *P2Pool* software listens on.
chain             | TEXT      | The *chain* name: `mainchain`, `minisidechain`, `nanosidechain`.
config_file       | TEXT      | The path to the *P2Pool* configuration file.
enabled           | INTEGER   | 0 or 1, representing whether the *P2Pool* deployment is enabled.
in_peers          | INTEGER   | The number of incoming peer connections.
instance          | TEXT      | The deployment name.
ip_addr           | TEXT      | The *IP address* that the *P2Pool* software listens on.
log_file          | TEXT      | The path to the *P2Pool* log file.
log_rotate_config | TEXT      | The path to the *P2Pool* log rotation configuration file.
max_log_files     | INTEGER   | The maximum number of log files. These are rotated.
max_log_size      | INTEGER   | The maximum size of a log file in bytes.
log_level         | INTEGER   | The log level of the *P2Pool daemon*.
out_peers         | INTEGER   | The number of outgoing peer connections.
p2p_port          | INTEGER   | The *P2Pool P2P Port* number.
parent            | INTEGER   | A *foreign key* that points at a `monerod` or `monerod_remote` table's `id` column.
stdin_path        | TEXT      | The path to the *P2Pool* STDIN file.
stratum_port      | INTEGER   | The *P2Pool Stratum Port* number.
user_wallet       | TEXT      | The user's *Monero* wallet, where mining payouts are directed.
version           | TEXT      | The version of the *P2Pool* software.
updated_y         | INTEGER   | The year the record was updated
updated_mo        | INTEGER   | The month the record was updated
updated_d         | INTEGER   | The day the record was updated
updated_h         | INTEGER   | The hour the record was updated
updated_mi        | INTEGER   | The minute the record was updated
updated_s         | INTEGER   | The second the record was updated

- For the `any_ip` column, a value of `0.0.0.0` is valid and means that the software will bind to all available network interfaces.
- For the `parent` column, a value of `-1` indicates that the parent is unset.

---

## XMRig Table

This table represents a *XMRig* software deployment on the *Db4E* server. *Db4E* supports deploying multiple *XMRig* deployments.

- Table name: `xmrig`

Column            | Data Type | Description
------------------|-----------|-------------------------
id                | INTEGER   | The *primary key* for the table.
config_file       | TEXT      | The path to the *XMRig* configuration file.
enabled           | INTEGER   | 0 or 1, representing whether the *XMRig* deployment is enabled.
instance          | TEXT      | The deployment name.
log_file          | TEXT      | The path to the *XMRig* log file.
log_rotate_config | TEXT      | The path to the *XMRig* log rotation configuration file.
max_log_files     | INTEGER   | The maximum number of log files. These are rotated.
max_log_size      | INTEGER   | The maximum size of a log file in bytes.
num_threads       | INTEGER   | The number of CPU threads that the XMRig deployment will use.
parent            | INTEGER   | A *foreign key* that points at a `p2pool` or `p2pool_remote` table's `id` column.
version           | TEXT      | The version of the *XMRig* software
updated_y         | INTEGER   | The year the record was updated
updated_mo        | INTEGER   | The month the record was updated
updated_d         | INTEGER   | The day the record was updated
updated_h         | INTEGER   | The hour the record was updated
updated_mi        | INTEGER   | The minute the record was updated
updated_s         | INTEGER   | The second the record was updated

---

## Remote XMRig Table

This table represents a reference to a *Remote XMRig* deployment on a remote node. *Db4E* supports deploying multiple *Remote XMRig* deployments. This is a **reference**, *Db4E* does not operate on remote nodes.

- Table name: `xmrig_remote`

Column            | Data Type | Description
------------------|-----------|-------------------------
id                | INTEGER   | The *primary key* for the table.
instance          | TEXT      | The miner name.
ip_addr           | TEXT      | The hostname or IP address of the remote *XMRig* node.
updated_y         | INTEGER   | Local year.
updated_mo        | INTEGER   | Local month.
updated_d         | INTEGER   | Local day.
updated_h         | INTEGER   | Local hour.
updated_mi        | INTEGER   | Local minute.
updated_s         | INTEGER   | Local second.


---

# The Operations Tables

This section details the *operations* tables. These tables are used to record start and stop times and current uptime of different components. 

---

## Current Uptime Table

This table contains the current uptime of a deployed component. The contents of this table are created when a component is started.

The table is also updated once a minute when the `cur_time` is updated. This allows the
timekeeping to be accurate in the event of an unexpected shutdown.

On startup the server seaches for any open (records with no `stop_time`) and closes them
using the `cur_time` value for the `stop_time`.


- Table name: `current_uptime`

Column            | Data Type | Description
------------------|-----------|-------------------------
id                | INTEGER   | The *primary key* for the table.
tracked_type      | TEXT      | The deployed element e.g. `monerod`, `xmrig` and `db4e`.
tracked_instance  | TEXT      | The deployment name.
start_time        | INTEGER   | Seconds since the epoch.
stop_time         | INTEGER   | Seconds since the epoch.
cur_time          | INTEGER   | Seconds since the epoch.
current_secs      | INTEGER   | The current uptime in seconds.
updated_y         | INTEGER   | The year the record was updated
updated_mo        | INTEGER   | The month the record was updated
updated_d         | INTEGER   | The day the record was updated
updated_h         | INTEGER   | The hour the record was updated
updated_mi        | INTEGER   | The minute the record was updated
updated_s         | INTEGER   | The second the record was updated

- The can be only one record for each deployment instance where the `current` column is set to `1`.


---
## Total Uptime Table

This table contains the total uptime of a deployed component. Each unique `type`/`instance` pair has a corresponding entry in this table. The table is updated when record in the `current_uptime` table is *closed* i.e.the `stop_time` is set.

- Table name: `total_uptime`

Column            | Data Type | Description
------------------|-----------|-------------------------
id                | INTEGER   | The *primary key* for the table.
tracked_type      | TEXT      | The deployed element e.g. `monerod`, `xmrig` and `db4e`.
tracked_instance  | TEXT      | The deployment name.
start_time        | INTEGER   | Seconds since the epoch.
stop_time         | INTEGER   | Seconds since the epoch.
cur_time          | INTEGER   | Seconds since the epoch.
current_secs      | INTEGER   | The current uptime in seconds.
updated_y         | INTEGER   | The year the record was updated
updated_mo        | INTEGER   | The month the record was updated
updated_d         | INTEGER   | The day the record was updated
updated_h         | INTEGER   | The hour the record was updated
updated_mi        | INTEGER   | The minute the record was updated
updated_s         | INTEGER   | The second the record was updated

- The can be only one record for each deployment instance where the `current` column is set to `1`.

---

## TUI Log Table

This table contains records of operations performed by the *Db4E Client* such as adding a new deployment, starting or stopping a deployment, or changing a deployment's configuration.

- Table name: `tui_log_line`

Column            | Data Type | Description
------------------|-----------|-------------------------
id                | INTEGER   | The *primary key* for the table.
elem_type         | TEXT      | The element type being operated on: E.g. `monerod`, `xmrig` or `db4e`.
instance          | TEXT      | The deployment name.
status            | TEXT      | The status of the operation: `PENDING`, `PROCESSING` or `COMPLETED`.
operation         | TEXT      | The type of operation: 'ENABLE`, `DISABLE`, 'DELETE`, `RESTART`, `UPDATE` or `NEW`. 
message           | TEXT      | A description of the operation.
details           | TEXT      | Additional details of the operation.
updated_y         | INTEGER   | The year the record was updated
updated_mo        | INTEGER   | The month the record was updated
updated_d         | INTEGER   | The day the record was updated
updated_h         | INTEGER   | The hour the record was updated
updated_mi        | INTEGER   | The minute the record was updated
updated_s         | INTEGER   | The second the record was updated

---

# Mining Tables

This section details the *mining tables*, which contain mining events and mining metrics data.

---

## Block Found Event Table

This table contains block found events i.e. when a block is found on a chain. This data is collected from the internal, local *P2Pool* log file.

- Table name: `block_found_event`

Column            | Data Type | Description
------------------|-----------|-------------------------
id                | INTEGER   | The *primary key* for the table.
chain             | TEXT      | The chain name: `mainchain`, `minisidechain`, `nanosidechain`.
updated_y         | INTEGER   | The year the record was updated
updated_mo        | INTEGER   | The month the record was updated
updated_d         | INTEGER   | The day the record was updated
updated_h         | INTEGER   | The hour the record was updated
updated_mi        | INTEGER   | The minute the record was updated
updated_s         | INTEGER   | The second the record was updated

---

## Chain Hashrate Table

The table contains hashrate data for each chain. This data is collected every hour. The data is collected from the internal, local *P2Pool* log file.

- Table name: `chain_hashrate`

Column            | Data Type | Description
------------------|-----------|-------------------------
id                | INTEGER   | The *primary key* for the table.
chain             | TEXT      | The chain name: `mainchain`, `minisidechain`, `nanosidechain`.
hashrate          | REAL      | The hashrate of the chain in *H/s*.
updated_y         | INTEGER   | The year the record was updated
updated_mo        | INTEGER   | The month the record was updated
updated_d         | INTEGER   | The day the record was updated
updated_h         | INTEGER   | The hour the record was updated

- Unique constraint: `UNIQUE (chain, updated_y, updated_mo, updated_d, updated_h)`
---

## Chain Miners Table

This table contains the number of active wallets mining on a chain. This data is collected every hour. This data is collected from the internal, local *P2Pool* API.

- Table name: `chain_miners`

Column            | Data Type | Description
------------------|-----------|-------------------------
id                | INTEGER   | The *primary key* for the table.
chain             | TEXT      | The chain name: `mainchain`, `minisidechain`, `nanosidechain`.
miners            | INTEGER   | The number of active miners on the chain.
updated_y         | INTEGER   | The year the record was updated
updated_mo        | INTEGER   | The month the record was updated
updated_d         | INTEGER   | The day the record was updated
updated_h         | INTEGER   | The hour the record was updated

- Unique constraint: `UNIQUE (chain, updated_y, updated_mo, updated_d, updated_h)`
---

## Miner Hashrate

This table contains hashrate data for each miner. This data is collected from the *P2Pool* log file. The log event is triggered when a `workers` command is sent to the running *P2Pool* instance using the `stdin` socket. This socket is created when the *P2Pool systemd service* starts.

- Table name: `miner_hashrate`

Column            | Data Type | Description
------------------|-----------|-------------------------
id                | INTEGER   | The *primary key* for the table.
miner             | TEXT      | The `instance` name of the miner.
chain             | TEXT      | The chain name: `mainchain`, `minisidechain`, `nanosidechain`.
pool              | TEXT      | The `instance` of the local `P2Pool` deployment.
hashrate          | REAL      | The hashrate of the miner in *H/s*.
updated_y         | INTEGER   | The year the record was updated
updated_mo        | INTEGER   | The month the record was updated
updated_d         | INTEGER   | The day the record was updated
updated_h         | INTEGER   | The hour the record was updated

- The `instance` name of the miner is also in the `xmrig` or `xmrig_remote` deployment table.
- The `instance` name of the local `P2Pool` deployment is also in the `p2pool` deployment table.
- Unique constraint: `UNIQUE (miner, chain, pool, updated_y, updated_mo, updated_d, updated_h)`

---

## Pool Hashrate

This table contains hashrate data for the local *P2Pool* deployment. This data is collected every hour. The  data is collected from the *P2Pool* log file. The log event is triggered by sending a `status` command using the `stdin` socket. This socket is created when the *P2Pool systemd service* starts.

- Table name: `pool_hashrate`

Column            | Data Type | Description
------------------|-----------|-------------------------
id                | INTEGER   | The *primary key* for the table.
chain             | TEXT      | The chain name: `mainchain`, `minisidechain`, `nanosidechain`.
pool              | TEXT      | The `instance` name of the local *P2Pool deployment*.
hashrate          | REAL      | The hashrate of the pool in *H/s*.
updated_y         | INTEGER   | The year the record was updated
updated_mo        | INTEGER   | The month the record was updated
updated_d         | INTEGER   | The day the record was updated
updated_h         | INTEGER   | The hour the record was updated
updated_mi        | INTEGER   | The minute the record was updated
updated_s         | INTEGER   | The second the record was updated

- The `instance` name for the `pool` column is also in the `p2pool` deployment table.

---

## Share Found Event

This table contains share found events i.e. when a share is found on a user defined, local *P2Pool deployment*. This data is collected from the *P2Pool* log file.

- Table name: `share_found_event`

Column            | Data Type | Description
------------------|-----------|-------------------------
id                | INTEGER   | The *primary key* for the table.
miner             | TEXT      | The `instance` name of the miner.
chain             | TEXT      | The `chain` name: `mainchain`, `minisidechain`, `nanosidechain`.
pool              | TEXT      | The `instance` name of the local `P2Pool` deployment.
ip_addr           | TEXT      | The IP address of the miner.
effort            | REAL      | The effort of the miner for this share.
updated_y         | INTEGER   | The year the record was updated
updated_mo        | INTEGER   | The month the record was updated
updated_d         | INTEGER   | The day the record was updated
updated_h         | INTEGER   | The hour the record was updated
updated_mi        | INTEGER   | The minute the record was updated
updated_s         | INTEGER   | The second the record was updated

---

## Shares Position

This table contains the *share position* string from the *P2Pool* log file.

- Table name: `shares_position`

Column            | Data Type | Description
------------------|-----------|-------------------------
id                | INTEGER   | The *primary key* for the table.
pool              | TEXT      | The `instance` name of the local `P2Pool` deployment.
position          | TEXT      | The *share position* string from the *P2Pool* log file.
updated_y         | INTEGER   | The year the record was updated
updated_mo        | INTEGER   | The month the record was updated
updated_d         | INTEGER   | The day the record was updated
updated_h         | INTEGER   | The hour the record was updated
updated_mi        | INTEGER   | The minute the record was updated
updated_s         | INTEGER   | The second the record was updated

---

## XMR Payments

This table contains XMR payment data. This data is collected from the *P2Pool* log file.

- Table name: `xmr_payments`

Column            | Data Type | Description
------------------|-----------|-------------------------
id                | INTEGER   | The *primary key* for the table.
pool              | TEXT      | The `instance` name of the local `P2Pool`
chain             | TEXT      | The `chain` name: `mainchain`, `minisidechain`, `nanosidechain`.
piconero          | INTEGER   | XMR in piconeros
updated_y         | INTEGER   | The year the record was updated
updated_mo        | INTEGER   | The month the record was updated
updated_d         | INTEGER   | The day the record was updated
updated_h         | INTEGER   | The hour the record was updated
updated_mi        | INTEGER   | The minute the record was updated
updated_s         | INTEGER   | The second the record was updated

---

# Indexes and Constraints

## Overview

Indexes improve performance for frequent queries — especially those that filter or sort by date or identifier. Constraints maintain data integrity by preventing duplicates or invalid references.

The following indexes and constraints are designed to optimize typical Db4E workflows:

- Efficient retrieval of hashrate and share-found data by date (for plotting and analytics)
- Fast lookup of current uptime records
- Reliable foreign-key integrity between tables
- Enforced uniqueness of certain runtime states (e.g., one “current” uptime per deployment)

## Foreign Keys

the `PRAGMA foreign_keys = ON` is used when opening connections to enforce foreign key constraints.

---

# Generated Columns

In order to facilitate the synchronization process between the **Db4E service** and the **Textual TUI Client**, every table has a *virtual* `updated_ts` column:

```
ALTER TABLE {table_name}
ADD COLUMN updated_ts INTEGER
    GENERATED ALWAYS AS (
        (strftime('%s', 
            printf('%04d-%02d-%02d %02d:%02d:%02d',
                updated_y, updated_mo, updated_d, updated_h, updated_mi, updated_s
            )
        ))
    ) VIRTUAL;
```

For the *hourly mining metrics* tables (e.g. `miner_hashrate`, `pool_hashrate` and `chain_hashrate`), the `updated_mi` and `updated_s` values are set to zero.