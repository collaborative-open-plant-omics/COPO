var wizardMessages;
var sampleDescriptionToken = '';
var sampleTableInstance = null;

$(document).ready(function () {
    const acceptRejectSampleURL = "/copo/accept_reject_sample"
    const tolInspectURL = "/copo/tol_inspect"
    const component = "accessions";
    const copoVisualsURL = "/copo/copo_accessions_visualise/";
    const componentMeta = get_component_meta(component);
    const componentName = $("#nav_component_name").val();

    $(document).data("isSampleProfileTypeStandalone", false)

    $(document).on("click", ".accept_reject_samples", function (evt) {
        document.location = acceptRejectSampleURL
    })

    $(document).on("click", ".tol_inspect", function (evt) {
        document.location = tolInspectURL
    })

    $(document).on("click", ".btn-toggle2", toggle_accessions_view)

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

    //set up global navigation components
    do_page_controls(componentName);

    //load records
    load_accessions_records(componentMeta, copoVisualsURL);

    //instantin ate/refresh tooltips
    refresh_accessions_tool_tips();


    // $(".filter-accessions").change(function () {
    //     console.log("Hi")
    //     console.log('accessions_filterTypes:', $(document).data('accessions_filterTypes'))
    //     render();
    // });
    /** Reset accessions_table display to default view*/

    $(document).on("change", ".filter-accessions", render)

}); //end document ready


//_________________________________________________
// Handlers
// Filter accessions table by accession type
const resetDisplay = function () {
    const uncheckedAccessions = getValues($(".filter-accessions:not(:checked)"))

    uncheckedAccessions.forEach(function (type) {
        let rows = $('.accessions_row').filter(function () {
            return $(this).attr('accession_type') === type;
        });

        // Show each row based on the accession type unchecked
        $(rows).each(function () {
            $(this).show()
        });

    });
}

const getValues = function ($el) {
    const items = [];
    $el.each(function () {
        items.push($(this).val());
    });

    return items;
};

const render = function () {
    const selectedAccessions = getValues($(".filter-accessions:checked"));
    console.log("I am here 2")
    console.log("selectedAccessions:", selectedAccessions)
    if ($(".filter-accessions:not(:checked)").length === $('.filter-accessions').length) {
        // If length of all unchecked accession types is equal to the number of accession checkboxes
        // in the filter accession type div, show all table rows
        $(".accessions_row").show();
    } else if (selectedAccessions.length > 0) {
        $(".accessions_row").hide();

        selectedAccessions.forEach(function (type) {
            let rows = $('.accessions_row').filter(function () {
                return $(this).attr('accession_type') === type;
            });

            // Show each row based on the accession type that is checked
            $(rows).each(function () {
                $(this).show()
            });

        });
    } else {
        resetDisplay();
    }
};

// Accessions component
// Set COPO frontpage properties in this dictionary
function get_component_meta(component) {
    let componentMeta = null;
    const components = get_copo_accessions_components();

    components.forEach(function (comp) {
        if (comp.component === component) {
            componentMeta = comp;
            return false;
        }
    });

    return componentMeta
}

function get_copo_accessions_components() {
    return [
        {
            component: 'profile',
            title: 'Work Profiles',
            buttons: ["quick-tour-template", "new-component-template"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
            tableID: 'copo_profiles_table',
            secondaryTableID: 'copo_shared_profiles_table',
            visibleColumns: 4,
            recordActions: ["add_record_all", "edit_record_single", "delete_record_multi"] //specifies action buttons for records manipulation
        },
        {
            component: 'sample',
            title: 'Samples',
            iconClass: "fa fa-filter",
            semanticIcon: "filter", //semantic UI equivalence of fontawesome icon
            countsKey: "num_sample",
            buttons: ["quick-tour-template", "new-samples-template", "new-samples-spreadsheet-template", "new-samples-spreadsheet-template-erga", "accept_reject_samples", "tol_inspect"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
            colorClass: "samples_color",
            color: "olive",
            profile_component: true,
            tableID: 'sample_table',
            recordActions: ["show_sample_source", "describe_record_all", "edit_record_single"],
            visibleColumns: 3 //no of columns to be displayed, if tabular data is required. remaining columns will be displayed in a sub-table
        },
        {
            component: 'accessions',
            title: 'Accessions',
            iconClass: "fa fa-barcode",
            semanticIcon: "barcode", //semantic UI equivalence of fontawesome icon
            countsKey: "num_accessions",
            buttons: ["copo_accessions", "tol_inspect", "accept_reject_samples"],
            sidebarPanels: ["copo-sidebar-info"],
            colorClass: "accessions_color",
            color: "pink",
            profile_component: true,
            tableID: 'accessions_table',
            recordActions: ["btn-toggle1", "btn-toggle2"],
            visibleColumns: 3 //no of columns to be displayed, if tabular data is required. remaining columns will be displayed in a sub-table
        },
        {
            component: 'datafile',
            title: 'Datafiles',
            iconClass: "fa fa-database",
            semanticIcon: "database",
            countsKey: "num_data",
            colorClass: "data_color",
            color: "black",
            buttons: ["quick-tour-template"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
            tableID: 'datafile_table',
            profile_component: true,
            // recordActions: ["describe_record_multi", "unbundle_record_multi", "undescribe_record_multi"],
            recordActions: [],
            visibleColumns: 3
        },
        {
            component: 'submission',
            title: 'Submissions',
            iconClass: "fa fa-envelope",
            semanticIcon: "mail outline",
            countsKey: "num_submission",
            buttons: ["quick-tour-template"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
            colorClass: "submissions_color",
            color: "green",
            tableID: 'submission_table',
            profile_component: true,
            recordActions: [],
            visibleColumns: 3
        },
        {
            component: 'publication',
            title: 'Publications',
            iconClass: "fa fa-paperclip",
            semanticIcon: "attach",
            countsKey: "num_pub",
            buttons: ["quick-tour-template", "new-component-template"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
            colorClass: "pubs_color",
            color: "orange",
            tableID: 'publication_table',
            profile_component: true,
            recordActions: ["add_record_all", "edit_record_single", "delete_record_multi"],
            visibleColumns: 4
        },
        {
            component: 'metadata_template',
            title: 'Metadata Template',
            iconClass: "fa fa-table",
            semanticIcon: "attach",
            countsKey: "num_temp",
            buttons: ["quick-tour-template", "new-component-template"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
            colorClass: "pubs_color",
            color: "blue",
            tableID: 'metadata_template_table',
            recordActions: ["add_record_all", "edit_record_single", "delete_record_multi"],
            visibleColumns: 4
        },
        {
            component: 'person',
            title: 'People',
            iconClass: "fa fa-users",
            semanticIcon: "users",
            countsKey: "num_person",
            buttons: ["quick-tour-template", "new-component-template"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
            colorClass: "people_color",
            color: "red",
            tableID: 'person_table',
            profile_component: true,
            recordActions: ["add_record_all", "edit_record_single"],
            visibleColumns: 5
        },
    ];
}

function place_accessions_task_buttons(componentMeta) {
    let class_name = "btn-toggle2"
    //place custom buttons on table

    if (!componentMeta.recordActions.length) {
        return;
    }

    const table = $('#' + componentMeta.tableID).DataTable();

    const customButtons = $('<span/>', {
        style: "padding-left: 15px;",
        class: "copo-table-cbuttons"
    });

    if (class_name === "btn-toggle2") {
        $(table.buttons().container()).append(customButtons);
    }

    const actionBTN = $(".accessions-record-action-templates").find("." + class_name).clone();

    actionBTN.attr("data-table", componentMeta.tableID);
    customButtons.append(actionBTN);

    refresh_accessions_tool_tips();
}

// Populate Accessions table
// function render_standalone_accessions_table(data, cols, dataSet, recordIDs, accession_types, componentMeta) {
//     const tableID = `#${componentMeta.tableID}`;
//     //set data
//     let table = null;
//
//     console.log('Cols:', cols)
//     console.log('dataSet:', dataSet)
//
//     if ($.fn.dataTable.isDataTable(tableID)) {
//         //if table instance already exists, then do refresh
//         table = $(tableID).DataTable().clear().destroy()
//     }
//
//     if (table) {
//         // table.clear()
//
//         //clear old, set new data
//         // table.rows().deselect();
//         // table
//         //     .clear()
//         //     .draw();
//         // table
//         //     .rows
//         //     .add(dataSet);
//         // table
//         //     .columns
//         //     .add(cols)
//         // table
//         //     .search('')
//         //     .columns()
//         //     .search('')
//         //     .draw();
//         table = $(tableID).DataTable({
//             data: dataSet,
//             select: false,
//             searchHighlight: true,
//             ordering: true,
//             lengthChange: true,
//             scrollX: true,
//             scrollY: 350,
//             bDestroy: true,
//             buttons: [
//                 {
//                     extend: 'csv',
//                     text: 'Export CSV',
//                     title: null,
//                     filename: "copo_" + String(componentMeta.tableID) + "_data"
//                 },
//             ],
//             language: {
//                 "info": "Showing _START_ to _END_ of _TOTAL_ records",
//                 "search": " ",
//                 "lengthMenu": "show _MENU_ records",
//                 select: {
//                     rows: {
//                         _: "%d records selected",
//                         0: "<span class='extra-table-info'>Click <span class='fa-stack' style='color:green; font-size:10px;'><i class='fa fa-circle fa-stack-2x'></i><i class='fa fa-plus fa-stack-1x fa-inverse'></i></span> beside a record to view extra details</span>",
//                         1: "%d record selected"
//                     }
//                 },
//                 buttons: {}
//             },
//             order: [[0, 'asc']],
//
//             fnDrawCallback: function () {
//                 refresh_accessions_tool_tips();
//                 const event = jQuery.Event("posttablerefresh"); //individual compnents can trap and handle this event as they so wish
//                 $('body').trigger(event);
//             },
//             columns: cols,
//
//             "columnDefs": [
//                 {
//                     "targets": "_all", // all fields
//                     "createdCell": function (td, cellData, rowData, row, col) {
//                         if (cellData === "") {
//                             $(td).addClass("cell-no-content")
//                         }
//                     }
//                 },
//                 // {
//                 //     'targets': [3, 5], // 'biosampleAccession' column & 'sraAccession' column respectively
//                 //     'render': function (data, type, full, meta) {
//                 //         let ebi_url = `https://www.ebi.ac.uk/ena/browser/view/${data}`
//                 //         return '<a class="no-underline" href="' + ebi_url + '"  target="_blank">' + data + '</a>';
//                 //     }
//                 // },
//                 // {
//                 //     'targets': [4], // 'manifest_id' column
//                 //     'render': function (data, type, full, meta) {
//                 //         let get_samples_by_manifestID_url = `/api/manifest/${data}`
//                 //         return '<a class="no-underline" href="' + get_samples_by_manifestID_url + '"  target="_blank">' + data + '</a>';
//                 //     }
//                 // }
//             ],
//
//             createdRow: function (row, data, rowIndex) {
//                 //add class to row for ease of selection later
//                 // let recordId = index;
//                 // Iterate over the sample record IDs and add them to the row as a class
//                 $.each(recordIDs, function (recordIndex, recordID) {
//                     try {
//                         if (rowIndex === recordIndex) {
//                             $(row).attr("id", recordID)
//                             $(row).addClass("accessions_row");
//                             $(row).addClass(componentMeta.tableID + recordID);
//                         }
//                     } catch (err) {
//                         console.log(`Error: ${err}`)
//                     }
//                 });
//                 // Iterate over the sample types and add them as an attribute to each row   in the table              $.each(sample_types, function (index, type) {
//                 let filterAccessionsTypes = []
//                 $.each(accession_types, function (sampleIndex, sample_type) {
//                     try {
//                         if (rowIndex === sampleIndex) $(row).attr("accession_type", sample_type)
//                     } catch (err) {
//                         console.log(`Error: ${err}`)
//                     }
//                 });
//             },
//
//             dom: 'Bfr<"row"><"row info-rw" i>tlp'
//         });
//
//         table
//             .buttons()
//             .nodes()
//             .each(function (value) {
//                 $(this)
//                     .removeClass("btn btn-default")
//                     .addClass('tiny ui basic button');
//             });
//
//         // place_accessions_task_buttons(componentMeta);
//     } else {
//         // table = $(tableID).DataTable({
//         //     data: dataSet,
//         //     select: false,
//         //     searchHighlight: true,
//         //     ordering: true,
//         //     lengthChange: true,
//         //     scrollX: true,
//         //     scrollY: 350,
//         //     buttons: [
//         //         {
//         //             extend: 'csv',
//         //             text: 'Export CSV',
//         //             title: null,
//         //             filename: "copo_" + String(componentMeta.tableID) + "_data"
//         //         },
//         //     ],
//         //     language: {
//         //         "info": "Showing _START_ to _END_ of _TOTAL_ records",
//         //         "search": " ",
//         //         "lengthMenu": "show _MENU_ records",
//         //         select: {
//         //             rows: {
//         //                 _: "%d records selected",
//         //                 0: "<span class='extra-table-info'>Click <span class='fa-stack' style='color:green; font-size:10px;'><i class='fa fa-circle fa-stack-2x'></i><i class='fa fa-plus fa-stack-1x fa-inverse'></i></span> beside a record to view extra details</span>",
//         //                 1: "%d record selected"
//         //             }
//         //         },
//         //         buttons: {}
//         //     },
//         //     order: [[0, 'asc']],
//         //
//         //     fnDrawCallback: function () {
//         //         refresh_accessions_tool_tips();
//         //         const event = jQuery.Event("posttablerefresh"); //individual compnents can trap and handle this event as they so wish
//         //         $('body').trigger(event);
//         //     },
//         //     columns: cols,
//         //
//         //     "columnDefs": [
//         //         {
//         //             "targets": "_all", // all fields
//         //             "createdCell": function (td, cellData, rowData, row, col) {
//         //                 if (cellData === "") {
//         //                     $(td).addClass("cell-no-content")
//         //                 }
//         //             }
//         //         },
//         //         {
//         //             'targets': [3, 5], // 'biosampleAccession' column & 'sraAccession' column respectively
//         //             'render': function (data, type, full, meta) {
//         //                 let ebi_url = `https://www.ebi.ac.uk/ena/browser/view/${data}`
//         //                 return '<a class="no-underline" href="' + ebi_url + '"  target="_blank">' + data + '</a>';
//         //             }
//         //         },
//         //         {
//         //             'targets': [4], // 'manifest_id' column
//         //             'render': function (data, type, full, meta) {
//         //                 let get_samples_by_manifestID_url = `/api/manifest/${data}`
//         //                 return '<a class="no-underline" href="' + get_samples_by_manifestID_url + '"  target="_blank">' + data + '</a>';
//         //             }
//         //         }
//         //     ],
//         //
//         //     createdRow: function (row, data, rowIndex) {
//         //         //add class to row for ease of selection later
//         //         // let recordId = index;
//         //         // Iterate over the sample record IDs and add them to the row as a class
//         //         $.each(recordIDs, function (recordIndex, recordID) {
//         //             try {
//         //                 if (rowIndex === recordIndex) {
//         //                     $(row).attr("id", recordID)
//         //                     $(row).addClass("accessions_row");
//         //                     $(row).addClass(componentMeta.tableID + recordID);
//         //                 }
//         //             } catch (err) {
//         //                 console.log(`Error: ${err}`)
//         //             }
//         //         });
//         //         // Iterate over the sample types and add them as an attribute to each row   in the table              $.each(sample_types, function (index, type) {
//         //         let filterAccessionsTypes = []
//         //         $.each(accession_types, function (sampleIndex, sample_type) {
//         //             try {
//         //                 if (rowIndex === sampleIndex) $(row).attr("accession_type", sample_type)
//         //             } catch (err) {
//         //                 console.log(`Error: ${err}`)
//         //             }
//         //         });
//         //     },
//         //
//         //     dom: 'Bfr<"row"><"row info-rw" i>tlp'
//         // });
//         //
//         // table
//         //     .buttons()
//         //     .nodes()
//         //     .each(function (value) {
//         //         $(this)
//         //             .removeClass("btn btn-default")
//         //             .addClass('tiny ui basic button');
//         //     });
//         //
//         // place_accessions_task_buttons(componentMeta);
//     }
//     let table_wrapper = $(tableID + '_wrapper')
//
//     table_wrapper
//         .find(".dataTables_filter")
//         .find("label").css({"padding": "20px 0 20px 0", "margin-top": "10px"})
//         .find("input")
//         .removeClass("input-sm")
//         .attr("placeholder", "Search " + componentMeta.title)
//         .attr("size", 30);
//
//     // Add css to align the buttons to the right
//     table_wrapper.find(".dt-buttons").addClass("pull-right")
//     table_wrapper.find('.info-rw').hide() // Hide showing 'x' of 'x' row
//
//     // Insert breakpoints after the toggle button
//     if (table_wrapper.find("br").length === 0) {
//         $("<br><br>").insertAfter(table_wrapper.find(".dt-buttons"))
//     }
//
//     // Set height of table to fit the content in the table
//     table_wrapper.find(".dataTables_scrollBody").css("height", "fit-content")
//
//     // Add padding between table and show records filter
//     table_wrapper.find(".dataTables_length").css("padding-top", "20px")
// } //end of func

function render_accessions_table(data, cols, dataSet, recordIDs, accession_types, componentMeta) {
    const tableID = `#${componentMeta.tableID}`;
    //set data
    let table = null;

    if ($.fn.dataTable.isDataTable(tableID)) {
        //if table instance already exists, then do refresh
        table = $(tableID).DataTable()
    }
    // if ($(document).data("isSampleProfileTypeStandalone")) {
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

    if (table) {
        console.log("JS: I am here 1")
        console.log("cols 2", cols)
        console.log("dataSet 2", dataSet)
        console.log("recordIDs 2", recordIDs)

        // Get the column API object
        let column3 = table.column(3)
        let column4 = table.column(4)
        let column5 = table.column(5)
        let column6 = table.column(6)

        // Toggle visibility of the columns
        column3.visible(!column3.visible());
        column4.visible(!column4.visible());
        column5.visible(!column5.visible());
        column6.visible(!column6.visible());


        // Set column names
        $.each(cols, function (index, item) {
            $(table.column(index).header()).text(item.title);
            $(table.column(index).header()).val(item.value);
        });

        //clear old, set new data
        table.rows().deselect();
        table
            .clear()
            .draw();
        table
            .rows
            .add(dataSet);
        table
            .columns
            .adjust()
            .draw();
        table
            .search('')
            .columns()
            .search('')
            .draw();
        //

        let dt_options;
        if ($(document).data("isSampleProfileTypeStandalone")) {
            console.log('Table rows', table.rows())
            console.log('Table rows type', typeof table.rows())
            table.rows().every(function (rowIdx, tableLoop, rowLoop) {
                var data = this.data();
                let row = table.row(this.closest("tr")[rowIdx])
                console.log('row data', data)
                console.log('tableLoop', tableLoop)
                console.log('rowLoop', rowLoop)
                $(row).attr("id", 'hiID')
                // ... do something with data(), or this.node(), etc
            });
            // dt_options = {
            //     order: [[2, 'asc']],
            //     createdRow: function (row, data, rowIndex) {
            //         //add class to row for ease of selection later
            //         // let recordId = index;
            //         // Iterate over the sample record IDs and add them to the row as a class
            //
            //         console.log("recordIDs 4", recordIDs)
            //         recordIDs.map(function (item) {
            //             console.log("recordID", item.recordID)
            //             console.log("profile_id", item.profile_id)
            //         });
            //     }
            // }
            //
            // $(tableID).DataTable(dt_options);
        } else {

        }
        table.draw();

    } else {
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
            order: [[0, 'asc']],
            fnDrawCallback: function () {
                refresh_accessions_tool_tips();
                const event = jQuery.Event("posttablerefresh"); //individual compnents can trap and handle this event as they so wish
                $('body').trigger(event);
            },
            columns: cols,
            "columnDefs": columnDefinition,
            createdRow: function (row, data, rowIndex) {
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
                // Iterate over the sample types and add them as an attribute to each row   in the table              $.each(sample_types, function (index, type) {
                let filterAccessionsTypes = []
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

        table
            .buttons()
            .nodes()
            .each(function (value) {
                $(this)
                    .removeClass("btn btn-default")
                    .addClass('tiny ui basic button');
            });

        place_accessions_task_buttons(componentMeta);
    }

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
    if (table_wrapper.find("br").length === 0) {
        $("<br><br>").insertAfter(table_wrapper.find(".dt-buttons"))
    }

    // Set height of table to fit the content in the table
    table_wrapper.find(".dataTables_scrollBody").css("height", "fit-content")

    // Add padding between table and show records filter
    table_wrapper.find(".dataTables_length").css("padding-top", "20px")
} //end of func

function set_filter_checkboxes(accession_types) {
    let accessions_checkboxes = $('.accessions-checkboxes')
    let accession_types_unique = [...new Set(accession_types)]; // Remove duplicates from sample types array

    // Clear accessions checkboxes div if data exists within it
    if (accessions_checkboxes.length) accessions_checkboxes.empty()

    $.each(accession_types_unique, function (index, type) {
        let label = $(document).data("isSampleProfileTypeStandalone")
            ? convertStringToTitleCase(pluraliseString(type))
            : type

        let $filterCheckBoxItem = '<div class="form-check">'
        $filterCheckBoxItem += '<input id="' + type + '" ' +
            'class="filter-accessions form-check-input" ' +
            'type="checkbox" name="accessionsTypes[]" value="' + type + '"/>'
        $filterCheckBoxItem += '<label class="form-check-label" style="padding-left: 5px" for="' + type + '">'
        $filterCheckBoxItem += label
        $filterCheckBoxItem += '</label>'
        $filterCheckBoxItem += '</div>'
        $filterCheckBoxItem += '<br/>'

        // Check "Projects" checkbox by default in Stand-alone project accession filter checkboxes
        if ($(document).data("isSampleProfileTypeStandalone") && type === "project" && index === 0) {
            $filterCheckBoxItem = $filterCheckBoxItem.replace('type="checkbox"', 'type="checkbox" checked')
        }

        // Populate the accessions checkboxes div with the accession types checkboxes
        $(".accessions-legend").find('.accessions-checkboxes').append($filterCheckBoxItem)
    });
}

function load_accessions_records(componentMeta, copoVisualsURL) {
    const component_table_loder = $("#component_table_loader")
    const csrftoken = $.cookie('csrftoken');

    //loader
    let tableLoader = null;

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
            "isSampleProfileTypeStandalone": $(document).data("isSampleProfileTypeStandalone"),
            "isUserProfileActive": false,

        },
        dataType: "json",
        success: function (data) {
            let accessions_checkboxes = $('.accessions-checkboxes')
            if (data.length === 0) {
                if (accessions_checkboxes.length) accessions_checkboxes.empty()
                if (tableLoader) tableLoader.remove(); //remove loader
                return false;
            } else {
                if ($(document).data("isSampleProfileTypeStandalone")) {
                    // Get Stand-alone projects data
                    let column_names = ["Accession", "Alias", "Profile Title"]
                    let cols = [];
                    let accession_types = []
                    let recordIDs = []
                    let profileIDs = []

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
                            // profileIDs.push(data[index].profile_id)
                            obj.profileID = data[index].profile_id
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
                                    // console.log("i", i)
                                    // dataSet.push(Object.values(item))
                                });

                                // Append profile title to the end of the array
                                values_array.push(data[index].profile_title)
                                // let key_name = `${type}`
                                // let dataSet_array = {key_name: dataSet}
                                data_array[type] = values_array

                            });


                            console.log('Accessions:', data[index].accessions)
                            console.log("data_array", data_array)
                            $(document).data("standaloneAccessionsData", data_array)

                            delete data[index].accessions;
                        }


                    });

                    // console.log("profile IDs length", profileIDs)

                    // Add filter checkbox to under info panel to right side of screen
                    set_filter_checkboxes(accession_types)

                    // Get element keys
                    column_names.forEach(item => {

                        cols.push({title: item, value: item.toLowerCase().replace(/ /g, "_")})
                    });
                    console.log("cols", cols)

                    // Get data values based on checked accession types
                    const selectedAccessions = getValues($(".filter-accessions:checked"));
                    console.log("selectedAccessions 1", selectedAccessions)
                    let dataSet = []
                    selectedAccessions.forEach(item => {
                        dataSet.push($(document).data("standaloneAccessionsData")[item])
                    });
                    console.log("dataSet", dataSet)


                    // Render table
                    //render_standalone_accessions_table(data, cols, [dataSet], recordIDs, accession_types, componentMeta);
                    render_accessions_table(data, cols, dataSet, recordIDs, accession_types, componentMeta);

                    if (tableLoader) tableLoader.remove(); //remove loader
                } else {
                    // Get other projects' data
                    let dataSet = []
                    let cols = [];
                    let accession_types = []
                    let sampleIDs = []


                    $.each(data, function (index, item) {
                        // Remove sample ID & project type from key-value pair from the original object
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

            }


        },
        error: function () {
            alert("Couldn't retrieve " + componentMeta.component + " data!");
        }
    });
}

function refresh_accessions_tool_tips() {
    $("[data-toggle='tooltip']").tooltip();
    $("[data-toggle='popover']").popover();
    $('.ui.dropdown')
        .dropdown()
    ;
    $('.copo-tooltip')
        .popup()
    ;
} //end of func

function toggle_accessions_view() {
    const component = "accessions";
    const componentMeta = get_component_meta(component);
    const copoVisualsURL = "/copo/copo_accessions_visualise/";

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

    if ($(this).find('.active').text().includes("Stand-alone Projects'")) {
        $(document).data("isSampleProfileTypeStandalone", true)
        load_accessions_records(componentMeta, copoVisualsURL)
    } else {
        $(document).data("isSampleProfileTypeStandalone", false)
        load_accessions_records(componentMeta, copoVisualsURL)
    }
}

//builds component-page navbar
function do_page_controls(componentName) {
    let component = null;
    const components = get_copo_accessions_components();

    components.forEach(function (comp) {
        if (comp.component === componentName) {
            component = comp;
            return false;
        }
    });

    if (component == null) {
        return false;
    }

    generate_component_control(component);

} //end of func

function generate_component_control(component) {
    const pageHeaders = $(".copo-page-headers"); //page header/icons
    const pageIcons = $(".copo-page-icons"); //profile component icons
    const sideBar = $(".copo-sidebar"); //sidebar panels
    let profileTitleID = $("#profile_title") // profile title ID

    //add profile title
    if (profileTitleID.length) {
        const profileTitle = $('<div/>', {
            class: "page-title-custom",
            style: "margin-right:10px;",
            html: "<span title='Profile title' style='color: #8c8c8c; font-size: 18px;'>Profile: " + profileTitleID.val() + "</span>"
        });

        pageHeaders.append(profileTitle);
    }

    //add page title
    const PageTitle = $('<span/>', {
        class: "page-title-custom",
        style: "margin-right:10px;",
        html: component.title
    });

    pageHeaders.append(PageTitle);


    //create panels
    if (component.sidebarPanels) {
        const sidebarTemplate = $(".copo-sidebar-templates")
        const sidebarPanels = sidebarTemplate.clone();
        const sidebarPanels2 = sidebarPanels.clone();
        sidebarPanels.find(".nav-tabs").html('');
        sidebarPanels.find(".tab-content").html('');
        sidebarTemplate.remove();


        component.sidebarPanels.forEach(function (item) {
            sidebarPanels.find(".nav-tabs").append(sidebarPanels2.find(".nav-tabs").find("." + item));
            sidebarPanels.find(".tab-content").append(sidebarPanels2.find(".tab-content").find("." + item));
            sidebarPanels.find(".accessions-legend").append(sidebarPanels2.find(".accessions-legend").find("." + item));
        });

        sideBar
            .append(sidebarPanels.find(".nav-tabs"))
            .append(sidebarPanels.find(".tab-content"))
            .append(sidebarPanels.find(".accessions-legend"));


    }

    //create buttons
    const buttonsSpan = $('<span/>', {style: "white-space:nowrap;"});
    pageHeaders.append(buttonsSpan);
    component.buttons.forEach(function (item) {
        if (component.buttons) {
            component.buttons.forEach(function (item) {
                buttonsSpan.append($("." + item)).append("<span style='display: inline;'>&nbsp;</span>");
            });
        }
    });

    //...and profile component buttons
    if (component.hasOwnProperty("profile_component") && component.profile_component.toString() === "true") {
        const pcomponentHTML = $(".pcomponents-icons-templates").clone().removeClass("pcomponents-icons-templates");
        const pcomponentAnchor = pcomponentHTML.find(".pcomponents-anchor").clone().removeClass("pcomponents-anchor");
        pcomponentHTML.find(".pcomponents-anchor").remove();

        pageIcons.append(pcomponentHTML);

        const components = get_copo_accessions_components();

        for (let i = 1; i < components.length; ++i) {
            const comp = components[i];
            if (comp.hasOwnProperty("profile_component") && comp.profile_component.toString() === "true") {

                if ((comp.component === component.component)) {
                    continue;
                }

                const newAnchor = pcomponentAnchor.clone();
                pcomponentHTML.append(newAnchor);

                newAnchor.attr("title", "Navigate to " + comp.title);
                newAnchor.attr("href", $("#" + comp.component + "_url").val());
                newAnchor.find("i")
                    .addClass(comp.color)
                    .addClass(comp.semanticIcon);

            }
        }
    }

    //refresh components...
    // quick_tour_event();
    refresh_accessions_tool_tips();
}

//#------------- Helpers -----------------#
function convertStringToTitleCase(str) {
    // Given a string, convert it to title case/ sentence case
    return str.replace(
        /\w\S*/g,
        function (txt) {
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        }
    ).replace("_id", " ID")
        .replace("_name", " Name")
        .replace("accession", " Accession")
        .replace("Sra", "SRA")
        .replace("seq_a", "Sequence A")
}

function pluraliseString(str) {
    // Pluralise a word based on the passed value
    const pluralise = (val, word, plural = word + 's') => {
        const _pluralise = (num, word, plural = word + 's') =>
            [1, -1].includes(Number(num)) ? word : plural;
        if (typeof val === 'object') return (num, word) => _pluralise(num, word, val[word]);
        return _pluralise(val, word, plural);
    };

    // Plural form of special words
    const PLURALS = {
        assembly: 'assemblies'
    };
    const autoPluralise = pluralise(PLURALS);

    return str === "assembly" ? autoPluralise(2, str) : pluralise(2, str)


}
