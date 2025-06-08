const csvUrl = '/csv/sharesfound/by-miner-sharesfound-30days.csv';
const dateData = [];

const totalBingoData = [];
const totalKermitData = [];
const totalMaiaData = [];
const totalParisData = [];
const totalSallyData = [];
const totalPhoebeData = [];
const totalIslandsData = [];

Papa.parse(csvUrl, {
  download: true,
  header: true,
  delimiter: ",",
  complete: data => {
    data.data.forEach(row => {
      const dateString = row['Date'];

const bingo = row['bingo'];
const kermit = row['kermit'];
const maia = row['maia'];
const paris = row['paris'];
const sally = row['sally'];
const phoebe = row['phoebe'];
const islands = row['islands'];

      // Check for missing or invalid data
      //if (!dateString || isNaN(value)) {
      //  console.log('Invalid or missing data found. Skipping this row.');
      //  return;
      //}

      // Parse the date string and convert it to a timestamp
      const date = new Date(dateString).getTime();

      dateData.push(date);
      //totalData.push(Number(total));

      totalBingoData.push({ x:date, y: bingo});
      totalKermitData.push({ x:date, y: kermit});
      totalMaiaData.push({ x:date, y: maia});
      totalParisData.push({ x:date, y: paris});
      totalSallyData.push({ x:date, y: sally});
      totalPhoebeData.push({ x:date, y: phoebe});
      totalIslandsData.push({ x:date, y: islands});
    });
    
    const areaOptions = {
      chart: {
        id: "barChart",
        stacked: true,
        type: "bar",
        height: 275,
        foreColor: "#ccc",
        toolbar: {
          autoSelected: "pan",
          show: false
        }
      },
      /* TODO Need to paramerize the next line based on the number of active miners */
      colors: ["#23ac35", "#FF6500", "#C40C0C", "#FFC100", "#472a07", "#559abc", "#B771E5"],
      stroke: {
	    curve: 'stepline',
        width: 3
      },
      grid: {
        borderColor: "#555",
        clipMarkers: false,
        yaxis: {
          lines: {
            show: false
          }
        }
      },
      dataLabels: {
        enabled: false
      },
      fill: {
        gradient: {
          enabled: true,
          opacityFrom: 0.55,
          opacityTo: 0,
        }
      },
      markers: {
        size: 0,
        colors: ["#000524"],
        strokeColor: "#00baec",
        strokeWidth: 1
      },
      series: [
        {
          name: "Bingo",
          data: totalBingoData
        },
        {
          name: "Kermit",
          data: totalKermitData
        },
        {
          name: "Maia",
          data: totalMaiaData
        },
        {
          name: "Paris",
          data: totalParisData
        },
        {
          name: "Sally",
          data: totalSallyData
        },
        {
          name: "Phoebe",
          data: totalPhoebeData
        },
        {
          name: "Islands",
          data: totalIslandsData
        },
      ],
      tooltip: {
        theme: "dark"
      },
      title: {
	    text: 'Shares Found by Worker',
	    align: 'left'
      },
      xaxis: {
        type: "datetime"
      },
      yaxis: {
        min: 0
      }
    };

    var areaChart = new ApexCharts(document.querySelector("#areaChart"), areaOptions);
    areaChart.render();

  }});

