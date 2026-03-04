(function($) {
  'use strict';
  $(function() {
    if ($("#performanceLine").length) { 
      const ctx = document.getElementById('performanceLine');
      var graphGradient = document.getElementById("performanceLine").getContext('2d');
      var graphGradient2 = document.getElementById("performanceLine").getContext('2d');
      var saleGradientBg = graphGradient.createLinearGradient(5, 0, 5, 100);
      saleGradientBg.addColorStop(0, 'rgba(26, 115, 232, 0.18)');
      saleGradientBg.addColorStop(1, 'rgba(26, 115, 232, 0.02)');
      var saleGradientBg2 = graphGradient2.createLinearGradient(100, 0, 50, 150);
      saleGradientBg2.addColorStop(0, 'rgba(0, 208, 255, 0.19)');
      saleGradientBg2.addColorStop(1, 'rgba(0, 208, 255, 0.03)');

      new Chart(ctx, {
        type: 'line',
        data: {
          labels: ["SUN","sun", "MON", "mon", "TUE","tue", "WED", "wed", "THU", "thu", "FRI", "fri", "SAT"],
          datasets: [{
            label: 'This week',
            data: [50, 110, 60, 290, 200, 115, 130, 170, 90, 210, 240, 280, 200],
            backgroundColor: saleGradientBg,
            borderColor: [
                '#1F3BB3',
            ],
            borderWidth: 1.5,
            fill: true, // 3: no fill
            pointBorderWidth: 1,
            pointRadius: [4, 4, 4, 4, 4,4, 4, 4, 4, 4,4, 4, 4],
            pointHoverRadius: [2, 2, 2, 2, 2,2, 2, 2, 2, 2,2, 2, 2],
            pointBackgroundColor: ['#1F3BB3)', '#1F3BB3', '#1F3BB3', '#1F3BB3','#1F3BB3)', '#1F3BB3', '#1F3BB3', '#1F3BB3','#1F3BB3)', '#1F3BB3', '#1F3BB3', '#1F3BB3','#1F3BB3)'],
            pointBorderColor: ['#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff',],
        },{
          label: 'Last week',
          data: [30, 150, 190, 250, 120, 150, 130, 20, 30, 15, 40, 95, 180],
          backgroundColor: saleGradientBg2,
          borderColor: [
              '#52CDFF',
          ],
          borderWidth: 1.5,
          fill: true, // 3: no fill
          pointBorderWidth: 1,
          pointRadius: [0, 0, 0, 4, 0],
          pointHoverRadius: [0, 0, 0, 2, 0],
          pointBackgroundColor: ['#52CDFF)', '#52CDFF', '#52CDFF', '#52CDFF','#52CDFF)', '#52CDFF', '#52CDFF', '#52CDFF','#52CDFF)', '#52CDFF', '#52CDFF', '#52CDFF','#52CDFF)'],
            pointBorderColor: ['#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff',],
      }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          elements: {
            line: {
                tension: 0.4,
            }
        },
        
          scales: {
            yAxes: {
              grid: {
                display: true,
                drawTicks: false,
                color:"#F0F0F0",
                zeroLineColor: '#F0F0F0',
              },
              ticks: {
                beginAtZero: false,
                autoSkip: true,
                maxTicksLimit: 4,
                color:"#6B778C",
                font: {
                  size: 10,
                }
              }
            },
            xAxes: {
              grid: {
                display: false,
                drawTicks: false,
              },
              ticks: {
                beginAtZero: false,
                autoSkip: true,
                maxTicksLimit: 7,
                color:"#6B778C",
                font: {
                  size: 10,
                }
              }
            }
          },
          plugins: {
            legend: {
                display: false,
            }
          }
        },
        plugins: [{
          afterDatasetUpdate: function (chart, args, options) {
              const chartId = chart.canvas.id;
              var i;
              const legendId = `${chartId}-legend`;
              const ul = document.createElement('ul');
              for(i=0;i<chart.data.datasets.length; i++) {
                  ul.innerHTML += `
                  <li>
                    <span style="background-color: ${chart.data.datasets[i].borderColor}"></span>
                    ${chart.data.datasets[i].label}
                  </li>
                `;
              }
              return document.getElementById(legendId).appendChild(ul);
            }
        }]
      });
    }

    if ($("#status-summary").length) { 
      const statusSummaryChartCanvas = document.getElementById('status-summary');
      new Chart(statusSummaryChartCanvas, {
        type: 'line',
        data: {
          labels: ["SUN", "MON", "TUE", "WED", "THU", "FRI"],
          datasets: [{
              label: '# of Votes',
              data: [50, 68, 70, 10, 12, 80],
              backgroundColor: "#ffcc00",
              borderColor: [
                  '#01B6A0',
              ],
              borderWidth: 2,
              fill: false, // 3: no fill
              pointBorderWidth: 0,
              pointRadius: [0, 0, 0, 0, 0, 0],
              pointHoverRadius: [0, 0, 0, 0, 0, 0],
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          elements: {
            line: {
                tension: 0.4,
            }
        },
          scales: {
            yAxes: {
              display: false,
              grid: {
                display: false,
              },
            },
            xAxes: {
              display: false,
              grid: {
                display: false,
              }
            }
          },
          plugins: {
            legend: {
                display: false,
            }
          }
        }
      });
    }
    
    if ($("#customChart").length) { 
      // Get the canvas element
      const customChartCanvas = document.getElementById('customChart');
      
      // Fetch monthly balance data using AJAX
      $.ajax({
          url: '/monthly_balance_chart_root/',  // Replace with the actual URL for your monthly_balance_chart view
          type: 'GET',
          dataType: 'json',
          success: function(data) {
              new Chart(customChartCanvas, {
                  type: 'bar',
                  data: {
                      labels: data.labels,
                      datasets: [{
                          label: 'Total Credit',
                          data: data.credit_data,
                          backgroundColor: "#52CDFF",
                          borderColor: ['#52CDFF'],
                          borderWidth: 0,
                          barPercentage: 0.35,
                          fill: true,
                      },{
                          label: 'Total Debit',
                          data: data.debit_data,
                          backgroundColor: "#1F3BB3",
                          borderColor: ['#1F3BB3'],
                          borderWidth: 0,
                          barPercentage: 0.35,
                          fill: true,
                      }]
                  },
                  options: {
                      responsive: true,
                      maintainAspectRatio: false,
                      elements: {
                          line: {
                              tension: 0.4,
                          }
                      },
                      scales: {
                          y: {
                              grid: {
                                  display: true,
                                  drawTicks: false,
                                  color: "#F0F0F0",
                                  zeroLineColor: '#F0F0F0',
                              },
                              ticks: {
                                  beginAtZero: false,
                                  autoSkip: true,
                                  maxTicksLimit: 4,
                                  color: "#6B778C",
                                  font: {
                                      size: 10,
                                  }
                              }
                          },
                          x: {
                              stacked: true,
                              grid: {
                                  display: false,
                                  drawTicks: false,
                              },
                              ticks: {
                                  beginAtZero: false,
                                  autoSkip: true,
                                  maxTicksLimit: 7,
                                  color: "#6B778C",
                                  font: {
                                      size: 10,
                                  }
                              }
                          }
                      },
                      plugins: {
                          legend: {
                              display: false,
                          }
                      }
                  },
                  plugins: [{
                      afterDatasetUpdate: function (chart, args, options) {
                          const chartId = chart.canvas.id;
                          var i;
                          const legendId = `${chartId}-legend`;
                          const ul = document.createElement('ul');
                          for(i=0;i<chart.data.datasets.length; i++) {
                              ul.innerHTML += `
                                  <li>
                                      <span style="background-color: ${chart.data.datasets[i].borderColor}"></span>
                                      ${chart.data.datasets[i].label}
                                  </li>
                              `;
                          }
                          const legendElement = document.getElementById(legendId);
                          if (legendElement) {
                              legendElement.innerHTML = ''; // Clear existing content
                              legendElement.appendChild(ul);
                          } else {
                              console.error(`Element with ID ${legendId} not found`);
                          }
                      }
                  }]
              });
          },
          error: function(error) {
              console.error('Error fetching monthly balance data:', error);
          }
      });
  }
    if ($("#monthlyBalanceChart").length) {
        // Make AJAX request to fetch data
        $.ajax({
            url: '/monthly_balance_chart_root/',
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                console.log('Data received from server:', data);

                // Get reference to the canvas element
                const monthlyBalanceCanvas = document.getElementById('monthlyBalanceChart');
                console.log('Monthly Balance Canvas:', monthlyBalanceCanvas);

                // Replace null values in debit_data with 0
                const sanitizedDebitData = data.debit_data.map(value => value === null ? 0 : value);

                // Initialize the chart using Chart.js
                new Chart(monthlyBalanceCanvas, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Credit',
                            data: data.credit_data,
                            backgroundColor: "#52CDFF",
                            borderColor: "#52CDFF",
                            borderWidth: 1,
                            barPercentage: 0.35,
                            fill: true,
                        }, {
                            label: 'Debit',
                            data: sanitizedDebitData,
                            backgroundColor: "#1F3BB3",
                            borderColor: "#1F3BB3",
                            borderWidth: 1,
                            barPercentage: 0.35,
                            fill: true,
                        }]
                    },
                    options: {
                        // Add any chart options here, if needed
                    },
                    plugins: [{
                        afterDatasetUpdate: function(chart, args, options) {
                            // Any custom plugin logic can go here
                        }
                    }]
                });

                console.log('Chart initialized successfully');
            },
            error: function(error) {
                console.error('Error fetching data:', error);
            }
        });
    }
    if ($('#totalVisitors').length) {
      var bar = new ProgressBar.Circle(totalVisitors, {
        color: '#fff',
        // This has to be the same size as the maximum width to
        // prevent clipping
        strokeWidth: 15,
        trailWidth: 15, 
        easing: 'easeInOut',
        duration: 1400,
        text: {
          autoStyleContainer: false
        },
        from: {
          color: '#52CDFF',
          width: 15
        },
        to: {
          color: '#677ae4',
          width: 15
        },
        // Set default step function for all animate calls
        step: function(state, circle) {
          circle.path.setAttribute('stroke', state.color);
          circle.path.setAttribute('stroke-width', state.width);
  
          var value = Math.round(circle.value() * 100);
          if (value === 0) {
            circle.setText('');
          } else {
            circle.setText(value);
          }
  
        }
      });
  
      bar.text.style.fontSize = '0rem';
      bar.animate(.64); // Number from 0.0 to 1.0
    }

    if ($('#visitperday').length) {
      var bar = new ProgressBar.Circle(visitperday, {
        color: '#fff',
        // This has to be the same size as the maximum width to
        // prevent clipping
        strokeWidth: 15,
        trailWidth: 15,
        easing: 'easeInOut',
        duration: 1400,
        text: {
          autoStyleContainer: false
        },
        from: {
          color: '#34B1AA',
          width: 15
        },
        to: {
          color: '#677ae4',
          width: 15
        },
        // Set default step function for all animate calls
        step: function(state, circle) {
          circle.path.setAttribute('stroke', state.color);
          circle.path.setAttribute('stroke-width', state.width);
  
          var value = Math.round(circle.value() * 100);
          if (value === 0) {
            circle.setText('');
          } else {
            circle.setText(value);
          }
  
        }
      });
  
      bar.text.style.fontSize = '0rem';
      bar.animate(.34); // Number from 0.0 to 1.0
    }

    if ($("#doughnutChart").length) {
      $.ajax({
          url: '/type_of_balance/',  // Replace with the actual URL of your view
          type: 'GET',
          dataType: 'json',
          success: function (data) {
              console.log('Received data from server:', data); // Log the received data
  
              const doughnutChartCanvas = document.getElementById('doughnutChart');
  
              // Map numeric payment method values to labels
              const paymentMethods = data.payment_method_totals.map(item => {
                  switch (item.pay_method) {
                      case 1:
                          return 'Cash';
                      case 2:
                          return 'Bank Deposit';
                      case 3:
                          return 'Check';
                      default:
                          return 'Unknown';
                  }
              });
  
              const totalAmounts = data.payment_method_totals.map(item => item.total_amount);
  
              // Generate colors dynamically based on the number of payment methods
              const colors = generateColors(paymentMethods.length);
  
              new Chart(doughnutChartCanvas, {
                  type: 'doughnut',
                  data: {
                      labels: paymentMethods,
                      datasets: [{
                          data: totalAmounts,
                          backgroundColor: colors,
                          borderColor: colors,
                      }]
                  },
                  options: {
                      cutout: 90,
                      animationEasing: "easeOutBounce",
                      animateRotate: true,
                      animateScale: false,
                      responsive: true,
                      maintainAspectRatio: true,
                      showScale: true,
                      legend: false,
                      plugins: {
                          legend: {
                              display: false,
                          }
                      }
                  },
                  plugins: [{
                      afterDatasetUpdate: function (chart, args, options) {
                          const chartId = chart.canvas.id;
                          var i;
                          const legendId = `${chartId}-legend`;
                          const ul = document.createElement('ul');
                          for (i = 0; i < chart.data.datasets[0].data.length; i++) {
                              ul.innerHTML += `
                                  <li>
                                      <span style="background-color: ${chart.data.datasets[0].backgroundColor[i]}"></span>
                                      ${chart.data.labels[i]}
                                  </li>
                              `;
                          }
                          return document.getElementById(legendId).innerHTML = ul.outerHTML;
                      }
                  }]
              });
          },
          error: function (error) {
              console.error('Error fetching data:', error);
          }
      });
  }



  if ($("#ratingsDoughnutChart").length) {
    $.ajax({
        url: '/consultant_ratings_json/',  // Replace with the actual URL of your view
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            console.log('Received data from server:', data);

            const doughnutChartCanvas = document.getElementById('ratingsDoughnutChart');

            // Assuming data.ratings_data contains labels and values
            const labels = ['Average Rating', 'Highest Rating'];
            const values = [data.ratings_data.average_rating, 5];

            const colors = generateColors(labels.length);

            new Chart(doughnutChartCanvas, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: values,
                        backgroundColor: colors,
                        borderColor: colors,
                    }]
                },
                options: {
                    cutout: 90,
                    animationEasing: "easeOutBounce",
                    animateRotate: true,
                    animateScale: false,
                    responsive: true,
                    maintainAspectRatio: true,
                    showScale: true,
                    legend: false,
                    plugins: {
                        legend: {
                            display: false,
                        }
                    }
                },
                plugins: [{
                    afterDatasetUpdate: function (chart, args, options) {
                        const chartId = chart.canvas.id;
                        const legendId = `${chartId}-legend`;
                        const ul = document.createElement('ul');
                        for (let i = 0; i < chart.data.datasets[0].data.length; i++) {
                            ul.innerHTML += `
                                <li>
                                    <span style="background-color: ${chart.data.datasets[0].backgroundColor[i]}"></span>
                                    ${chart.data.labels[i]}
                                </li>
                            `;
                        }
                        return document.getElementById(legendId).innerHTML = ul.outerHTML;
                    }
                }]
            });
        },
        error: function (error) {
            console.error('Error fetching data:', error);
        }
    });
}


// Function to generate random colors
function generateColors(count) {
const colors = [];
for (let i = 0; i < count; i++) {
    const randomColor = "#" + Math.floor(Math.random() * 16777215).toString(16);
    colors.push(randomColor);
}
return colors;
}


// Function to generate random colors
function generateColors(count) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        const randomColor = "#" + Math.floor(Math.random() * 16777215).toString(16);
        colors.push(randomColor);
    }
    return colors;
}

  // Function to generate random colors
  function generateColors(count) {
      const colors = [];
      for (let i = 0; i < count; i++) {
          const randomColor = "#" + Math.floor(Math.random() * 16777215).toString(16);
          colors.push(randomColor);
      }
      return colors;
  }
  // Function to generate random colors
  function generateColors(count) {
      const colors = [];
      for (let i = 0; i < count; i++) {
          const randomColor = "#" + Math.floor(Math.random() * 16777215).toString(16);
          colors.push(randomColor);
      }
      return colors;
  }
  
  // Function to generate random colors
  function generateColors(count) {
      const colors = [];
      for (let i = 0; i < count; i++) {
          const randomColor = "#" + Math.floor(Math.random() * 16777215).toString(16);
          colors.push(randomColor);
      }
      return colors;
  }
  // Function to generate random colors
  function generateColors(count) {
      const colors = [];
      for (let i = 0; i < count; i++) {
          const randomColor = "#" + Math.floor(Math.random() * 16777215).toString(16);
          colors.push(randomColor);
      }
      return colors;
  }
  
  // Function to generate random colors
  function generateColors(count) {
      const colors = [];
      for (let i = 0; i < count; i++) {
          const randomColor = "#" + Math.floor(Math.random() * 16777215).toString(16);
          colors.push(randomColor);
      }
      return colors;
  }
  if ($("#studentReport").length) {
    // Function to make an AJAX request to the Django view for monthly student data
    function fetchMonthlyStudentData() {
      // Get CSRF token from the cookie
      const csrftoken = getCookie('csrftoken');
  
      $.ajax({
        url: '/count_students_monthly_entry/',  // Replace with the actual URL of your Django view
        type: 'POST',
        dataType: 'json',
        headers: { 'X-CSRFToken': csrftoken },
        success: function (data) {
          console.log('Received monthly student data from server:', data);
          if (data.students_counts) {
            createMonthlyStudentChart(data.students_counts);
          } else {
            console.log('No monthly student data available for chart creation.');
          }
        },
        error: function (error) {
          console.error('Error fetching monthly student data:', error);
        }
      });
    }
  
    // Function to retrieve CSRF token from cookies
    function getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
    }
    // Function to create the monthly student chart using Chart.js
    function createMonthlyStudentChart(monthlyStudentData) {
      console.log('Received monthly student data for chart creation:', monthlyStudentData);
  
      try {
        const studentReportCanvas = document.getElementById('studentReport').getContext('2d');
  
        // Filter out entries with null month
        const filteredData = monthlyStudentData.filter(entry => entry.month !== null);
  
        new Chart(studentReportCanvas, {
          type: 'bar',
          data: {
            labels: filteredData.map(entry => entry.month),
            datasets: [{
              label: 'Number of Students',
              data: filteredData.map(entry => entry.count),
              backgroundColor: "#52CDFF",
              borderColor: ['#52CDFF'],
              borderWidth: 0,
              fill: true,
              barPercentage: 0.5,
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            elements: {
              line: {
                tension: 0.4,
              }
            },
            scales: {
              yAxes: {
                display: true,
                grid: {
                  display: false,
                  drawBorder: false,
                  color: "rgba(255,255,255,.05)",
                  zeroLineColor: "rgba(255,255,255,.05)",
                },
                ticks: {
                  beginAtZero: true,
                  autoSkip: true,
                  maxTicksLimit: 5,
                  fontSize: 10,
                  color: "#6B778C",
                  font: {
                    size: 10,
                  }
                }
              },
              xAxes: {
                display: true,
                grid: {
                  display: false,
                },
                ticks: {
                  beginAtZero: false,
                  autoSkip: true,
                  maxTicksLimit: 7,
                  fontSize: 10,
                  color: "#6B778C",
                  font: {
                    size: 10,
                  }
                }
              }
            },
            plugins: {
              legend: {
                display: false,
              }
            }
          }
        });
      } catch (error) {
        console.error('Error creating monthly student chart:', error);
      }
    }
  
    // Call the fetchMonthlyStudentData function to initiate the AJAX request
    fetchMonthlyStudentData();
  }
    
  });
  // iconify.load('icons.svg').then(function() {
  //   iconify(document.querySelector('.my-cool.icon'));
  // });

  
})(jQuery);