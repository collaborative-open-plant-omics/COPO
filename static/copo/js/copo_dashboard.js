$(document).ready(function () {
    // Card body
    const copoStatisticsURL = "/copo/stats";
    const copoGALInspectionURL = "/copo/tol_inspect/gal";
    const copoTOLInspectionURL = "/copo/tol_inspect";

    $(document).on("click", ".statistics_card .statistics_card_title", function () {
        document.location = copoStatisticsURL
    })

    $(document).on("click", ".gal_inspection_card .gal_inspection_card_title", function () {
        document.location = copoGALInspectionURL;
    })

    $(document).on("click", ".tol_inspect_card .tol_inspect_card_title", function () {
        document.location = copoTOLInspectionURL;
    })

    // Statistics bar chart
    const barChartCtx = document.getElementById('chart-bars').getContext("2d");

    new Chart(barChartCtx, {
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

    // GAL Inspection pie chart
    const pieChartCtx = document.getElementById("chartjs-dashboard-pie").getContext('2d');

    new Chart(pieChartCtx, {
        type: "pie",
        data: {
            labels: ["Chrome", "Firefox", "IE"],
            datasets: [{
                data: [4306, 3801, 1689],
                index: 0,
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
                position: 'right'
            },
            cutoutPercentage: 75
        }
    });

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

    const markers = [
        {
            latLng: [31.230391, 121.473701],
            name: "Shanghai"
        },
        {
            latLng: [28.704060, 77.102493],
            name: "Delhi"
        },
        {
            latLng: [6.524379, 3.379206],
            name: "Lagos"
        },
        {
            latLng: [35.689487, 139.691711],
            name: "Tokyo"
        },
        {
            latLng: [23.129110, 113.264381],
            name: "Guangzhou"
        },
        {
            latLng: [40.7127837, -74.0059413],
            name: "New York"
        },
        {
            latLng: [34.052235, -118.243683],
            name: "Los Angeles"
        },
        {
            latLng: [41.878113, -87.629799],
            name: "Chicago"
        },
        {
            latLng: [51.507351, -0.127758],
            name: "London"
        },
        {
            latLng: [40.416775, -3.703790],
            name: "Madrid "
        }
    ];

    // const map = new vectorMap({
    //     map: "world",
    //     selector: "#world_map",
    //     draggable: true,
    //     zoomButtons: true,
    //     zoomOnScroll: true,
    //     zoomAnimate: true,
    //     zoomOnScrollSpeed: 3,
    //     zoomMax: 12,
    //     zoomMin: 1,
    //     markers: markers1,
    //     markerStyle: {
    //         initial: {
    //             r: 9,
    //             strokeWidth: 7,
    //             stokeOpacity: .4,
    //             fill: '#3B7DDD'
    //         },
    //         hover: {
    //             fill: '#6f42c1',
    //             stroke: '#6f42c1'
    //         }
    //     },
    //     onLoad: function (event, map) {
    //         $('#world_map').vectorMap('zoomIn');
    //     }
    //
    // });


    $('#world_map').vectorMap({
        map: 'world_mill',
        backgroundColor: 'none', // 'aliceblue',
        draggable: true,
        markersSelectable: false,
        regionsSelectable: false,
        zoomAnimate: true,
        zoomOnScroll: true,
        zoomOnScrollSpeed: 3,
        hoverColor: false,
        hoverOpacity: 0.7,
        normalizeFunction: 'polynomial',
        scaleColors: ['#C8EEFF', '#0071A4'],
        markers: get_map_location_markers(),
        markerStyle: {
            initial: {
                r: 5,
                fill: '#3B7DDD',
                stroke: '#383f47',
                strokeWidth: 2,
                stokeOpacity: .2,
            },
            hover: {
                fill: '#383f47',
                stroke: '#383f47'
            }
        },
        regionStyle: {
            initial: {
                fill: 'lightgrey', //'#dee2e8',
                stroke: 'none',
                "stroke-width": 0,
            },
        },
        regionLabelStyle: {
            initial: {
                fill: '#B90E32'
            },
            hover: {
                cursor: 'pointer',
                fill: 'black'
            }
        },
    });

});

function get_map_location_markers() {
//     map = $('#worldmap').vectorMap('get', 'mapObject');
// $.getJSON('http://127.0.0.1/bantools/ip/ip.txt', function(data){
// $.each(data.relays, function(idx, relay)
//     {
//         map.addMarker(relay.or_addresses[0], {'latLng' : [relay.latitude, relay.longitude], "name" : relay.or_addresses[0]});
//     });
// });
// });
    const markers = [
        {
            name: 'Centro Nacional De Análisis Genómico (CNAG), xxxxx',
            latLng: [41.29322842500072, 2.112447951213345], //location
        },
        {
            name: 'DNA Sequencing and Genomics Laboratory, Helsinki Genomics Core Facility (HGCF), xxxxxx',
            latLng: [52.604080415603875, 1.322325116120334], //location
        },
        {
            name: 'Dresden-Concept (DRC), xxxx',
            latLng: [50.953555072066706, 13.765873443664715], //location
        },
        {
            name: 'Earlham Institute (EI), Norwich, England',
            latLng: [52.62318280716785, 1.2555952213587074], //location
        },
        {
            name: 'Industry Partner (IP), xxxx',
            latLng: [53.415313884089315, 14.621839848348806], //location
        },
        {
            name: 'Sanger Institute (SAN), England',
            latLng: [52.078851760344094, 0.1833635227184019], //location
        },
        {
            name: 'Scilifelab (SCI), xxxx',
            latLng: [59.35025588644969, 18.02342940480995], //location
        },
        {
            name: 'Svardal Lab, Antwerp (SVL), xxxx',
            latLng: [51.204388155984645, 4.383337520422855], //location
        },
        {
            name: 'University of Bari  (UBA), xxxx',
            latLng: [41.09506928572348, 16.88037847340563], //location
        },
        {
            name: 'University Of Florence (FL), xxxx',
            latLng: [43.7443574368754, 11.222120017904818], //location
        },
        {
            name: 'West German Genome Centre (WGGC), xxxx',
            latLng: [51.51577076977291, -0.058774328461889375], //location
        }

    ]

    return markers
}