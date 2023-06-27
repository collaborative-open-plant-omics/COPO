$(document).ready(function () {
    const acceptRejectSampleURL = "/copo/accept_reject_sample"
    const tolInspectURL = "/copo/tol_inspect"
    const component = "accessions";
    const copoVisualsURL = "/copo/copo_accessions_visualise/";
    const componentMeta = get_accession_component_meta(component);
    const componentName = $("#nav_component_name").val();

    $(document).data("isSampleProfileTypeStandalone", false)
    $(document).data("isUserProfileActive", true)
    $(document).data("showAllCOPOAccessions", false)

    $(document).on("click", ".accept_reject_samples", function (evt) {
        document.location = acceptRejectSampleURL
    })

    $(document).on("click", ".tol_inspect", function (evt) {
        document.location = tolInspectURL
    })

    $(document).on("click", ".btn-toggle1 .btn-toggle2", toggle_accessions_view)

    $(document).on("change", ".filter-accessions", filterAccessionTypes)

    $(document).on("click", ".copo_accessions", function (evt) {
        $(document).data("showAllCOPOAccessions", true)
        const tableLoader = $('<div class="copo-i-loader"></div>');
        let table_id = "*"
        // load_all_COPO_accessions_records(componentMeta, copoVisualsURL)
        load_accessions_records(componentMeta, copoVisualsURL);
        if (tableLoader) tableLoader.remove(); //remove loader
        // if ($(".table-parent-div").length) {
        //     $(table_id).find(".table-parent-div").show();
        // }
        if ($(".page-welcome-message").length) {
            $(table_id).find(".page-welcome-message").hide();
        }
    })

    //trigger refresh of table
    $('body').on('refreshtable', function (event) {
        render_accessions_table(globalDataBuffer, componentMeta);
    });


    if (groups.includes("dtol_sample_managers") || groups.includes("erga_sample_managers") || groups.includes("dtolenv_sample_managers")) {
        $(".accept_reject_samples").show()
    }

    if (groups.includes("dtol_users") || groups.includes("dtol_sample_managers") || groups.includes("erga_users") || groups.includes("erga_sample_managers") || groups.includes("dtolenv_sample_managers")) {
        $(".tol_inspect").show()
    }

    // Set up global navigation components
    do_accession_page_controls(componentName);

    // Load records
    load_accessions_records(componentMeta, copoVisualsURL);

    // Instantiate/refresh tooltips
    refresh_accessions_tool_tips();

    // Instantiate based on profile type
    let profile_type = $("#profile_type").val()
    let groupBtn2 = $('.groupBtn2')

    if (profile_type.includes("Stand-alone")) {
        $(document).data("isSampleProfileTypeStandalone", true)

        // Retain toggled button on "Standalone projects accessions" option
        if (groupBtn2.find('.active').text().includes("Other Projects' Accessions")) {
            groupBtn2.find('.btn').toggleClass('active');

            if (groupBtn2.find('.btn-success').size() > 0) {
                $('.groupBtn2').find('.btn').toggleClass('btn-success');
            }
            groupBtn2.find('.btn').toggleClass('btn-default');
        }
    }
}); //end document ready

//______________Handlers___________________________________
function set_empty_accessions_component_message(dataRows, table_id = "*") {
    //decides, based on presence of record, to display table or getting started info

    if (dataRows === 0) {
        if ($(".table-parent-div").length) {
            $(table_id).find(".table-parent-div").hide();
            $("#wizard_submissions_label").hide()
            $("#manifest_submissions_label").hide()
        }

        if ($(".page-welcome-message").length) {
            $(table_id).find(".page-welcome-message").show();
        }

    } else {
        if ($(".table-parent-div").length) {
            $(table_id).find(".table-parent-div").show();
            $("#wizard_submissions_label").show()
            $("#manifest_submissions_label").show()
        }

        if ($(".page-welcome-message").length) {
            $(table_id).find(".page-welcome-message").hide();
        }
    }
}

function place_accessions_task_buttons(componentMeta) {
    let class_name = $(document).data("showAllCOPOAccessions") ? "btn-toggle2" : "btn-toggle1";
    //place custom buttons on table

    if (!componentMeta.recordActions.length) {
        return;
    }

    const table = $('#' + componentMeta.tableID).DataTable();

    const customButtons = $('<span/>', {
        style: "padding-left: 15px;",
        class: "copo-table-cbuttons"
    });

    if (class_name === "btn-toggle1") {
        $(table.buttons().container()).append(customButtons);
    }

    if (class_name === "btn-toggle2") {
        $(table.buttons().container()).append(customButtons);
    }

    const actionBTN = $(".accessions-record-action-templates").find("." + class_name).clone();

    // Retain toggled button on "Standalone projects accessions" option
    if ($(document).data("isSampleProfileTypeStandalone") && actionBTN.find('.active').text().includes("Other Projects' Accessions")) {
        actionBTN.find('.btn').toggleClass('active');

        if (actionBTN.find('.btn-success').size() > 0) {
            actionBTN.find('.btn').toggleClass('btn-success');
        }
        actionBTN.find('.btn').toggleClass('btn-default');
    }

    actionBTN.attr("data-table", componentMeta.tableID);
    customButtons.append(actionBTN);

    if (!$(document).data("showAllCOPOAccessions")) {
        // Truncate profile title if it is too long
        let profile_title = $("#profile_title")
        let truncated_profile_title = profile_title.val().length > 10 ?
            jQuery.trim(profile_title.val()).substring(0, 10).trim(this) + '...'
            : profile_title.val()

        // Add profile title to the active toggle button
        $(".btn-toggle1").find(".btn-success").text(`View Profile: ${truncated_profile_title} Accessions`)
    }

    refresh_accessions_tool_tips();
}

function render_accessions_table(data, cols, dataSet, recordIDs, accession_types, componentMeta) {
    const tableID = `#${componentMeta.tableID}`;
    let table = null;

    // if table instance already exists then, clear, destroy and empty the table
    if ($.fn.dataTable.isDataTable(tableID)) {
        $(tableID).DataTable().clear().destroy()
        $(tableID + " tbody").empty();
        $(tableID + " thead").empty();
    }
    let order = $(document).data("isSampleProfileTypeStandalone") ? [[2, 'asc']] : [[0, 'asc']];

    let columnDefinition = $(document).data("isSampleProfileTypeStandalone")
        ? [
            {
                "targets": "_all", // all fields
                "createdCell": function (td, cellData, rowData, row, col) {
                    if (cellData === "") {
                        $(td).addClass("cell-no-content")
                    }
                },
            },
            {
                "targets": "_all", // all fields
                "defaultContent": "",
            },
            {
                'targets': [0], // 'accession' column
                'render': function (data, type, full, meta) {
                    let ebi_url = `https://www.ebi.ac.uk/ena/browser/view/${data}`
                    return '<a class="no-underline" href="' + ebi_url + '"  target="_blank">' + data + '</a>';
                }
            }
        ]
        : [
            {
                "targets": "_all", // all fields
                "defaultContent": "",
            },
            {
                "targets": "_all", // all fields
                "createdCell": function (td, cellData, rowData, row, col) {
                    if (cellData === "") {
                        $(td).addClass("cell-no-content")
                    }
                }
            },
            {
                'targets': [3, 5], // 'biosampleAccession' column & 'sraAccession' column respectively
                'render': function (data, type, full, meta) {
                    let ebi_url = `https://www.ebi.ac.uk/ena/browser/view/${data}`
                    return '<a class="no-underline" href="' + ebi_url + '"  target="_blank">' + data + '</a>';
                }
            },
            {
                'targets': [4], // 'manifest_id' column
                'render': function (data, type, full, meta) {
                    let get_samples_by_manifestID_url = `/api/manifest/${data}`
                    return '<a class="no-underline" href="' + get_samples_by_manifestID_url + '"  target="_blank">' + data + '</a>';
                }
            }
        ]

    table = $(tableID).DataTable({
        data: dataSet,
        select: false,
        searchHighlight: true,
        ordering: true,
        lengthChange: true,
        scrollX: true,
        responsive: true,
        scrollY: 350,
        bDestroy: true,
        buttons: [
            {
                extend: 'csv',
                text: 'Export CSV',
                title: null,
                filename: "copo_" + String(componentMeta.tableID) + "_data"
            },
        ],
        language: {
            "info": "Showing _START_ to _END_ of _TOTAL_ records",
            "search": " ",
            "lengthMenu": "show _MENU_ records",
            select: {
                rows: {
                    _: "%d records selected",
                    0: "<span class='extra-table-info'>Click <span class='fa-stack' style='color:green; font-size:10px;'><i class='fa fa-circle fa-stack-2x'></i><i class='fa fa-plus fa-stack-1x fa-inverse'></i></span> beside a record to view extra details</span>",
                    1: "%d record selected"
                }
            },
            buttons: {}
        },
        order: order,
        fnDrawCallback: function () {
            refresh_accessions_tool_tips();
            const event = jQuery.Event("posttablerefresh"); // individual compnents can trap and handle this event as they so wish
            $('body').trigger(event);
        },
        columns: cols,
        "columnDefs": columnDefinition,
        createdRow: function (row, data, rowIndex) {
            // Add the record ID and accesstion type to each row
            if ($(document).data("isSampleProfileTypeStandalone")) {
                recordIDs.map(function (item) {
                    $(row).attr("id", item.recordID)
                    $(row).addClass("accessions_row");
                    $(row).addClass(componentMeta.tableID + item.recordID);
                    $(row).find('td:last-child').attr("data-profile_id", item.profile_id)
                });
            } else {
                // Iterate over the record IDs and add them to the row as a class
                $.each(recordIDs, function (recordIndex, recordID) {
                    try {
                        if (rowIndex === recordIndex) {
                            $(row).attr("id", recordID)
                            $(row).addClass("accessions_row");
                            $(row).addClass(componentMeta.tableID + recordID);
                        }
                    } catch (err) {
                        console.log(`Error: ${err}`)
                    }
                });

            }

            // Iterate over the accession types and add them as an attribute to each row  in the table
            $.each(accession_types, function (sampleIndex, sample_type) {
                try {
                    if (rowIndex === sampleIndex) $(row).attr("accession_type", sample_type)
                } catch (err) {
                    console.log(`Error: ${err}`)
                }
            });
        },
        dom: 'Bfr<"row"><"row info-rw" i>tlp'
    });

    // Add buttons to the table
    table
        .buttons()
        .nodes()
        .each(function (value) {
            $(this)
                .removeClass("btn btn-default")
                .addClass('tiny ui basic button');
        });

    place_accessions_task_buttons(componentMeta);


    // Filter the rows that are not associated with the current checked "Standalone" accession type
    if ($(document).data("isSampleProfileTypeStandalone")) filterAccessionTypes()

    let table_wrapper = $(tableID + '_wrapper')

    table_wrapper
        .find(".dataTables_filter")
        .find("label").css({"padding": "20px 0 20px 0", "margin-top": "10px"})
        .find("input")
        .removeClass("input-sm")
        .attr("placeholder", "Search " + componentMeta.title)
        .attr("size", 30);

    // Add css to align the buttons to the right
    table_wrapper.find(".dt-buttons").addClass("pull-right")
    table_wrapper.find('.info-rw').hide() // Hide showing 'x' of 'x' row

    // Insert breakpoints after the toggle button
    if ($(document).data("showAllCOPOAccessions")) {
        $("<br><br>").insertAfter(table_wrapper.find(".dt-buttons"))
    } else {
        const actionBTN2 = $(".accessions-record-action-templates").find("." + "groupBtn2").clone();
        table_wrapper.find(".dt-buttons").append($("<br><br>")).append(actionBTN2).append($("<br><br>"))
    }

    // Set height of table to fit the content in the table
    table_wrapper.find(".dataTables_scrollBody").css("height", "fit-content")

    // Add padding between table and show records filter
    table_wrapper.find(".dataTables_length").css("padding-top", "20px")

} // End of func

// function load_all_COPO_accessions_records(componentMeta, copoVisualsURL) {
//     let component_table_loder = $("#component_table_loader")
//     const csrftoken = $.cookie('csrftoken');
//
//     //loader
//     let tableLoader = null;
//
//     if (component_table_loder.length) {
//         tableLoader = $('<div class="copo-i-loader"></div>');
//         component_table_loder.append(tableLoader);
//     }
//
//     $.ajax({
//         url: copoVisualsURL,
//         type: "POST",
//         headers: {
//             'X-CSRFToken': csrftoken
//         },
//         data: {
//             "isSampleProfileTypeStandalone": false,
//             "isUserProfileActive": false,
//         },
//         dataType: "json",
//         success: function (data) {
//             let cols = [];
//             let dataSet = []
//
//             // Sort data by key
//             $.each(data, function (index, item) {
//                 // Remove "_id" from key-value pair from the original object
//                 if (item.hasOwnProperty("_id")) delete data[index]["_id"];
//
//                 // Sort element dictionary by key
//                 data[index] = Object.keys(data[index]).sort().reduce((a, c) => (a[c] = data[index][c], a), {})
//                 dataSet.push(Object.values(item))
//             });
//
//             // Get element keys
//             // If there exists at least one element, the keys will remain the same so just get the
//             // keys from the first element
//             Object.keys(data[0]).forEach(item => {
//                 cols.push({title: convertStringToTitleCase(item), value: item});
//             })
//
//             render_accessions_table(data, cols, dataSet, componentMeta);
//
//             //remove loader
//             if (tableLoader) tableLoader.remove();
//         },
//         error: function () {
//             alert("Couldn't retrieve " + componentMeta.component + " data!");
//         }
//     });
// }

function load_accessions_records(componentMeta, copoVisualsURL) {
    const component_table_loder = $("#component_table_loader")
    const csrftoken = $.cookie('csrftoken');
    let isSampleProfileTypeStandalone = $(document).data("showAllCOPOAccessions") ? false : $(document).data("isSampleProfileTypeStandalone")
    let isUserProfileActive = $(document).data("showAllCOPOAccessions") ? false : $(document).data("isUserProfileActive")

    let tableLoader = null; //loader

    if (component_table_loder.length) {
        tableLoader = $('<div class="copo-i-loader"></div>');
        component_table_loder.append(tableLoader);
    }

    $.ajax({
        url: copoVisualsURL,
        type: "POST",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            "isSampleProfileTypeStandalone": isSampleProfileTypeStandalone, //$(document).data("isSampleProfileTypeStandalone"),
            "isUserProfileActive": isUserProfileActive //$(document).data("isUserProfileActive")

        },
        dataType: "json",
        success: function (data) {
            let accessions_checkboxes = $('.accessions-checkboxes')

            if (data.length === 0) {
                if (accessions_checkboxes.length) accessions_checkboxes.empty()
                set_empty_accessions_component_message(data.length); //display empty component message when there's no record
                $(".copo_accessions").show()
                if (tableLoader) tableLoader.remove(); //remove loader
                return false;
            } else {
                if ($(document).data("showAllCOPOAccessions") && $(document).data("isSampleProfileTypeStandalone")
                    || $(document).data("isUserProfileActive") && $(document).data("isSampleProfileTypeStandalone")) {
                    // Get Stand-alone projects data
                    let column_names = ["Accession", "Alias", "Profile Title"]
                    let cols = [];
                    let accession_types = []
                    let recordIDs = []

                    $.each(data, function (index, item) {
                        let obj = {}

                        // Remove record ID & accession type from key-value pair from the original object
                        // and keep a record of it
                        if (item.hasOwnProperty("_id")) {
                            // recordIDs.push(data[index]._id.$oid)
                            obj.recordID = data[index]._id.$oid
                            delete data[index]._id;
                        }
                        if (item.hasOwnProperty("profile_id")) {
                            // profile_ids.push(data[index].profile_id)
                            obj.profile_id = data[index].profile_id
                            delete data[index].profile_id;
                        }

                        recordIDs.push(obj) // Add record ID & profile ID to the object

                        if (item.hasOwnProperty("accessions")) {
                            // Get accession types
                            Object.keys(data[index].accessions).forEach(item => {
                                accession_types.push(item)
                            })
                            // Get accessions types values
                            let data_array = {}
                            accession_types.map(function (type) {

                                let values_array = []

                                data[index].accessions[type].map(function (i) {
                                    if (i.hasOwnProperty("accession")) {
                                        values_array.push(i.accession)
                                    }
                                    if (i.hasOwnProperty("alias")) {
                                        values_array.push(i.alias)
                                    }

                                    if (i.hasOwnProperty("sample_accession")) {
                                        values_array.push(i.sample_accession)
                                    }
                                    if (i.hasOwnProperty("sample_alias")) {
                                        values_array.push(i.sample_alias)
                                    }
                                });

                                // Append profile title to the end of the array
                                values_array.push(data[index].profile_title)
                                data_array[type] = values_array

                            });

                            // Store "Standalone" accessions data in a global variable
                            $(document).data("standaloneAccessionsData", data_array)

                            delete data[index].accessions;
                        }
                    });


                    // Add filter checkbox to under info panel to right side of screen
                    set_filter_checkboxes(accession_types)

                    // Get element keys
                    // Replace whitespaces in the string with underscores and convert to lowercase
                    column_names.forEach(item => {
                        cols.push({title: item, value: item.toLowerCase().replace(/ /g, "_")})
                    });

                    // Populate the row values for the table based on the accession type
                    let dataSet = []
                    Object.keys($(document).data("standaloneAccessionsData")).forEach(item => {
                        dataSet.push($(document).data("standaloneAccessionsData")[item])
                    })

                    // Render table
                    render_accessions_table(data, cols, dataSet, recordIDs, accession_types, componentMeta);

                    if (tableLoader) tableLoader.remove(); // remove loader
                } else {
                    // Get other projects' data
                    let dataSet = []
                    let cols = [];
                    let accession_types = []
                    let sampleIDs = []


                    $.each(data, function (index, item) {
                        // Remove record ID & project type from key-value pair from the original object
                        // and keep a record of it
                        if (item.hasOwnProperty("_id")) {
                            sampleIDs.push(data[index]._id.$oid)
                            delete data[index]._id;
                        }

                        if (item.hasOwnProperty("tol_project")) {
                            accession_types.push(data[index].tol_project)
                            delete data[index].tol_project;
                        }

                        dataSet.push(Object.values(item))
                    });

                    // Add filter checkbox to under info panel to right side of screen
                    set_filter_checkboxes(accession_types)

                    // Get element keys
                    // If there exists at least one element, the keys will remain the same so just get the
                    // keys from the first element
                    Object.keys(data[0]).forEach(item => {
                        cols.push({title: convertStringToTitleCase(item), value: item});
                    })

                    render_accessions_table(data, cols, dataSet, sampleIDs, accession_types, componentMeta);

                    if (tableLoader) tableLoader.remove(); //remove loader
                }

                // let cols = [];
                // let dataSet = []
                //
                // // Sort data by key
                // $.each(data, function (index, item) {
                //     // Remove "_id" from key-value pair from the original object
                //     if (item.hasOwnProperty("_id")) delete data[index]["_id"];
                //
                //     // Sort element dictionary by key
                //     data[index] = Object.keys(data[index]).sort().reduce((a, c) => (a[c] = data[index][c], a), {})
                //     dataSet.push(Object.values(item))
                // });
                //
                // if ($(document).data("showAllCOPOAccessions")) {
                //     console.log("showAllCOPOAccessions is true")
                //     console.log("data", data)
                //     console.log("dataSet", dataSet)
                //     // load_accessions_records(componentMeta, copoVisualsURL)
                //     // Get element keys
                //     // If there exists at least one element, the keys will remain the same so just get the
                //     // keys from the first element
                //     Object.keys(data[0]).forEach(item => {
                //         cols.push({title: convertStringToTitleCase(item), value: item});
                //     })
                //
                //     render_accessions_table(data, cols, dataSet, componentMeta);
                //
                //     //remove loader
                //     if (tableLoader) tableLoader.remove();
                //
                // } else {
                //     console.log("showAllCOPOAccessions is false")
                //
                //     // Get element keys
                //     // If there exists at least one element, the keys will remain the same so just get the
                //     // keys from the first element
                //     Object.keys(data[0]).forEach(item => {
                //         cols.push({title: convertStringToTitleCase(item), value: item});
                //     })
                //
                //     render_accessions_table(data, cols, dataSet, componentMeta);
                //
                //     if (tableLoader) tableLoader.remove(); //remove loader

                // }

            }
        },
        error: function () {
            alert("Couldn't retrieve " + componentMeta.component + " data!");
        }
    });
}

// function refresh_accessions_tool_tips() {
//     $("[data-toggle='tooltip']").tooltip();
//     $("[data-toggle='popover']").popover();
//     $('.ui.dropdown')
//         .dropdown()
//     ;
//     $('.copo-tooltip')
//         .popup()
//     ;
//     //
//     // apply_color();
//     // refresh_selectbox();
//     // refresh_select2box();
//     // refresh_multiselectbox();
//     // refresh_multiselect2box();
//     // refresh_singleselectbox();
//     // refresh_multisearch();
//     // refresh_ontology_select();
//     // refresh_general_ontology_search();
//     // refresh_general_ontology_select();
//     // refresh_copo_lookup();
//     // refresh_copo_lookup2();
//     //
//     // refresh_range_slider();
//     // auto_complete();
//     //
//     // setup_datepicker();
//
// } //end of func

function toggle_accessions_view() {
    const component = "accessions";
    const copoVisualsURL = "/copo/copo_accessions_visualise/";
    const componentMeta = get_accession_component_meta(component);

    $('.btn-toggle').click(function () {
        $(this).find('.btn').toggleClass('active');

        if ($(this).find('.btn-primary').size() > 0) {
            $(this).find('.btn').toggleClass('btn-primary');
        }
        if ($(this).find('.btn-danger').size() > 0) {
            $(this).find('.btn').toggleClass('btn-danger');
        }
        if ($(this).find('.btn-success').size() > 0) {
            $(this).find('.btn').toggleClass('btn-success');
        }
        if ($(this).find('.btn-info').size() > 0) {
            $(this).find('.btn').toggleClass('btn-info');
        }

        $(this).find('.btn').toggleClass('btn-default');

        // Show all accessions
        if ($(this).find('.active').text().includes("All COPO Accessions")) {
            $(".page-title-custom").find("[title='Profile title']").hide() // Hide profile title
            $(document).data("isUserProfileActive", false)
            load_accessions_records(componentMeta, copoVisualsURL)

            // let copo_accessions_options = $(".dt-buttons ").clone()
            //
            // // Remove breakpoints before the toggle button
            // // copo_accessions_options.previousSibling.remove()
            // copo_accessions_options.prev("br").remove();
            // console.log("previousSibling: ", copo_accessions_options.prev())
            //
            // copo_accessions_options.find('.buttons-csv').remove()
            //
            // copo_accessions_options.insertBefore($(`#${componentMeta.tableID}_filter`))
            //     .find('.active').text('Other Projects\' Accessions')
            //
            // copo_accessions_options.find('.btn-default').text('Stand-alone Projects\' Accessions')
        } else {
            $(".page-title-custom").find("[title='Profile title']").show()
            $(document).data("isUserProfileActive", true)
            load_accessions_records(componentMeta, copoVisualsURL)
        }
    });
} // End of function toggle_accessions_view()

//builds component-page navbar
// function do_page_controls(componentName) {
//     let component = null;
//     const components = get_copo_accessions_components();
//
//     components.forEach(function (comp) {
//         if (comp.component === componentName) {
//             component = comp;
//             return false;
//         }
//     });
//
//     if (component == null) {
//         return false;
//     }
//
//     generate_accession_component_control(component);
//
// } //end of func

// function generate_component_control(component) {
//     const pageHeaders = $(".copo-page-headers"); //page header/icons
//     const pageIcons = $(".copo-page-icons"); //profile component icons
//     const sideBar = $(".copo-sidebar"); //sidebar panels
//     let profileTitleID = $("#profile_title") // profile title ID
//
//     //add profile title
//     if (profileTitleID.length) {
//         const profileTitle = $('<div/>', {
//             class: "page-title-custom",
//             style: "margin-right:10px;",
//             html: "<span title='Profile title' style='color: #8c8c8c; font-size: 18px;'>Profile: " + profileTitleID.val() + "</span>"
//         });
//
//         pageHeaders.append(profileTitle);
//     }
//
//     //add page title
//     const PageTitle = $('<span/>', {
//         class: "page-title-custom",
//         style: "margin-right:10px;",
//         html: component.title
//     });
//
//     pageHeaders.append(PageTitle);
//
//
//     //create panels
//     if (component.sidebarPanels) {
//         const sidebarTemplate = $(".copo-sidebar-templates")
//         const sidebarPanels = sidebarTemplate.clone();
//         const sidebarPanels2 = sidebarPanels.clone();
//         sidebarPanels.find(".nav-tabs").html('');
//         sidebarPanels.find(".tab-content").html('');
//         sidebarTemplate.remove();
//
//
//         component.sidebarPanels.forEach(function (item) {
//             sidebarPanels.find(".nav-tabs").append(sidebarPanels2.find(".nav-tabs").find("." + item));
//             sidebarPanels.find(".tab-content").append(sidebarPanels2.find(".tab-content").find("." + item));
//             // sidebarPanels.find(".profiles-legend").append(sidebarPanels2.find(".profiles-legend").find("." + item));
//         });
//
//         sideBar
//             .append(sidebarPanels.find(".nav-tabs"))
//             .append(sidebarPanels.find(".tab-content"))
//         // .append(sidebarPanels.find(".profiles-legend"));
//
//
//     }
//
//     //create buttons
//     const buttonsSpan = $('<span/>', {style: "white-space:nowrap;"});
//     pageHeaders.append(buttonsSpan);
//     component.buttons.forEach(function (item) {
//         if (component.buttons) {
//             component.buttons.forEach(function (item) {
//                 buttonsSpan.append($("." + item)).append("<span style='display: inline;'>&nbsp;</span>");
//             });
//         }
//     });
//
//     //...and profile component buttons
//     if (component.hasOwnProperty("profile_component") && component.profile_component.toString() === "true") {
//         const pcomponentHTML = $(".pcomponents-icons-templates").clone().removeClass("pcomponents-icons-templates");
//         const pcomponentAnchor = pcomponentHTML.find(".pcomponents-anchor").clone().removeClass("pcomponents-anchor");
//         pcomponentHTML.find(".pcomponents-anchor").remove();
//
//         pageIcons.append(pcomponentHTML);
//
//         const components = get_copo_accessions_components();
//
//         for (let i = 1; i < components.length; ++i) {
//             const comp = components[i];
//             if (comp.hasOwnProperty("profile_component") && comp.profile_component.toString() === "true") {
//
//                 if ((comp.component === component.component)) {
//                     continue;
//                 }
//
//                 const newAnchor = pcomponentAnchor.clone();
//                 pcomponentHTML.append(newAnchor);
//
//                 newAnchor.attr("title", "Navigate to " + comp.title);
//                 newAnchor.attr("href", $("#" + comp.component + "_url").val());
//                 newAnchor.find("i")
//                     .addClass(comp.color)
//                     .addClass(comp.semanticIcon);
//
//             }
//         }
//     }
//
//     //refresh components...
//     // quick_tour_event();
//     refresh_accessions_tool_tips();
// }

// #------------- Helpers -----------------#
// function convertStringToTitleCase(str) {
//     return str.replace(
//         /\w\S*/g,
//         function (txt) {
//             return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
//         }
//     ).replace("_id", " ID")
//         .replace("_name", " Name")
//         .replace("accession", " Accession")
//         .replace("Sra", "SRA")
//
//
// }
