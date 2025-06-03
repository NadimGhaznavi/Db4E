---
title: db4e.py Console Application
---

The `db4e.py` is the server side backend interface to the *Database 4 Everything* application. It's primary use is to watch the P2Pool daemon log. In this capacity:

* The application runs continuously. I restart it daily, just because.
* It is responsible for recording P2Pool events in MongoDB.
* It also triggers event driven processes that extract data from MongoDB into CSV format and pushes those files to a GitHub hosted website.

```
$ db4e.py --help
Database 4 Everything
usage: db4e.py [-h] [-a ACTION] [-la]

DB4E Configuration

options:
  -h, --help            show this help message and exit
  -a ACTION, --action ACTION
                        Do -la to list all actions.
  -la, --list_actions   List all available actions.
```

```
$ db4e.py -la
Database 4 Everything
Available actions:
  new_blocks_found_csv     : Generate the 'Blocks Found' CSV files and push them to GitHub.
  new_p2pool_payment_csv   : Generate the 'P2Pool Payments' CSV files and push them to GitHub.
  new_shares_found_csv     : Generate the 'Shares Found' CSV files and push it them GitHub.
  new_shares_found_by_host : Generate the 'Shares Found by Host' CSV files and push them to GitHub.
  backup_db                : Backup MongoDB and push the backup to GitHub.
  monitor_p2pool_log       : Start monitoring the P2Pool daemon log.
  get_wallet_balance       : Get the wallet balance from MongoDb.
```

[Back](/)


