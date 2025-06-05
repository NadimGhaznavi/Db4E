const csvUrl = '/csv/sharesfound/by-miner-sharesfound-60days.csv';
const dateData = [];

const totalBingoData = [];
const totalKermitData = [];
const totalMaiaData = [];
const totalParisData = [];
const totalSallyData = [];
const totalPhoebeData = [];
const totalIslandsData = [];
[[CONST_TOTAL_MINER_DEFS]]

Papa.parse(csvUrl, {
  download: true,
  header: true,
  delimiter: ",",
  complete: data => {
    data.data.forEach(row => {
      const dateString = row['Date'];

[[CONST_MINER_DEFS]]

      // Check for missing or invalid data
      //if (!dateString || isNaN(value)) {
      //  console.log('Invalid or missing data found. Skipping this row.');
      //  return;
      //}

      // Parse the date string and convert it to a timestamp
      const date = new Date(dateString).getTime();

      dateData.push(date);
      //totalData.push(Number(total));

[[TOTAL_MINER_PUSH]]
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
      colors: ["#00baec","#ffbaec","#01f9c6","#808000","#ffffcc","#fef250","#644117", "#ff5722"],
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
[[SERIES DEFS]]        

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

