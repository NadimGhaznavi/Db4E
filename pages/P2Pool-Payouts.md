---
layout: post
title: P2Pool Payouts
date: 2024-09-08
---
<script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.3.0/papaparse.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
<script src="/assets/js/P2PoolPayouts.js"></script>

The chart below shows a visualization of the Monero XMR that the mining farm has earned. 

* My code monitors the P2Pool log continuously looking for XMR payment log messages.
* When it detects a XMR payment it loads the payout event into a MongoDB backend.
* The code then calls a function that extracts all XMR payouts from MongoDB and transforms the data into a CSV format with daily XMR payout totals.
* Then the code calls a script to push the CSV file to this GitHub pages site.
* Finally, this *GitHub Formatted Markdown* page displays the information using a JavaScript library, ApexChart, to do the actual chart rendering.

<div id="wrapper">
  <div id="areaChart">
  </div>
  <div id="barChart">
  </div>
 </div>


