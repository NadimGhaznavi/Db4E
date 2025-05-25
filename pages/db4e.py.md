---
title: db4e.py Console Application
---

The `db4e.py` utility monitors the Monero XMR P2Pool daemon log. This log contains information about the Monoero blockchain and the performance of the mininers in my mining farm.

* The application runs continuously and is restarted once a day. 
* It is responsible for recording P2Pool events in MongoDB.
* It also triggers event driven processes that aggregate and export data and push that data up to GitGub, where it is rendered.

  * [P2Pool Payouts Visualization](https://xmr.osoyalce.com/pages/P2Pool-Payouts.html)
  * [Blocks Found Visualization](https://xmr.osoyalce.com/pages/Blocks-Found.html)
  * [Shares Found Visualization](https://xmr.osoyalce.com/pages/Shares-Found.html)

* The `db4e.py` utility also creates MongoDb records that include miner performance metrics, share found events, XMR payment events and the hashrate for the Monero XMR mainchain, the sidechain hashrate and my mining farm pool's hashrate.
  * This data is pulled from MongoDB by the db4e-gui.py monitoring application and displayed in realtime.

* [Back][/]