---
title: XMR Received
date: 2024-10-29
---
<script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.3.0/papaparse.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
<script src="/assets/js/XMRReceived.js"></script>

The chart below shows a visualization of the Monero XMR that the mining farm has earned. The data is taken from the wallet transaction history associated with XMR Mining.

<div id="wrapper">
  <div id="areaChart">
  </div>
  <div id="barChart">
  </div>
 </div>

Note that the graph is remarkably linear with a few exceptions:

* On the dates below, I won the [XMR vs. Beast](https://xmrvsbeast.com/) lottery; I qualify for free as an active Monero miner. The *winnings* consist of extra hash power, so the actual earnings vary, but in all three cases, the spike is visible on the graph.
  * 2024-10-02 06:41:36	Bonus: 6696.8kH/s	Round: vip
  * 2024-08-19 06:53:37	Bonus: 6624.5kH/s	Round: vip
  * 2024-07-12 07:20:14 ERROR: miner not found in PPLNS window, skipping
  * 2024-05-17 10:03:26	Bonus: 7798.6kH/s	Round: vip
* The slight increase from mid June, 2024 till the end of the month is when I burned through about $750 free credits of cloud resources and I setup various container configurations (1 CPU up to 8 CPU with 8 Gb up to 32 Gb) to mine in the cloud.
* I added two miners with a modest hash rate of about 750 H/s and 215 H/a in early October, 2024 and you can see the slight increase in the slope of the graph.
* In May of 2025 I added islands.osoyalce.com to the mining farm 
* Also in May of 2025 brat.osoyalce.com finally died, it was an old micro-mini

Here's a snapshot (taken on November 11, 2024) showing the hashrates of the workers in the mining farm:
```
2024-11-12 02:20:01.1257 StratumServer IP:port                    TLS    uptime              difficulty          hashrate       name
2024-11-12 02:20:01.1257 StratumServer 192.168.0.86:58904         no     19h 56m 42s         51026               1.700 KH/s     sally
2024-11-12 02:20:01.1257 StratumServer 192.168.0.192:48534        no     19h 56m 42s         20296               676 H/s        brat
2024-11-12 02:20:01.1257 StratumServer 192.168.0.169:35654        no     19h 56m 42s         42599               1.419 KH/s     maia
2024-11-12 02:20:01.1257 StratumServer 192.168.0.220:46078        no     19h 56m 42s         27161               905 H/s        phoebe
2024-11-12 02:20:01.1257 StratumServer 192.168.0.244:60544        no     19h 56m 42s         7363                245 H/s        bingo
2024-11-12 02:20:01.1257 StratumServer 192.168.0.27:53106         no     19h 56m 42s         25371               845 H/s        paris
2024-11-12 02:20:01.1257 StratumServer 192.168.0.176:40924        no     19h 56m 43s         39401               1.313 KH/s     kermit
2024-11-12 02:20:01.1257 StratumServer Total: 7 workers
```

The graph shows a direct relationship between hash rate and profitability and also shows that it's a consistent relationship over time.

Finally, for anyone thinking about mining in the cloud: It's not worth it. In fact it's only because my rent includes electricity that I'm able to mine at home and make a profit.

[Back](/pages/web/index.html)








