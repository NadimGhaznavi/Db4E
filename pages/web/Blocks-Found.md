---
layout: post
title: Blocks Found
date: 2024-11-12
---
<script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.3.0/papaparse.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
<script src="/assets/js/BlocksFound.js"></script>

The chart below shows a visualization of the Monero XMR blocks that were found on the mini sidechain.

* My code monitors the P2Pool log continuously looking for *Block Found* events.
* When it detects a *Block Found* event it loads the timestamp of the event into a MongoDB backend database.
* The code then calls a function that extracts all *Block Found* events from MongoDB and transforms the data into a CSV format with daily totals.
* Then the code calls a script to push the CSV file to this GitHub pages site.
* Finally, this *GitHub Formatted Markdown* page displays the information using a JavaScript library, ApexChart, to do the actual chart rendering.

<div id="wrapper">
  <div id="areaChart">
  </div>
  <div id="barChart">
  </div>
 </div>



