/* 
tmpl/js/mainchain-hashrate.js

This template is used by the Db4eReports module to generate report
specific JavaScript files.
*/


/*
  This file is part of *db4e*, the *Database 4 Everything* project
  <https://github.com/NadimGhaznavi/db4e>, developed independently
  by Nadim-Daniel Ghaznavi. Copyright (c) 2024-2025 NadimGhaznavi
  <https://github.com/NadimGhaznavi/db4e>.
 
  This program is free software: you can redistribute it and/or 
  modify it under the terms of the GNU General Public License as 
  published by the Free Software Foundation, version 3.
 
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  General Public License for more details.

  You should have received a copy (LICENSE.txt) of the GNU General 
  Public License along with this program. If not, see 
  <http://www.gnu.org/licenses/>.
*/


const csvUrl = '/csv/mainchain-hashrate.csv';
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
      const [datePart, hourPart] = dateString.split(' ');
      const [year, month, day] = datePart.split('-').map(Number);
      const hour = parseInt(hourPart, 10);
      const date = new Date(year, month - 1, day, hour).getTime();

      dateData.push(date);
      //totalData.push(Number(total));
      hashData.push({ x: date, y: value });

    });
    
    const areaOptions = {
      chart: {
        id: "areaChart",
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
          name: "Hashrate (GH/s)",
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
        id: "barChart",
        height: 100,
        type: "bar",
        foreColor: "#ccc",
        brush: {
          target: "areaChart",
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

