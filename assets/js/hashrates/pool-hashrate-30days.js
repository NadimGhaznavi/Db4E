const csvUrl = '/csv/hashrates/pool-hashrate-30days.csv';
const dateData = [];
const hashData = [];

Papa.parse(csvUrl, {
  download: true,
  header: true,
  delimiter: ",",
  complete: data => {
    data.data.forEach(row => {
      const dateString = row['Datetime'];
      const value = row['Hashrate'];

      // Check for missing or invalid data
      if (!dateString || isNaN(value)) {
        console.log('Invalid or missing data found. Skipping this row.');
        return;
      }

      // Parse the date string and convert it to a timestamp
      const date = new Date(dateString).getTime();

      dateData.push(date);
      //totalData.push(Number(total));
      hashData.push({ x: date, y: value });

    });
    
    const areaOptions = {
      chart: {
        id: "barChart",
        type: "area",
        height: 275,
        foreColor: "#ccc",
        toolbar: {
          autoSelected: "pan",
          show: false
        }
      },
      colors: ["#00baec"],
      stroke: {
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
          name: "Hashrate (KH/s)",
          data: hashData
        }
      ],
      tooltip: {
        theme: "dark"
      },
      xaxis: {
        type: "datetime"
      //},
      //yaxis: {
      //  min: 0,
      //  tickAmount: 4
      }
    };

    var areaChart = new ApexCharts(document.querySelector("#areaChart"), areaOptions);
    areaChart.render();

    var barOptions = {
      chart: {
        id: "areaChart",
        height: 100,
        type: "bar",
        foreColor: "#ccc",
        brush: {
          target: "barChart",
          enabled: true
        },
        selection: {
          enabled: true,
          fill: {
            color: "#fff",
            opacity: 0.4
          },
        }
      },
      colors: ["#FF0080"],
      series: [
        {
          data: hashData
        }
      ],
      stroke: {
        width: 2
      },
      grid: {
        borderColor: "#444"
      },
      markers: {
        size: 0
      },
      xaxis: {
        type: "datetime",
        tooltip: {
          enabled: false
        }
      },
    };

    var barChart = new ApexCharts(document.querySelector("#barChart"), barOptions);
    barChart.render();

  }});

