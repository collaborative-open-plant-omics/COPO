$(document).ready(function () {
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
            console.log(`Number of samples (y-axis): ${data.samples}`)
            // y-axis label : number of samples
            // Tool tip: Date
            // Number of samples: value
            console.log(`Date (x-axis): ${data.date}`) //%Y-%m-%d" format
        }).error(function (error) {
        console.log(`Error: ${error.message}`)
    })

    const barChartCtx = document.getElementById('chart-bars').getContext("2d");

    new Chart(barChartCtx, {
        type: "line",
        data: {
            labels: ["2022-05-01", "2022-06-01", "2022-07-01", "2022-08-01", "2022-09-01", "2022-10-01", "2022-11-0", "2022-12-01"],
            datasets: [{
                label: "Number of Samples",
                tension: 0,
                pointRadius: 5,
                pointBackgroundColor: "rgba(255, 255, 255, .8)",
                pointBorderColor: "transparent",
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

    // GAL Inspection card
    $($("#gal_names tbody tr")[1]).click()

    // TOL Inspection card
    const project = $("#sample_filter").find(".active").find("a").attr("href");
    get_profile_titles(project)

    // Ensure that the exisiting dataTable (if any at all) is removed before being retinialised
    if ($.fn.DataTable.isDataTable('#profile_samples')) $("#profile_samples").DataTable().clear().destroy();

    let first_profile_row = $($("#profile_titles tr")[1])
    populate_samples_table_based_on_profile_title(first_profile_row) // Call function from 'tol_inspect_funtions' js file
    $('#profile_samples_wrapper .dataTables_scroll > div.dataTables_scrollHead').css({"width": "540px"}) // Set width for samples table


    $("table#profile_samples tr").removeAttr("onclick"); // Disable click event on table rows
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