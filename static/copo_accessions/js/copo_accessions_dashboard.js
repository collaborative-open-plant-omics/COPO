$(document).ready(function () {
    const acceptRejectSampleURL = "/copo/accept_reject_sample"
    const tolInspectURL = "/copo/tol_inspect"
    const tolInspectByGALURL = "/copo/tol_inspect/gal/"
    const component = "accessions";
    const copoVisualsURL = "/copo/copo_accessions_visualise/";
    const componentMeta = get_accession_component_meta(component);
    const componentName = $("#nav_component_name").val();

    $(document).data("isSampleProfileTypeStandalone", false)
    $(document).data("isUserProfileActive", false)

    $(document).on("click", ".accept_reject_samples", function () {
        document.location = acceptRejectSampleURL
    })

    $(document).on("click", ".tol_inspect", function () {
        document.location = tolInspectURL
    })

    $(document).on("click", ".tol_inspect_gal", function () {
        document.location = tolInspectByGALURL
    })

    $(document).on("click", ".btn-toggle2", toggle_accessions_view)

    $(document).on("change", ".filter-accessions", filterDataByAccessionType)

    //trigger refresh of table
    $('body').on('refreshtable', function (event) {
        render_accessions_table(globalDataBuffer, componentMeta);
    });

    if (groups.includes("dtol_sample_managers") || groups.includes("erga_sample_managers")
        || groups.includes("dtolenv_sample_managers")) {
        $(".accept_reject_samples").show() // Show 'accept/reject samples' button
    }

    if (groups.includes("dtol_users") || groups.includes("dtol_sample_managers") || groups.includes("erga_users")
        || groups.includes("erga_sample_managers") || groups.includes("dtolenv_sample_managers")) {
        $(".tol_inspect").show() // Show 'tol_inspect' button
        $(".tol_inspect_gal").show() // Show 'tol_inspect_gal' button
    }

    // Hide buttons if user does not belon to a group
    if (groups.length === 0) {
        $(".tol_inspect").hide() // Hide 'tol_inspect' button
        $(".tol_inspect_gal").hide() // Hide 'tol_inspect_gal' button
    }

    // Set up global navigation components
    do_accession_page_controls(componentName);

    // Load records
    load_accessions_records(componentMeta, copoVisualsURL);

    // Instantiate/refresh tooltips
    refresh_accessions_tool_tips();
}); //End document ready

//______________Handlers___________________________________

// Filter accessions table by accession type
const getValues = function ($el) {
    let items = [];
    $el.each(function () {
        items.push($(this).val());
    });

    return items;
};

const filterDataByAccessionType = function () {
    const component = "accessions";
    const componentMeta = get_accession_component_meta(component);
    let tableID = `#${componentMeta.tableID}`
    let table = $(tableID).DataTable()

    $.fn.dataTable.ext.search.push(
        function (settings, data, dataIndex) {
            let checkedAccessions = getValues($(".filter-accessions:checked:visible"));
            let uncheckedboxes = $(".filter-accessions:not(:checked):visible")
            let uncheckedAccessions = getValues(uncheckedboxes)

            if (settings.nTable.id === componentMeta.tableID) {
                let row_accession_type = table
                    .row(dataIndex)         // get the row to evaluate
                    .nodes()                // extract the HTML - node() does not support to$
                    .to$()                  // get rows as jQuery object
                    .attr('accession_type'); //get the value of 'accession_type' attribute

                if (uncheckedboxes.length === $('.filter-accessions').length) {
                    // If length of all unchecked accession types is equal to the number of accession checkboxes
                    // in the filter accession type div then, show all table rows
                    return true;
                } else if (checkedAccessions.length > 0) {
                    // Show each row based on the accession type that is checked
                    return checkedAccessions.includes(row_accession_type);
                } else {
                    // Reset display
                    // Show each row based on the accession type that is unchecked
                    return uncheckedAccessions.includes(row_accession_type);
                }
            }
        }
    );
    table.draw(); // Redraw the table
    $.fn.dataTable.ext.search.pop();
};

// Accessions component
function get_accession_component_meta(component) {
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
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-profiles-legend"],
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
            buttons: ["quick-tour-template", "new-samples-template", "new-samples-spreadsheet-template", "new-samples-spreadsheet-template-erga", "accept_reject_samples"],
            sidebarPanels: ["copo-sidebar-info"],
            colorClass: "samples_color",
            color: "olive",
            profile_component: "dtol",
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
            buttons: ["copo_accessions", "accept_reject_samples", "tol_inspect", "tol_inspect_gal"],
            sidebarPanels: ["copo-sidebar-info"],
            colorClass: "accessions_color",
            color: "pink",
            profile_component: "dtol",
            tableID: 'accessions_table',
            recordActions: ["btn-toggle"],
            visibleColumns: 3 //no of columns to be displayed, if tabular data is required. remaining columns will be displayed in a sub-table
        },
        {
            component: 'accessions',
            title: 'Accessions',
            iconClass: "fa fa-barcode",
            semanticIcon: "barcode", //semantic UI equivalence of fontawesome icon
            countsKey: "num_accessions",
            buttons: ["copo_accessions", "accept_reject_samples", "tol_inspect", "tol_inspect_gal"],
            sidebarPanels: ["copo-sidebar-info"],
            colorClass: "accessions_color",
            color: "pink",
            profile_component: "stand-alone",
            tableID: 'accessions_table',
            recordActions: ["btn-toggle"],
            visibleColumns: 3 //no of columns to be displayed, if tabular data is required. remaining columns will be displayed in a sub-table
        },
        {
            component: 'read',
            title: 'Reads',
            iconClass: "fa fa-filter",
            semanticIcon: "filter", //semantic UI equivalence of fontawesome icon
            countsKey: "num_read",
            buttons: ["new-reads-spreadsheet-template", "update-reads-template"],
            sidebarPanels: ["copo-sidebar-info"],
            colorClass: "samples_color",
            color: "olive",
            profile_component: "stand-alone",
            tableID: 'sample_table',
            recordActions: ["delete_read_multi", "submit_read_multi"],
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
            sidebarPanels: ["copo-sidebar-info"],
            tableID: 'datafile_table',
            //profile_component: true,
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
            sidebarPanels: ["copo-sidebar-info"],
            colorClass: "submissions_color",
            color: "green",
            tableID: 'submission_table',
            //profile_component: true,
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
            sidebarPanels: ["copo-sidebar-info"],
            colorClass: "pubs_color",
            color: "orange",
            tableID: 'publication_table',
            //profile_component: true,
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
            sidebarPanels: ["copo-sidebar-info"],
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
            sidebarPanels: ["copo-sidebar-info"],
            colorClass: "people_color",
            color: "red",
            tableID: 'person_table',
            //profile_component: true,
            recordActions: ["add_record_all", "edit_record_single"],
            visibleColumns: 5
        },
        {
            component: 'assembly',
            title: 'Assembly',
            iconClass: "fa fa-database",
            semanticIcon: "database",
            countsKey: "num_assembly",
            buttons: ["quick-tour-template", "new-component-template"],
            sidebarPanels: ["copo-sidebar-info"],
            colorClass: "assembly_color",
            color: "violet",
            tableID: 'assembly_table',
            profile_component: "stand-alone",
            recordActions: ["add_record_all"],   // "delete_record_multi, submit_assembly_multi, , "edit_record_single"
            visibleColumns: 5
        },
        {
            component: 'seqannotation',
            title: 'Sequence Annotations',
            iconClass: "fa fa-database",
            semanticIcon: "database",
            countsKey: "num_seqannotation",
            buttons: ["quick-tour-template", "new-component-template"],
            sidebarPanels: ["copo-sidebar-info"],
            colorClass: "data_color",
            color: "yellow",
            tableID: 'seqannotation_table',
            profile_component: "stand-alone",
            recordActions: ["add_record_all", "edit_record_single", "delete_record_multi", "submit_annotation_multi"],
            visibleColumns: 5
        },
        {
            component: 'files',
            title: 'Files',
            iconClass: "fa fa-file",
            semanticIcon: "file",
            countsKey1_deleted: "num_assembly",
            buttons: ["new-local-file", "new-terminal-file"],
            sidebarPanels: ["copo-sidebar-info"],
            colorClass: "files_color",
            color: "blue",
            tableID: 'files_table',
            profile_component: "stand-alone",
            recordActions: ["add_local_all", "add_terminal_all", "delete_record_multi"],   // "delete_record_multi, submit_assembly_multi , "edit_record_single"
            visibleColumns: 5
        }

        /*
        {
            component: 'annotation',
            title: 'Generic Annotations',
            iconClass: "fa fa-pencil",
            semanticIcon: "write",
            countsKey: "num_annotation",
            buttons: ["quick-tour-template"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-annotate"],
            colorClass: "annotations_color",
            color: "violet",
            tableID: 'annotation_table',
            recordActions: ["delete_record_multi"],
            visibleColumns: 10000
        }, TODO - these need to be reactivated in the future sometime
        {
            component: 'repository',
            title: 'Repositories',
            iconClass: "fa fa-pencil",
            semanticIcon: "write",
            countsKey: "num_annotation",
            buttons: ["quick-tour-template", "new-component-template"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help", "copo-sidebar-annotate"],
            colorClass: "annotations_color",
            color: "violet",
            tableID: 'repository_table',
            recordActions: ["delete_record_multi"],
            visibleColumns: 10000
        }*/
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
                    if (typeof cellData == 'undefined') {
                        $(td).addClass("cell-no-content")
                        $(td).text("")
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
                    if (typeof cellData == 'undefined') {
                        $(td).addClass("cell-no-content")
                        $(td).text("")
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
                recordIDs.map(function (item, recordIndex) {
                    try {
                        if (rowIndex === recordIndex) {
                            $(row).attr("id", item.recordID)
                            $(row).addClass("accessions_row");
                            $(row).addClass(componentMeta.tableID + item.recordID);
                            // Set the profile ID as an attribute of the last cell in the row
                            $(row).find('td:last-child').attr("data-profile_id", item.profile_id)
                        }
                    } catch (error) {
                        console.log(`Error: ${error.message}`)
                    }
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
                    } catch (error) {
                        console.log(`Error: ${error.message}`)
                    }
                });

            }

            // Iterate over the accession types and add them as an attribute to each row  in the table
            $.each(accession_types, function (sampleIndex, sample_type) {
                try {
                    if (rowIndex === sampleIndex) $(row).attr("accession_type", sample_type)
                } catch (error) {
                    console.log(`Error: ${error.message}`)
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
    if ($(document).data("isSampleProfileTypeStandalone")) {
        // Click first accession type shown in the 'filter accessions'' legend
        $('.filter-accessions:checkbox:first:visible').click()
        filterDataByAccessionType()
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
} //End of func

function get_filter_accession_titles(accession_types) {
    $.ajax({
        url: '/copo/get_filter_accession_titles/',
        method: "POST",
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        dataType: "json",
        data: {
            "isSampleProfileTypeStandalone": $(document).data("isSampleProfileTypeStandalone"),
        },
        success: function (filter_accession_titles) {
            if (filter_accession_titles.length === 0) {
                return false;
            } else {
                set_filter_checkboxes(accession_types, filter_accession_titles)
            }
        },
        error: function (error) {
            console.log(`Error: ${error.message}`);
        }
    });
}

function set_filter_checkboxes(accession_types, filter_accession_titles) {
    let accessions_checkboxes = $('.accessions-checkboxes')
    let accession_types_unique = [...new Set(accession_types)]; // Remove duplicates from the sample types array

    // Clear accessions checkboxes div if data exists within it
    if (accessions_checkboxes.length) accessions_checkboxes.empty()

    $.each(accession_types_unique, function (index, type) {
        let accession_type_title = filter_accession_titles.filter(function (x) {
            // Check if "type" exists in the object i.e. "type" is a key in the object
            if (x.hasOwnProperty(type)) {
                return x[type]
            }
        });

        let label = $(document).data("isSampleProfileTypeStandalone")
            ? convertStringToTitleCase(type) //convertStringToTitleCase(pluraliseString(type))
            : type

        let $filterCheckBoxItem = '<div class="form-check">'
        $filterCheckBoxItem += '<input id="' + type + '" ' +
            'class="filter-accessions form-check-input" ' +
            'type="checkbox" value="' + type + '"/>'
        $filterCheckBoxItem += '<label class="form-check-label" style="padding-left: 5px" for="' + type + '">'
        $filterCheckBoxItem += label
        $filterCheckBoxItem += '<i class="fa fa-info-circle accession_type_info_icon" title="' + accession_type_title[0][type] + '"> </i>'
        $filterCheckBoxItem += '</label>'
        $filterCheckBoxItem += '</div>'
        $filterCheckBoxItem += '<br/>'

        // Check "Projects" checkbox by default in Stand-alone project accession filter checkboxes
        if ($(document).data("isSampleProfileTypeStandalone") && type === "project" && index === 0) {
            // $filterCheckBoxItem = $filterCheckBoxItem.replace('type="checkbox"', 'type="checkbox" checked')
        }
        if (!$(document).data("isSampleProfileTypeStandalone")) {
            // Check all checkboxes by default in "Other Projects'" project accessions
            $filterCheckBoxItem = $filterCheckBoxItem.replace('type="checkbox"', 'type="checkbox" checked')
        }

        // Populate the accessions checkboxes div with the accession types checkboxes
        $(".accessions-legend").find('.accessions-checkboxes').append($filterCheckBoxItem)
        if ($(document).data("isSampleProfileTypeStandalone")) {
            $('.filter-accessions:checkbox:first').click()
        }
    });
}

function load_accessions_records(componentMeta, copoVisualsURL) {
    const component_table_loder = $("#component_table_loader")
    const csrftoken = $.cookie('csrftoken');

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
            "isSampleProfileTypeStandalone": $(document).data("isSampleProfileTypeStandalone"),
            "isUserProfileActive": $(document).data("isUserProfileActive"),
        },
        dataType: "json",
        success: function (data) {
            if (data.length === 0) {
                let accessions_checkboxes = $('.accessions-checkboxes')
                if (accessions_checkboxes.find('.form-check').length) accessions_checkboxes.empty()
                $('.accessions-legend').hide()  // Hide the filter accessions' legend
                if (tableLoader) tableLoader.remove(); //remove loader
                return false;
            } else {
                if ($(document).data("isSampleProfileTypeStandalone")) {
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
                            obj.recordID = data[index]._id.$oid
                            delete data[index]._id;
                        }
                        if (item.hasOwnProperty("profile_id")) {
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
                                if (data[index].accessions[type] != undefined) {
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
                                }    

                            });

                            // Store "Standalone" accessions data in a global variable
                            $(document).data("standaloneAccessionsData", data_array)

                            delete data[index].accessions;
                        }
                    });


                    // Add filter checkbox to under info panel to right side of screen
                    get_filter_accession_titles(accession_types)

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

                    // Add filter checkboxes under info sidebar panel to right side of web page
                    get_filter_accession_titles(accession_types)

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
} // End of function refresh_accessions_tool_tips()

function toggle_accessions_view() {
    const component = "accessions";
    const componentMeta = get_accession_component_meta(component);
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
} // End of function toggle_accessions_view()

// Builds component-page navbar
function do_accession_page_controls(componentName) {
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

    generate_accession_component_control(component);

} //End of function do_accession_page_controls(componentName)

function generate_accession_component_control(component) {
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

    // create buttons
    const buttonsSpan = $('<span/>', {style: "white-space:nowrap;"});
    pageHeaders.append(buttonsSpan);
    component.buttons.forEach(function (item) {
        if (component.buttons) {
            component.buttons.forEach(function (item) {
                buttonsSpan.append($("." + item)).append("<span style='display: inline;'>&nbsp;</span>");
            });
        }
    });

    // Create page icons/profile component buttons if (current user) profile is active
    if ($(document).data("isUserProfileActive")) {
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
    }

    //refresh components...
    refresh_accessions_tool_tips();
} //End of function generate_accession_component_control(component)

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