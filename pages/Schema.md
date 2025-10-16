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
  - [XMRig Table](#xmrig_table)
  - [Remote XMRig Table](#remote_xmrig_table)

- [Operations Tables](#operations_tables)
  - [Start/Stop Table](#start_stop_table)
  - [Current Uptime Table](#current_uptime_table)

- [Mining Tables](#mining_tables)
  - [Block Found Event Table](#block_found_event_table)
  - [Chain Hashrate Table](#chain_hashrate_table)
  - [Chain Miners Table](#chain_miners_table)
  - [Miner Hashrate Table](#miner_hashrate_table)
  - [Pool Hashrate Table](#pool_hashrate_table)
  - [Share Found Event Table](#share_found_event_table)
  - [Share Position Table](#shares_position_table)
  - [XMR Payments Table](#xmr_payments_table)

## Foreign Keys

the `PRAGMA foreign_keys = ON` is used when opening connections to enforce foreign key constraints.

---

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
group           | TEXT      | The Linux group that the Db4E application runs as.
install_dir     | TEXT      | The base *venv* directory holding the PIP *Db4E* package.
instance        | TEXT      | The deployment name; `db4e`.
primary_server  | INTEGER   | A *foreign key* that points at the `monero` table's `id` column.
user            | TEXT      | The Linux group that the Db4E application runs as.
vendor_dir      | TEXT      | The directory where *Db4E's* runtime filesystem artifacts are deployed.
donation_wallet | TEXT      | The *Monero* donation wallet.
user_wallet     | TEXT      | The user's *Monero* wallet, where mining profits are directed.
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
show_time_stats | INTEGER   | 0 or 1, representing whether to show time statistics option is used.
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
enabled         | INTEGER   | 0 or 1, representing whether the *P2Pool* deployment is enabled.
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

This table represents a reference to a *XMRig* deployment on a remote node. *Db4E* supports deploying multiple *XMRig* deployments. This is a **reference**, *Db4E* does not operate on remote nodes.

- Table name: `xmrig_remote`

Column            | Data Type | Description
------------------|-----------|-------------------------
id                | INTEGER   | The *primary key* for the table.
ip_addr           | TEXT      | The hostname or IP address of the remote *XMRig* node.
hashrate          | REAL      | The latest captured hashrate of the remote *XMRig* node in *H/s*.
local_y           | INTEGER   | Local year.
local_mo          | INTEGER   | Local month.
local_d           | INTEGER   | Local day.
local_h           | INTEGER   | Local hour.
local_mi          | INTEGER   | Local minute.
local_s           | INTEGER   | Local second.
uptime            | TEXT      | The uptime of the remote *XMRig* node from the local *P2Pool* log.
updated_y         | INTEGER   | The year the record was updated
updated_mo        | INTEGER   | The month the record was updated
updated_d         | INTEGER   | The day the record was updated
updated_h         | INTEGER   | The hour the record was updated
updated_mi        | INTEGER   | The minute the record was updated
updated_s         | INTEGER   | The second the record was updated

- The *local* times are from the *Db4E* server whereas the *updated* time is from the *P2Pool* log. The latter are in the UTC timezone.

---

# The Operations Tables

This section details the *operations tables.

---

## Start Stop Table

This table contains the start and stop times of the deployed components.

- Table name: `start_stop`

Column            | Data Type | Description
------------------|-----------|-------------------------
id                | INTEGER   | The *primary key* for the table.
element           | TEXT      | The deployed element e.g. `monerod`, `xmrig` and `db4e`.
instance          | TEXT      | The deployment name.
event             | TEXT      | The type of event i.e. `start` or `stop`
updated_y         | INTEGER   | The year the record was updated
updated_mo        | INTEGER   | The month the record was updated
updated_d         | INTEGER   | The day the record was updated
updated_h         | INTEGER   | The hour the record was updated
updated_mi        | INTEGER   | The minute the record was updated
updated_s         | INTEGER   | The second the record was updated

- Timestamps are in the form `YYYY-MM-DD HH:MM:SS`.

---

## Current Uptime Table

This table contains the current uptime of a deployed component. The contents of this table are constructed as *start/stop* events are created in the `start_stop` table. This table is updated when a new record is inserted into the `start_stop` table. 


- Table name: `current_uptime`

Column            | Data Type | Description
------------------|-----------|-------------------------
id                | INTEGER   | The *primary key* for the table.
element           | TEXT      | The deployed element e.g. `monerod`, `xmrig` and `db4e`.
instance          | TEXT      | The deployment name.
start_time        | INTEGER   | A *foreign key* that points at a `start_stop` table's `id`
stop_time         | INTEGER   | A *foreign key* that points at a `start_stop` table's `id`
current_secs      | INTEGER   | The current uptime in seconds.
current           | INTEGER   | 0 or 1, indicating whether the record is the current uptime.

- The can be only one record for each deployment instance where the `current` column is set to `1`.
- The *total uptime* for a deployed instance can be calculated from this table.

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
updated_mi        | INTEGER   | The minute the record was updated
updated_s         | INTEGER   | The second the record was updated

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
updated_mi        | INTEGER   | The minute the record was updated
updated_s         | INTEGER   | The second the record was updated

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
updated_mi        | INTEGER   | The minute the record was updated
updated_s         | INTEGER   | The second the record was updated

- The `instance` name of the miner is also in the `xmrig` or `xmrig_remote` deployment table.
- The `instance` name of the local `P2Pool` deployment is also in the `p2pool` deployment table.

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
xmr               | INTEGER   | The portion of the *XMR payment* that is greater than 1.
xmr_part          | INTEGER   | The portion of the *XMR payment* that is less than 1.
updated_y         | INTEGER   | The year the record was updated
updated_mo        | INTEGER   | The month the record was updated
updated_d         | INTEGER   | The day the record was updated
updated_h         | INTEGER   | The hour the record was updated
updated_mi        | INTEGER   | The minute the record was updated
updated_s         | INTEGER   | The second the record was updated

