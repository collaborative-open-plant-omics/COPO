$(document).ready(function () {
    const copoStatisticsURL = "/copo/stats";
    const copoGALInspectionURL = "/copo/tol_inspect/gal";
    const copoTOLInspectionURL = "/copo/tol_inspect";

    // Set faceted search/ search filter to 'false' so that search queries are initially
    // done within samples within the user's profile
    $(document).data("filterByCOPODatabaseID", false)

    $(document).on("click", ".statistics_card .statistics_card_title", function () {
        document.location = copoStatisticsURL
    })

    $(document).on("click", ".gal_inspection_card .gal_inspection_card_title", function () {
        document.location = copoGALInspectionURL;
    })

    $(document).on("click", ".tol_inspect_card .tol_inspect_card_title", function () {
        document.location = copoTOLInspectionURL;
    })

    $(document).on("click", "#filterByCOPODatabaseID", function () {
        let checkedValue = !!$("#filterByCOPODatabaseID").is(":checked");
        $(document).data("filterByCOPODatabaseID", checkedValue);
    })

    // Status bar
    $.getJSON("copo/stats/numbers")
        .done(function (data) {
            $("#num_samples").html(data.samples)
            $("#num_profiles").html(data.profiles)
            $("#num_users").html(data.users)
            $("#num_uploads").html(data.datafiles)
        }).error(function (error) {
        console.log(`Error: ${error.message}`)
    })

    // COPO Statistics card
    $.getJSON("copo/stats/combined_stats_json")
        .done(function (data) {
            let lineGraph_x_axis_values = []
            let lineGraph_y_axis_values = []

            lineGraph_x_axis_values = data.map(x => x.date); // x-axis i.e. Number of samples
            lineGraph_y_axis_values = data.map(x => x.samples); // y-axis i.e. Dates

            // Reverse Bar graph x values and y values
            lineGraph_x_axis_values.reverse()
            lineGraph_y_axis_values.reverse()


            // Build bar graph
            // Check if there is an existing instance of bar graph, if there is, destroy it
            if (Chart.getChart("lineGraphID") !== undefined) Chart.getChart("lineGraphID").destroy()

            let lineGraphID = document.getElementById("lineGraphID")

            if (typeof lineGraphID !== 'undefined' && lineGraphID !== null) {
                // new Date(Date.parse(title))

                const lineGraphCtx = document.getElementById('lineGraphID').getContext("2d");
                new Chart(lineGraphCtx, {
                    type: "line",
                    data: {
                        labels: lineGraph_x_axis_values,
                        datasets: [{
                            label: "number of samples",
                            tension: 0,
                            pointRadius: 3,
                            pointHoverRadius: 6,
                            pointBackgroundColor: '#000000',
                            pointHoverBackgroundColor: '#4383b5',
                            pointBorderColor: "transparent",
                            pointHoverBorderColor: 'rgba(255, 255, 255, .2)',
                            borderColor: '#4383b5',
                            borderWidth: 4,
                            pointHoverBorderWidth: 2,
                            backgroundColor: "transparent",
                            fill: true,
                            data: lineGraph_y_axis_values,
                            maxBarThickness: 4

                        }],
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false,
                            },
                            tooltip: {
                                backgroundColor: "#FFFFFF",
                                titleAlign: 'center',
                                bodyAlign: 'center',
                                titleColor: '#000000',
                                titleFont: {size: 14},
                                bodyColor: '#000000',
                                bodyFont: {size: 13},
                                borderColor: 'rgba(255, 255, 255, .2)',
                                borderWidth: 3,
                                boxPadding: 3,
                                callbacks: {
                                    title: function (context) {
                                        let title = context[0].label
                                        return moment(title).format("MMMM dddd D, YYYY")
                                    },
                                    label: ({
                                                label, formattedValue
                                            }) => `\xa0Number of samples: ${formattedValue}`,
                                    labelColor: function (context) {
                                        return {
                                            borderColor: 'transparent',
                                            backgroundColor: 'transparent',
                                        };
                                    },
                                },
                            },
                        },
                        interaction: {
                            intersect: false,
                            mode: 'index',
                        },
                        scales: {
                            y: {
                                title: {
                                    display: true,
                                    text: 'number of samples'
                                },

                                ticks: {
                                    display: true,
                                    color: '#000000', //'#f8f9fa',
                                    padding: 10,
                                    font: {
                                        size: 12,
                                        weight: 300,
                                        family: "sans-serif",
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
                                    color: '#000000', //'#f8f9fa',
                                    padding: 10,
                                    font: {
                                        size: 12,
                                        weight: 300,
                                        family: "sans-serif",
                                        style: 'normal',
                                        lineHeight: 2
                                    },
                                }
                            },
                        },
                    },
                });
            }

        }).error(function (error) {
        console.log(`Error: ${error.message}`)
    })


    // GAL Inspection card
    $($("#gal_names tbody tr")[1]).click()

    // TOL Inspection card
    $($("#profile_titles tr")[1]).click()

    $("table#profile_samples tr th").removeAttr("onclick"); // Disable click event on table rows
    $("#profile_samples").removeClass("table-hover") // Remove hover on table


    // World map
    // Show/Hide "World map is loading" spinner
    $('svg').length > 0 ? $("#spinner_div").hide() : $("#spinner_div").show();
    $.getJSON("gal_and_partners")
        .done(function (data) {
            let map_locations = data.partner_locations_lst.concat(data.gal_locations_lst)
            let map_markers = []
            map_locations.map(x => map_markers.push({
                name: x.name, latLng: [x.latitude, x.longitude], style: {r: x.style.r, fill: x.style.fill},
                city: x.city, state: x.state, country: x.country, samples_count: x.samples_count
            }));

            // Create and populate world map with map markers
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
                markers: map_markers,
                onMarkerClick: function (e, index) {
                    show_map_marker_popup_details(map_markers[index])
                },
                markerStyle: {
                    initial: {
                        // r: 5,
                        // fill: '#3B7DDD',
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
                series: {
                    markers: [{
                        attribute: 'fill',
                        scale: {
                            'yellow': '#F8E23B',
                            'blue': '#3B7DDD',

                        },
                        legend: {
                            horizontal: true,
                            title: 'Key',
                            labelRender: function (v) {
                                return {
                                    yellow: 'PARTNER',
                                    blue: 'GAL',

                                }[v];
                            }
                        }
                    }]
                }
            });
            $("#spinner_div").hide();
        }).error(function (error) {
        console.log(`Error: ${error.message}`)
    })

});


function show_map_marker_popup_details(item) {
    let dialogDiv = $('<div id="map_marker_detailsID"/>')

    // Only include item details if they are not empty
    if (item.name !== "") $('<p><b>Name:</b> ' + item.name + ' </p>').appendTo(dialogDiv)
    if (item.city !== "") $('<p><b>City:</b> ' + item.city + ' </p>').appendTo(dialogDiv)
    if (item.state !== "") $('<p><b>State:</b> ' + item.state + ' </p>').appendTo(dialogDiv)
    if (item.country !== "") $('<p><b>Country:</b> ' + item.country + ' </p>').appendTo(dialogDiv)

    $('<p><b>Number of samples produced:</b> ' + item.samples_count + ' </p>').appendTo(dialogDiv)

    dialogDiv.dialog({modal: true, title: "Details", show: 'clip', hide: 'clip'});
}