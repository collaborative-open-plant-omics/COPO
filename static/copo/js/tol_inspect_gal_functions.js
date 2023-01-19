/** Created by AProvidence on 16012023
 * Functions defined are called from 'copo_tol_inspect_gal' web page
 */

const fadeSpeed = 'fast';
$(document).ready(function () {
    const copoTOLInspectionURL = "/copo/tol_inspect";

    // add field names here which you want to use for the 'tol_inspect_gal' pie chart
    included_fields = ["ORDER_OR_GROUP", "FAMILY", "GENUS", "SCIENTIFIC_NAME"]

    $(document).on("click", ".tol_inspect", function () {
        document.location = copoTOLInspectionURL;
    })

    $(document).on("click", ".taxonomyLevel_fieldName", populate_pie_chart)

    $(document).on("click", ".selectable_row, .hot_tab", get_selected_gal_name_in_row)

    // Get the element with id="defaultOpen" and click on it
    document.getElementById("defaultTab").click();

    $(document).data("gal_names_lst", [])
    $(".taxonnomy_levelsDiv").hide()// hide on load

    get_gal_names()

});

function populate_pie_chart(el) {
    const gal_field_name = "GAL"
    let gal_name_row = $(document).data("selected_row")
    let gal_field_value = $(gal_name_row).find("td").text()
    let taxonomy_field_name = el.target.value
    let sample_panel = $("#sample_panel")

    // Remove previous active taxonomy level
    let previous_active_taxonomy_level = $("#taxonomyLevelsDivID > input.active_taxonomy_level")
    previous_active_taxonomy_level.css({"background-color": ""});

    $('#taxonomyLevelsDivID input.active_taxonomy_level').removeClass('active_taxonomy_level')

    // Set active taxonomy level
    $(el.target).addClass("active_taxonomy_level")
    $(el.target).css({"background-color": "#fff3ce"})

    $("#spinner").show()

    $.getJSON(`copo/sample/sample_field/${gal_field_name}/${gal_field_value}`)
        .done(function (samples) {
            let data = samples.data

            if (data.length) {
                let pie_chart_labels = [];
                let pie_chart_labels_values = [];
                let pie_chart_background_colours = [];
                let pie_chart_labels_distinct;

                const header = $("<h4/>", {html: "Taxonomy"});

                sample_panel.find(".labelling").empty().append(header)

                $(data).each(function (idx, db_data) {
                    for (let db_field_name in db_data) {
                        if (taxonomy_field_name === db_field_name && included_fields.includes(db_field_name)) {
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
                if (Chart.getChart("chartjs-dashboard-pie") !== undefined) Chart.getChart("chartjs-dashboard-pie").destroy()

                const pieChartCtx = document.getElementById("chartjs-dashboard-pie").getContext('2d');

                new Chart(pieChartCtx, {
                    type: "pie",
                    data: {
                        labels: pie_chart_labels_distinct,
                        datasets: [{
                            data: pie_chart_labels_values,
                            backgroundColor: pie_chart_background_colours,
                            borderWidth: 5
                        }]
                    },
                    options: {
                        plugins: {
                            legend: {
                                display: true,
                                position: 'right',
                            },
                            tooltip: {
                                callbacks: {
                                    label: ({
                                                label,
                                                formattedValue
                                            }) => `\xa0${taxonomy_field_name} name: ${label}; Number of sample associations: ${formattedValue}`
                                }
                            },
                        },
                    }
                });

                $(".taxonnomy_levelsDiv").show()

                populate_bar_graph() // Populate the bar graph showing the goal statistics for the selected GAL

            } else {
                let content
                if (data.hasOwnProperty("locked")) {
                    content = $("<h4/>", {
                        html: "View is locked by another User. Try again later."
                    })
                } else {
                    content = $("<h4/>", {
                        html: "Taxonomy Unavailable"
                    })
                }
                sample_panel.find(".labelling").empty().html(content)
            }
            $("#spinner").fadeOut("fast")

        }).error(function (error) {
        console.error(`ERROR: ${error.message}`)
    });
}

function populate_bar_graph() {
    // Build bar graph
    let gal_names_lst = $(document).data("gal_names_lst")
    let bar_graph_background_colours = []
    let bar_graph_border_colours = []
    let roundValue = Math.round, rndmValue = Math.random, maxNum = 255;

    bar_graph_background_colours = Array.apply(null, Array(gal_names_lst.length)).map(function () {
        return 'rgba(' + roundValue(rndmValue() * maxNum) + ',' + roundValue(rndmValue() * maxNum) + ',' + roundValue(rndmValue() * maxNum) + 0.2 + ')';
    })

    bar_graph_border_colours = Array.apply(null, Array(gal_names_lst.length)).map(function () {
        return 'rgba(' + roundValue(rndmValue() * maxNum) + ',' + roundValue(rndmValue() * maxNum) + ',' + roundValue(rndmValue() * maxNum) + ')';
    })


    // Check if there is an existing instance of bar graph, if there is, destroy it
    if (Chart.getChart("barGraphID") !== undefined) Chart.getChart("barGraphID").destroy()

    const barGraphCtx = document.getElementById("barGraphID").getContext('2d');
    new Chart(barGraphCtx, {
        type: "bar",
        data: {
            labels: gal_names_lst,
            datasets: [{
                axis: 'y',
                label: 'My First Dataset',
                data: [65, 59, 80, 81, 56, 55, 40],
                fill: false,
                backgroundColor: bar_graph_background_colours,
                //     [
                //     'rgba(255, 99, 132, 0.2)',
                //     'rgba(255, 159, 64, 0.2)',
                //     'rgba(255, 205, 86, 0.2)',
                //     'rgba(75, 192, 192, 0.2)',
                //     'rgba(54, 162, 235, 0.2)',
                //     'rgba(153, 102, 255, 0.2)',
                //     'rgba(201, 203, 207, 0.2)'
                // ],
                borderColor: bar_graph_border_colours,
                //     [
                //     'rgb(255, 99, 132)',
                //     'rgb(255, 159, 64)',
                //     'rgb(255, 205, 86)',
                //     'rgb(75, 192, 192)',
                //     'rgb(54, 162, 235)',
                //     'rgb(153, 102, 255)',
                //     'rgb(201, 203, 207)'
                // ],
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            plugins: {
                tooltip: {
                    callbacks: {
                        label: ({
                                    label,
                                    formattedValue
                                }) => `\xa0GAL name: ${label}; Goal percentage: ${formattedValue}%`
                    }
                },
            },
        }
    });

}

function get_selected_gal_name_in_row(ev) {
    // Get samples for the gal name clicked in the left-hand panel
    // Pie chart is automatically populated based on the selected gal name
    // and the first taxonomy level which is automatically clicked
    // in the right-hand panel
    jQuery.support.cors = true;
    let row;
    let first_taxonomy_level;

    if ($(ev.currentTarget).is("td") || $(ev.currentTarget).is("tr")) {
        // we have clicked a gal name on the left-hand list
        $(document).data("selected_row", $(ev.currentTarget))
        row = $(document).data("selected_row")
        $(".selected").removeClass("selected")
        $(row).addClass("selected")

        first_taxonomy_level = $('#taxonomyLevelsDivID').find('input').first().click()
        first_taxonomy_level.click()
    }
}

function get_gal_names() {
    // get gals and populate left hand column
    let gal_names = $("#gal_names")
    $.ajax({
        url: "/copo/get_gal_names",
        method: "GET",
        dataType: "json",
        data: {}
    }).done(function (data) {
        // Clear existing data in the gal names' table
        if ($.fn.DataTable.isDataTable('#gal_names')) {
            gal_names.DataTable().clear().destroy();
        }
        $(document).data("gal_names_lst", data)
        $(data).each(function (d) {
            gal_names.find("tbody").append("<tr class='selectable_row'><td style='max-width: 10px; text-align: center'>" + data[d] + "</td></tr>")

        })
        $($("#gal_names tr")[1]).click() // Click first gal name displayed

        // gal_names.DataTable({
        //     responsive: true,
        //     paging: false,
        //     dom: '<"top"f>rt<"bottom"lp><"clear">',
        //     "order": [[1, "desc"]],
        //
        // })

    }).error(function (error) {
        console.error(`Error: ${error.message}`)
    })
}

function showTab(evt, tabName) {
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
    evt.currentTarget.className += " active";
}


function randomRGB_backgroundColour() {
    var roundValue = Math.round, rndmValue = Math.random, maxNum = 255;
    return 'rgba(' + roundValue(rndmValue() * maxNum) + ',' + roundValue(rndmValue() * maxNum) + ',' + roundValue(rndmValue() * maxNum) + ')';
}