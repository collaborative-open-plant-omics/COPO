$(document).ready(function () {
    // Card body
    const copoStatisticsURL = "/copo/stats";
    const copoGALInspectionURL = "/copo/tol_inspect/institutions";

    $(document).on("click", ".statistics_card .statistics_card_title", function () {
        document.location = copoStatisticsURL
    })

    $(document).on("click", ".gal_inspection_card .gal_inspection_card_title", function () {
        document.location = copoGALInspectionURL;
    })

    // Charts
    const ctx = document.getElementById('chart-bars').getContext("2d");


    new Chart(ctx, {
        type: "line",
        data: {
            labels: ["2022-05-01", "2022-06-01", "2022-07-01", "2022-08-01", "2022-09-01", "2022-10-01", "2022-11-0", "2022-12-01"],
            datasets: [{
                label: "Number of Samples",
                tension: 0,
                borderWidth: 0,
                pointRadius: 5,
                pointBackgroundColor: "rgba(255, 255, 255, .8)",
                pointBorderColor: "transparent",
                borderColor: "rgba(255, 255, 255, .8)",
                borderColor: "rgba(255, 255, 255, .8)",
                borderWidth: 4,
                backgroundColor: "transparent",
                fill: true,
                data: [39, 39, 39, 39, 0, 139, 47, 47],
                maxBarThickness: 6

            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false,
                }
            },
            interaction: {
                intersect: false,
                mode: 'index',
            },
            scales: {
                y: {
                    grid: {
                        drawBorder: false,
                        display: true,
                        drawOnChartArea: true,
                        drawTicks: false,
                        borderDash: [5, 5],
                        color: 'rgba(255, 255, 255, .2)'
                    },
                    ticks: {
                        display: true,
                        color: '#f8f9fa',
                        padding: 10,
                        font: {
                            size: 14,
                            weight: 300,
                            family: "Roboto",
                            style: 'normal',
                            lineHeight: 2
                        },
                    }
                },
                x: {
                    grid: {
                        drawBorder: false,
                        display: false,
                        drawOnChartArea: false,
                        drawTicks: false,
                        borderDash: [5, 5]
                    },
                    ticks: {
                        display: true,
                        color: '#f8f9fa',
                        padding: 10,
                        font: {
                            size: 14,
                            weight: 300,
                            family: "Roboto",
                            style: 'normal',
                            lineHeight: 2
                        },
                    }
                },
            },
        },
    });

    // Pie chart
    new Chart(document.getElementById("chartjs-dashboard-pie"), {
        type: "pie",
        data: {
            labels: ["Chrome", "Firefox", "IE"],
            datasets: [{
                data: [4306, 3801, 1689],
                backgroundColor: [
                    '#3b7ddd',
                    '#fcb92c',
                    '#dc3545'
                ],
                borderWidth: 5
            }]
        },
        options: {
            responsive: !window.MSInputMethodContext,
            maintainAspectRatio: false,
            legend: {
                display: false
            },
            cutoutPercentage: 75
        }
    });
    //
    // new Chart(ctx, {
    //     type: "bar",
    //     data: {
    //         labels: ["M", "T", "W", "T", "F", "S", "S"],
    //         datasets: [{
    //             label: "Sales",
    //             tension: 0.4,
    //             borderWidth: 0,
    //             borderRadius: 4,
    //             borderSkipped: false,
    //             backgroundColor: "rgba(255, 255, 255, .8)",
    //             data: [50, 20, 10, 22, 50, 10, 40],
    //             maxBarThickness: 6
    //         },],
    //     },
    //     options: {
    //         responsive: true,
    //         maintainAspectRatio: false,
    //         plugins: {
    //             legend: {
    //                 display: false,
    //             }
    //         },
    //         interaction: {
    //             intersect: false,
    //             mode: 'index',
    //         },
    //         scales: {
    //             y: {
    //                 grid: {
    //                     drawBorder: false,
    //                     display: true,
    //                     drawOnChartArea: true,
    //                     drawTicks: false,
    //                     borderDash: [5, 5],
    //                     color: 'rgba(255, 255, 255, .2)'
    //                 },
    //                 ticks: {
    //                     suggestedMin: 0,
    //                     suggestedMax: 500,
    //                     beginAtZero: true,
    //                     padding: 10,
    //                     font: {
    //                         size: 14,
    //                         weight: 300,
    //                         family: "Roboto",
    //                         style: 'normal',
    //                         lineHeight: 2
    //                     },
    //                     color: "#fff"
    //                 },
    //             },
    //             x: {
    //                 grid: {
    //                     drawBorder: false,
    //                     display: true,
    //                     drawOnChartArea: true,
    //                     drawTicks: false,
    //                     borderDash: [5, 5],
    //                     color: 'rgba(255, 255, 255, .2)'
    //                 },
    //                 ticks: {
    //                     display: true,
    //                     color: '#f8f9fa',
    //                     padding: 10,
    //                     font: {
    //                         size: 14,
    //                         weight: 300,
    //                         family: "Roboto",
    //                         style: 'normal',
    //                         lineHeight: 2
    //                     },
    //                 }
    //             },
    //         },
    //     },
    // });

    //
    // const ctx2 = document.getElementById("chart-line").getContext("2d");
    //
    // new Chart(ctx2, {
    //     type: "line",
    //     data: {
    //         labels: ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    //         datasets: [{
    //             label: "Mobile apps",
    //             tension: 0,
    //             borderWidth: 0,
    //             pointRadius: 5,
    //             pointBackgroundColor: "rgba(255, 255, 255, .8)",
    //             pointBorderColor: "transparent",
    //             borderColor: "rgba(255, 255, 255, .8)",
    //             borderColor: "rgba(255, 255, 255, .8)",
    //             borderWidth: 4,
    //             backgroundColor: "transparent",
    //             fill: true,
    //             data: [50, 40, 300, 320, 500, 350, 200, 230, 500],
    //             maxBarThickness: 6
    //
    //         }],
    //     },
    //     options: {
    //         responsive: true,
    //         maintainAspectRatio: false,
    //         plugins: {
    //             legend: {
    //                 display: false,
    //             }
    //         },
    //         interaction: {
    //             intersect: false,
    //             mode: 'index',
    //         },
    //         scales: {
    //             y: {
    //                 grid: {
    //                     drawBorder: false,
    //                     display: true,
    //                     drawOnChartArea: true,
    //                     drawTicks: false,
    //                     borderDash: [5, 5],
    //                     color: 'rgba(255, 255, 255, .2)'
    //                 },
    //                 ticks: {
    //                     display: true,
    //                     color: '#f8f9fa',
    //                     padding: 10,
    //                     font: {
    //                         size: 14,
    //                         weight: 300,
    //                         family: "Roboto",
    //                         style: 'normal',
    //                         lineHeight: 2
    //                     },
    //                 }
    //             },
    //             x: {
    //                 grid: {
    //                     drawBorder: false,
    //                     display: false,
    //                     drawOnChartArea: false,
    //                     drawTicks: false,
    //                     borderDash: [5, 5]
    //                 },
    //                 ticks: {
    //                     display: true,
    //                     color: '#f8f9fa',
    //                     padding: 10,
    //                     font: {
    //                         size: 14,
    //                         weight: 300,
    //                         family: "Roboto",
    //                         style: 'normal',
    //                         lineHeight: 2
    //                     },
    //                 }
    //             },
    //         },
    //     },
    // });

    // const ctx3 = document.getElementById("chart-line-tasks").getContext("2d");
    //
    // new Chart(ctx3, {
    //     type: "line",
    //     data: {
    //         labels: ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    //         datasets: [{
    //             label: "Mobile apps",
    //             tension: 0,
    //             borderWidth: 0,
    //             pointRadius: 5,
    //             pointBackgroundColor: "rgba(255, 255, 255, .8)",
    //             pointBorderColor: "transparent",
    //             borderColor: "rgba(255, 255, 255, .8)",
    //             borderWidth: 4,
    //             backgroundColor: "transparent",
    //             fill: true,
    //             data: [50, 40, 300, 220, 500, 250, 400, 230, 500],
    //             maxBarThickness: 6
    //
    //         }],
    //     },
    //     options: {
    //         responsive: true,
    //         maintainAspectRatio: false,
    //         plugins: {
    //             legend: {
    //                 display: false,
    //             }
    //         },
    //         interaction: {
    //             intersect: false,
    //             mode: 'index',
    //         },
    //         scales: {
    //             y: {
    //                 grid: {
    //                     drawBorder: false,
    //                     display: true,
    //                     drawOnChartArea: true,
    //                     drawTicks: false,
    //                     borderDash: [5, 5],
    //                     color: 'rgba(255, 255, 255, .2)'
    //                 },
    //                 ticks: {
    //                     display: true,
    //                     padding: 10,
    //                     color: '#f8f9fa',
    //                     font: {
    //                         size: 14,
    //                         weight: 300,
    //                         family: "Roboto",
    //                         style: 'normal',
    //                         lineHeight: 2
    //                     },
    //                 }
    //             },
    //             x: {
    //                 grid: {
    //                     drawBorder: false,
    //                     display: false,
    //                     drawOnChartArea: false,
    //                     drawTicks: false,
    //                     borderDash: [5, 5]
    //                 },
    //                 ticks: {
    //                     display: true,
    //                     color: '#f8f9fa',
    //                     padding: 10,
    //                     font: {
    //                         size: 14,
    //                         weight: 300,
    //                         family: "Roboto",
    //                         style: 'normal',
    //                         lineHeight: 2
    //                     },
    //                 }
    //             },
    //         },
    //     },
    // });

    // Statistics
    $.getJSON("copo/stats/numbers")
        .done(function (data) {
            $("#num_samples").html(data.samples)
            $("#num_profiles").html(data.profiles)
            $("#num_users").html(data.users)
            $("#num_uploads").html(data.datafiles)
        }).error(function (error) {
        console.log(`Error: ${error}`)
    })

    // World map

    const markers = [{
        coords: [31.230391, 121.473701],
        name: "Shanghai"
    },
        {
            coords: [28.704060, 77.102493],
            name: "Delhi"
        },
        {
            coords: [6.524379, 3.379206],
            name: "Lagos"
        },
        {
            coords: [35.689487, 139.691711],
            name: "Tokyo"
        },
        {
            coords: [23.129110, 113.264381],
            name: "Guangzhou"
        },
        {
            coords: [40.7127837, -74.0059413],
            name: "New York"
        },
        {
            coords: [34.052235, -118.243683],
            name: "Los Angeles"
        },
        {
            coords: [41.878113, -87.629799],
            name: "Chicago"
        },
        {
            coords: [51.507351, -0.127758],
            name: "London"
        },
        {
            coords: [40.416775, -3.703790],
            name: "Madrid "
        }
    ];
    const map = new jsVectorMap({
        map: "world",
        selector: "#world_map",
        draggable: true,
        zoomButtons: true,
        zoomOnScroll: true,
        zoomAnimate: true,
        zoomOnScrollSpeed: 3,
        zoomMax: 12,
        zoomMin: 1,
        markers: markers,
        markerStyle: {
            initial: {
                r: 9,
                strokeWidth: 7,
                stokeOpacity: .4,
                fill: '#3B7DDD'
            },
            hover: {
                fill: '#6f42c1',
                stroke: '#6f42c1'
            }
        },

    });
    window.addEventListener("resize", () => {
        map.updateSize();
        map.set.re
    });

});