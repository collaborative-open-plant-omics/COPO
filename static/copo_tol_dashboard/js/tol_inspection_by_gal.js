/** Created by AProvidence on 16012023
 * Functions defined are called from 'copo_tol_inspect_gal' web page
 */

const fadeSpeed = 'fast';
$(document).ready(function () {
    const copoTOLInspectionURL = "/copo/tol_inspect";
    const copoTolDashboardURL = "/copo/dashboard/tol";
    const accessionsDashboardURL = "/copo/dashboard/accessions";
    let taxonomyLevelsDivID = $("#taxonomyLevelsDivID")

    $(document).on("click", ".tol_inspect", function () {
        document.location = copoTOLInspectionURL;
    })

    $(document).on("click", ".copo_tol_dashboard", function () {
        document.location = copoTolDashboardURL
    })

    $(document).on("click", ".copo_accessions", function () {
        document.location = accessionsDashboardURL
    })

    $(document).on("click", ".taxonomyLevel_fieldName", function (el) {
        let previous_active_taxonomy_level = $("#taxonomyLevelsDivID > input.active_taxonomy_level")
        let taxonomy_field_name = el.target === undefined || el.target === null ? previous_active_taxonomy_level.val() : el.target.value
        // Remove previous active taxonomy level
        previous_active_taxonomy_level.css({"background-color": ""});

        $('#taxonomyLevelsDivID input.active_taxonomy_level').removeClass('active_taxonomy_level')

        // Set active taxonomy level
        $(el.target).addClass("active_taxonomy_level")
        $(el.target).css({"background-color": "#fff3ce"})

        populate_pie_chart(previous_active_taxonomy_level)
    })

    $(document).data("gal_names_lst", [])

    taxonomyLevelsDivID.hide()// hide on load

    $(".tablinks").click(function () {
        this.className += " active";
        const tablink2_ID = "galSampleGoalStatisticsTabID";

        // Hide taxonomy levels div if tablink 2 is active/visible
        (!!this.outerHTML.includes(tablink2_ID)) ? taxonomyLevelsDivID.hide() : taxonomyLevelsDivID.show()
    });

    get_gal_names()

    // Highlight active GAL name and populate pie chart based on active taxonomy level
    let table = $("#gal_names").DataTable()

    table.on('click', 'tbody tr', (e) => {
        // Select only one row at a time
        let classList = e.currentTarget.classList;

        if (classList.contains('selected')) {
            classList.remove('selected');
        } else {
            table.rows('.selected').nodes().each((row) => row.classList.remove('selected'));
            classList.add('selected');
            $(document).data("selected_gal_name_row", e.currentTarget)
            let active_taxonomy_level = $("#taxonomyLevelsDivID > input.active_taxonomy_level")

            populate_pie_chart(active_taxonomy_level)
        }

    });
});


function populate_pie_chart(el) {
    let gal_name_row = $(document).data("selected_gal_name_row") || $("#gal_names").DataTable().rows('.selected').nodes()[0]
    let gal_field_value = $(gal_name_row).find("td").text()
    let sample_panel_tol_inspect_gal = $("#sample_panel_tol_inspect_gal")
    let match_items = {"GAL": gal_field_value}
    let taxonomy_field_name = $("#taxonomyLevelsDivID > input.active_taxonomy_level").val()
    let component_loader = $('.piechart_component_loader')

    $('#pieChartID').hide()
    $("#taxonomyLevelsDivID").hide()
    $("#spinner").show()

    if (!window.location.href.includes("dashboard/tol")) {
        component_loader.find('.piechart_spinner').toggleClass('hidden').toggleClass('active')
    }

    $("#taxonomy_data_status").text("Loading...")

    $.ajax({
        url: "/copo/get_samples_by_search_faceting/",
        data: {"match_items": JSON.stringify(match_items)},
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        method: "POST",
        dataType: "json"
    }).done(function (data) {
        let included_fields_tol_inspect_gal;

        if (data.length) {
            let pie_chart_labels = [];
            let pie_chart_labels_values = [];
            let pie_chart_background_colours = [];
            let pie_chart_labels_distinct;

            const header = $("<h4/>", {html: "Details"});

            // add field names here which you want to use for the 'tol_inspect_gal' pie chart
            included_fields_tol_inspect_gal = ["ORDER_OR_GROUP", "FAMILY", "GENUS", "SCIENTIFIC_NAME"]

            sample_panel_tol_inspect_gal.find(".labelling").empty().append(header)

            $(data).each(function (idx, db_data) {
                for (let db_field_name in db_data) {
                    if (taxonomy_field_name === db_field_name && included_fields_tol_inspect_gal.includes(db_field_name)) {
                        let selected_taxonomy_field_value = db_data[db_field_name]
                        pie_chart_labels.push(selected_taxonomy_field_value)
                    }
                }

                // Count occurences of taxonomy field value in an array of taxonomy field values
                pie_chart_labels_distinct = [...new Set(pie_chart_labels)]; // unique pie chart labels

                const field_name_occurences = pie_chart_labels.reduce((acc, e) => acc.set(e, (acc.get(e) || 0) + 1), new Map());
                pie_chart_labels_values = [...field_name_occurences.values()]

                // Generate pie chart data colour according to the number of (distinct) pie chart labels/values
                pie_chart_background_colours = Array.apply(null, Array(pie_chart_labels_distinct.length)).map(function () {
                    return '#' + Math.floor(Math.random() * 16777215).toString(16);
                })
            })

            // Build pie chart
            // Check if there is an existing instance of piechart, if there is, destroy it
            if (Chart.getChart("pieChartID") !== undefined) Chart.getChart("pieChartID").destroy()

            let pieChartID = document.getElementById("pieChartID")

            if (typeof pieChartID !== 'undefined' && pieChartID !== null) {
                const pieChartCtx = pieChartID.getContext('2d');

                new Chart(pieChartCtx, {
                    type: "pie", data: {
                        labels: pie_chart_labels_distinct, datasets: [{
                            data: pie_chart_labels_values,
                            backgroundColor: pie_chart_background_colours,
                            borderWidth: 5
                        }]
                    }, 
                    options: {
                        maintainAspectRatio: false, // Remove extra padding around the pie chart
                        responsive: true,
                        plugins: {
                            // maintainAspectRatio: false,
                            legend: {
                                display: true, position: 'right', maxWidth: 200,
                                labels: {
                                    usePointStyle: true,
                                    boxWidth: 6 // Get circular symbols instead of rectangular symbols
                                },
                            }, tooltip: {
                                callbacks: {
                                    label: ({
                                                label, formattedValue
                                            }) => [`\xa0\xa0Name of ${taxonomy_field_name}: ${label}`, `\xa0\xa0Number of sample associations: ${formattedValue}`]
                                },
                            },
                        },
                    },
                    plugins:[
                        {
                            id: 'emptyPieGraph',
                            afterDraw: function(chart) {
                                // No data is present
                                if (chart.data.datasets[0].data.every(item => item === 0)) {
                                    let ctx = chart.$context.chart.ctx
                                    let width = chart.$context.chart.width
                                    let height = chart.$context.chart.height;
                                    
                                    chart.clear();
                                    ctx.save();
                                    ctx.textAlign = 'center';
                                    ctx.fillStyle = '#344767';
                                    ctx.strokeStyle = '#344767';
                                    ctx.font = "bold 30px 'Helvetica Nueue'";
                                    ctx.textBaseline = 'middle';
                                    ctx.fillText('No data to display', width / 2, height / 2);
                                    ctx.restore();

                                    $("#spinner").fadeOut("fast")
                                    sample_panel_tol_inspect_gal.find(".labelling").empty().html(content)
                                    $("#taxonomy_data_status").text("Idle")
                                }
                            }
                    }
                    ]
                });
                // Set pie chart height and width on the 'tol_dashboard' web page
                if (window.location.href.includes('dashboard/tol')) {
                    $('#pieChartID').css({'height': '400', 'width': '500'})
                }
            }

            populate_bar_graph() // Populate the bar graph showing the goal statistics for the selected GAL

            $("#taxonomy_data_status").text("Idle")
            $("#taxonomyLevelsDivID").show()

            if (window.location.href.includes("dashboard/tol")) {
                component_loader.find('.piechart_spinner').toggleClass('active').toggleClass('hidden')
                $('.gal_inspection_card').css('margin-top', '0')

                // Set GAL name that is currently being viewed
                const current_gal_name = $("#gal_names").DataTable().data()[0][0]
                if (current_gal_name) $('#current_gal_name').text(`GAL: ${current_gal_name}`)
            } else {
                component_loader.find('.piechart_spinner').toggleClass('active').toggleClass('hidden')
            }

            $("#spinner").fadeOut("fast")
            $('#pieChartID').show()
        } else {
            let content
            if (data.hasOwnProperty("locked")) {
                content = $("<h4/>", {
                    html: "View is locked by another User. Try again later."
                })
            } else {
                content = $("<h4/>", {
                    html: "Details Unavailable"
                })
            }
            sample_panel_tol_inspect_gal.find(".labelling").empty().html(content)
            $("#taxonomy_data_status").text("Idle")
            component_loader.find('.piechart_spinner').toggleClass('hidden').toggleClass('active')
            component_loader.find('.piechart_spinner').find('.ui.text').text('No data available')

            if (window.location.href.includes("dashboard/tol")) {
                // Set GAL name that is currently being viewed
                const current_gal_name = $("#gal_names").DataTable().data()[0][0]
                if (current_gal_name) $('#current_gal_name').text(`GAL: ${current_gal_name}`)
            }
        }
    }).error(function (error) {
        console.log(`Error: ${error.message}`)
    })
}

function populate_bar_graph() {
    // Build bar graph
    let gal_names_lst = $(document).data("gal_names_lst")
    let bar_graph_background_colours
    let bar_graph_border_colours
    let gal_sample_goal_percentage_lst
    let roundValue = Math.round, rndmValue = Math.random, maxNum = 255;

    // Get rgb colours for border colours
    bar_graph_border_colours = Array.apply(null, Array(5)).map(function () {
        return 'rgb(' + roundValue(rndmValue() * maxNum) + ',' + roundValue(rndmValue() * maxNum) + ',' + roundValue(rndmValue() * maxNum) + ')';
    })

    // Add alpha channel i.e. 'a' to each rgb colour in the list of border colours
    bar_graph_background_colours = bar_graph_border_colours.map(colour => colour.replace(')', ', 0.2)').replace('rgb', 'rgba'));

    // Generate a random number between 1 and 100
    gal_sample_goal_percentage_lst = Array.apply(null, Array(gal_names_lst.length)).map(function () {
        return Math.floor((Math.random() * 100) + 1);
    })
    // Check if there is an existing instance of bar graph, if there is, destroy it
    if (Chart.getChart("barGraphID") !== undefined) Chart.getChart("barGraphID").destroy()

    let barGraphID = document.getElementById("barGraphID")
    if (typeof barGraphID !== 'undefined' && barGraphID !== null) {
        const barGraphCtx = barGraphID.getContext('2d');
        new Chart(barGraphCtx, {
            type: "bar", data: {
                labels: gal_names_lst, datasets: [{
                    axis: 'y',
                    data: gal_sample_goal_percentage_lst,
                    fill: false,
                    backgroundColor: bar_graph_background_colours,
                    borderColor: bar_graph_border_colours,
                    borderWidth: 1
                }]
            }, options: {
                responsive: true,
                indexAxis: 'y', plugins: {
                    legend: {
                        display: false
                    }, tooltip: {
                        callbacks: {
                            label: ({
                                        label, formattedValue
                                    }) => `\xa0GAL name: ${label}; Goal percentage: ${formattedValue}%`
                        },
                    },
                },
            }
        });
    }


}

function get_selected_gal_name_in_row(table) {
    // Pie chart is automatically populated based on the selected gal name
    // and the first taxonomy level which is automatically clicked
    // in the right-hand panel

    // Show piechart for the GAL that is is selected
    if (table.rows({selected: true}).any() === true) {
        let first_taxonomy_level;
        let spinner = $("#spinner")
        table.row($(document).data("selected_gal_name_row")).select();
        // Click on the first taxonomy level
        first_taxonomy_level = $('#taxonomyLevelsDivID').find('input').first()
        first_taxonomy_level.click()
        spinner.show()
        $("#taxonomyPieChartTabID").show() // Show pie chart
        spinner.fadeOut("fast")
    }
}

function get_gal_names() {
    // Get GALs and populate left hand column
    let tableID = 'gal_names';
    let gal_names_table = $(`#${tableID}`)

    $.ajax({
        url: "/copo/get_gal_names", method: "GET", dataType: "json", data: {}
    }).done(function (data) {
        if (data.length == 0){
            // Set piechart component to empty if no data is found in the 'gal_names' table
            // !$('#gal_names').DataTable().data().any()
            let sample_panel_tol_inspect_gal = $("#sample_panel_tol_inspect_gal")
            sample_panel_tol_inspect_gal.find('.labelling').text('Details Unavailable')
            sample_panel_tol_inspect_gal.find('.tab').remove()

            // Set no data to display if on the 'tol_dashboard' web page
            if (window.location.href.includes('dashboard/tol')) {
                let  piechart_component_loader = $('.piechart_component_loader')
                $('#pieChartID').remove()
                $('#taxonomyLevelsDivID').remove()
                piechart_component_loader.find('.piechart_spinner').toggleClass('active').toggleClass('hidden')
                $('<div class="emptyPiechartInfo">Details unavailable</div>').insertAfter(piechart_component_loader)
                $('.gal_inspection_card').css('margin-top', '44%')
            }
            
            return False
        }

        // Clear existing data in the gal names' table
        if ($.fn.DataTable.isDataTable(`#${tableID}`)) {
            gal_names_table.DataTable().clear().destroy();
        }
        $(document).data("gal_names_lst", data)
        $(data).each(function (d) {
            gal_names_table.find("tbody").append("<tr class='gal_name_selectable_row'><td style='max-width: 10px; text-align: center'>" + data[d] + "</td></tr>")
        })

        // Make "gal_names" table
        let table = gal_names_table.DataTable({
            select: 'single', // Allow only one row to be selected at a time
            responsive: true,
            ordering: true,
            paging: false,
            destroy: true,
            bDestroy: true,
            dom: '<"top"f>rt<"bottom"lp><"clear">',
            "order": [[0, "asc"]], // Order 'GAL' column in ascending order
        })

        // Add a placeholder to the search box
        let table_wrapper = $(`#${tableID}_wrapper`)
        table_wrapper
            .find(".dataTables_filter")
            .find("input[type='search']")
            .attr("placeholder", "Search GAL names")
       
        // Select first gal name displayed by default
        // This will trigger the pie chart to be displayed
        table.row(':eq(0)', {page: 'current'}).select()

        get_selected_gal_name_in_row(table)
    }).error(function (error) {
        console.log(`Error: ${error.message}`)
    })
}

function showTab(tabName) {
    let i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
}


