$(document).ready(function () {
    const acceptRejectSampleURL = "/copo/accept_reject_sample"
    const accessionsDashboardURL = "/copo/dashboard/accessions"
    const tolInspectURL = "/copo/tol_inspect"
    const tolInspectByGALURL = "/copo/tol_inspect/gal/"
    
    // Store 'showAllCOPOAccessions' value
    $("#showAllCOPOAccessions").val() == 'True' 
    ? $(document).data("showAllCOPOAccessions", true)
    : $(document).data("showAllCOPOAccessions", false)

    if ($(document).data("showAllCOPOAccessions")){
        // Stored data for accessions dashboard
        $(document).data("isSampleProfileTypeStandalone", false)
        $(document).data("isUserProfileActive", false)
    }else{
        // Stored data for accessions web page for a given profile
        $(document).data("isUserProfileActive", true)
        
    }
    
    $(document).on("click", ".accept_reject_samples", function () {
        document.location = acceptRejectSampleURL
    })

    $(document).on("click", ".tol_inspect", function () {
        document.location = tolInspectURL
    })

    $(document).on("click", ".tol_inspect_gal", function () {
        document.location = tolInspectByGALURL
    })

    $(document).on("click", ".copo_accessions", function () {
        document.location = accessionsDashboardURL
    })

    $(document).on("click", ".toggle-view", toggle_accessions_view)

    $(document).on("change", ".filter-accessions", filterDataByAccessionType)    

    //trigger refresh of table
    $('body').on('refreshtable', function (event) {
        render_accessions_table(globalDataBuffer);
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
    // Not accessions dashboard: Instantiate based on profile type
    if (!$(document).data("showAllCOPOAccessions")){
        let profile_type = $("#profile_type").val()
    
        profile_type.includes("Stand-alone")
        ?  $(document).data("isSampleProfileTypeStandalone", true)
        : $(document).data("isSampleProfileTypeStandalone", false)
    }

    // Load records
    load_accessions_records();

    // Instantiate/refresh tooltips
    refresh_tool_tips();
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
    const componentMeta = get_component_meta($("#nav_component_name").val());
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

function get_filter_accession_titles(accession_types) {
    $.ajax({
        url: '/copo/get_filter_accession_titles/',
        method: "POST",
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        dataType: "json",
        data: {
            "isSampleProfileTypeStandalone": $(document).data("isSampleProfileTypeStandalone"),
            "accession_types": JSON.stringify(accession_types)
        },
        success: function (data) {
            if (data.length === 0) {
                return false;
            } else {
                set_filter_checkboxes(data)
            }
        },
        error: function (error) {
            console.log(`Error: ${error.message}`);
        }
    });
}

function set_filter_checkboxes(accession_titles) {
    let accessions_checkboxes = $('.accessions-checkboxes')

    // Clear accessions checkboxes div if data exists within it
    if (accessions_checkboxes.length) accessions_checkboxes.empty()
    
    $.each(accession_titles, function( index, item ) {
        let label = $(document).data("isSampleProfileTypeStandalone") ? item.title : item.value

        let $filterCheckBoxItem = '<div class="form-check">'
        $filterCheckBoxItem += '<input id="' + item.value + '" ' +
            'class="filter-accessions form-check-input" ' +
            'type="checkbox" value="' + item.value + '"/>'
        $filterCheckBoxItem += '<label class="form-check-label" style="padding-left: 5px" for="' + item.value + '">'
        $filterCheckBoxItem += label
        $filterCheckBoxItem += '<i class="fa fa-info-circle accession_type_info_icon" title="' + item.title + '"> </i>'
        $filterCheckBoxItem += '</label>'
        $filterCheckBoxItem += '</div>'
        $filterCheckBoxItem += '<br/>'

        // Check "Projects" checkbox by default in Stand-alone project accession filter checkboxes
        if ($(document).data("isSampleProfileTypeStandalone") && item.value === "project") {
            $filterCheckBoxItem = $filterCheckBoxItem.replace('type="checkbox"', 'type="checkbox" checked')
        }
        // Check all checkboxes by default in "Other Projects'" project accessions
        if (!$(document).data("isSampleProfileTypeStandalone")) {
            $filterCheckBoxItem = $filterCheckBoxItem.replace('type="checkbox"', 'type="checkbox" checked')
        }

        // Populate the accessions checkboxes div with the accession types checkboxes
        $(".accessions-legend").find('.accessions-checkboxes').append($filterCheckBoxItem)
        if ($(document).data("isSampleProfileTypeStandalone")) {
            $('.filter-accessions:checkbox:first').click()
        }
    });
}

function place_accessions_task_buttons(componentMeta) {
    //place custom buttons on table
    if (!componentMeta.recordActions.length) {
        return;
    }

    var table = $('#' + componentMeta.tableID).DataTable();

    var customButtons = $('<span/>', {
        style: "padding-left: 15px;",
        class: "copo-table-cbuttons"
    });

    $(table.buttons().container()).append(customButtons);


    componentMeta.recordActions.forEach(function (item) {
        var actionBTN = $(".record-action-templates").find("." + item).clone();
        actionBTN.removeClass(item);
        actionBTN.attr("data-table", componentMeta.tableID);
        customButtons.append(actionBTN);
    });

    refresh_tool_tips();
}

function render_accessions_table(data) {
    const componentMeta = get_component_meta($("#nav_component_name").val());
    const tableID = `#${componentMeta.tableID}`;
    let table = null;
    let dataSet = data.table_data.dataSet;
    let cols = data.table_data.columns;

    // if table instance already exists then, clear, destroy and empty the table
    if ($.fn.dataTable.isDataTable(tableID)) {
        $(tableID).DataTable().clear().destroy()
        $(tableID + " tbody").empty();
        $(tableID + " thead").empty();

        // Set toggle button on accessions' dashboard only
        if($(document).data("showAllCOPOAccessions")) set_toggle_button()

        // table = $(tableID).DataTable();
    }

    let order = $(document).data("isSampleProfileTypeStandalone") ? [[4, 'asc']] : [[3, 'asc']];

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
                'targets': [4], // 'accession' column
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
                'targets': [3, 4], // 'biosampleAccession' column & 'sraAccession' column respectively
                'render': function (data, type, full, meta) {
                    let ebi_url = `https://www.ebi.ac.uk/ena/browser/view/${data}`
                    return '<a class="no-underline" href="' + ebi_url + '"  target="_blank">' + data + '</a>';
                }
            },
            {
                'targets': [6], // 'manifest_id' column
                'render': function (data, type, full, meta) {
                    let get_samples_by_manifestID_url = `/api/manifest/${data}`
                    return '<a class="no-underline" href="' + get_samples_by_manifestID_url + '"  target="_blank">' + data + '</a>';
                }
            }
        ]

    // if (table) {
    //     //clear old, set new data
    //     table.rows().deselect();
    //     table
    //         .clear()
    //         .draw();
    //     table
    //         .rows
    //         .add(dataSet);
    //     table
    //         .columns
    //         .adjust()
    //         .draw();
    //     table
    //         .search('')
    //         .columns()
    //         .search('')
    //         .draw(); 
    // } else {
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
    language: {},
    order: order,
    fnDrawCallback: function () {
        refresh_tool_tips();
        const event = jQuery.Event("posttablerefresh"); // individual compnents can trap and handle this event as they so wish
        $('body').trigger(event);

    },
    columns: cols,
    "columnDefs": columnDefinition,
    createdRow: function (row, data, index) {
        // Add the record ID and accesstion type to each row
        let recordID = index;

        try {
            recordID = data.record_id;
            accessionType = data.accession_type;

            if ($(document).data("isSampleProfileTypeStandalone")) {
                profile_id = data.profile_id;
            }
        } catch (error) {
            console.log(`Error: ${error.message}`)
        }

        $(row).addClass(componentMeta.tableID + recordID);
        $(row).addClass("accessions_row");
        $(row).attr("id", recordID)
        $(row).attr("accession_type", accessionType)

        if ($(document).data("isSampleProfileTypeStandalone")) {
            // Set the profile ID as an attribute of the last cell in the row
            $(row).find('td:last-child').attr("data-profile_id", profile_id)
        }

        //individual compnents can trap and handle this event as they so wish
        let event = jQuery.Event("postcreatedrow", row = row, data = data, index = index);
        $('body').trigger(event);        
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
    
    // Show task buttons for accessions' dashboard only
    if($(document).data("showAllCOPOAccessions")) place_accessions_task_buttons(componentMeta);
    // }

    // Get accession types
    let accession_types = []

    table.column(2).data().unique().sort().each( function ( value, key ) {
        accession_types.push(value)
    }); 

    // Add filter checkbox to under info panel to right side of screen on accessions' dashboard only
    if ($(document).data("showAllCOPOAccessions")) get_filter_accession_titles(accession_types)

    // Filter the rows that are not associated with the current checked "Standalone" accession type
    if ($(document).data("isSampleProfileTypeStandalone")) {
        // Click first accession type shown in the 'filter accessions'' legend
        $('.filter-accessions:checkbox:first:visible').click()
        filterDataByAccessionType()
    }

    // Show accessions legend if it was hidden and if table has data
    if (table.data().any()){
        $('.accessions-legend').show() 
        $('.accessions-checkboxes').show()  // Show the filter accessions' legend
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

function load_accessions_records() {
    const componentMeta = get_component_meta($("#nav_component_name").val());
    const component_table_loder = $("#component_table_loader")
    const csrftoken = $.cookie('csrftoken');
    
    let post_data = {}
    let tableLoader = null; //loader
    let accessions_checkboxes = $('.accessions-checkboxes')

    post_data['isUserProfileActive'] = $(document).data("isUserProfileActive") 
    post_data['isSampleProfileTypeStandalone'] = $(document).data("isSampleProfileTypeStandalone")
    post_data['task'] = 'table_data';
    post_data["quick_tour_flag"] = false
    post_data['component'] = componentMeta.component;

    if (component_table_loder.length) {
        tableLoader = $('<div class="copo-i-loader"></div>');
        component_table_loder.append(tableLoader);
    }

    // URL for accessions dashboard where the view for it does not require user to be logged in
    let url = '/copo/copo_visualize_accessions_dashboard/'
    
    $.ajax({
        url: $(document).data("showAllCOPOAccessions") ? url : copoVisualsURL,
        type: "POST",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: post_data,
        dataType: "json",
        success: function (data) {
            if (data.hasOwnProperty ("table_data") &&  data.table_data.dataSet.length == 0) {
                if($(document).data("showAllCOPOAccessions") && $(document).data("isSampleProfileTypeStandalone")){ 
                    // Show empty table
                    render_accessions_table(data)
                    
                    // Hide accessions legend if table is empty
                    if (!$(`#${componentMeta.tableID}`).DataTable().data().any()){
                        // if (accessions_checkboxes.find('.form-check').length) 
                        accessions_checkboxes.empty()
                        $('.accessions-legend').hide()  // Hide the filter accessions' legend
                    }
                }else if($(document).data("showAllCOPOAccessions") && !$(document).data("isSampleProfileTypeStandalone")){
                     // Show empty table
                    render_accessions_table(data)
                  
                    // Hide accessions legend if table is empty
                    if (!$(`#${componentMeta.tableID}`).DataTable().data().any()){
                        // if (accessions_checkboxes.find('.form-check').length) 
                        accessions_checkboxes.empty()
                        $('.accessions-legend').hide()  // Hide the filter accessions' legend
                    }
                } else{
                    // Show empty component message for 'Other projects' accessions'
                    set_empty_component_message(data.table_data.dataSet.length); //display empty component message when there's no record
                    // if (accessions_checkboxes.find('.form-check').length) 
                    accessions_checkboxes.empty()
                    $('.accessions-legend').hide()  // Hide the filter accessions' legend
                }
               

                if(!$(document).data("showAllCOPOAccessions")) $(".copo_accessions").show() // Show the accessions' button on accessions web page for a given profile
                if (tableLoader) tableLoader.remove(); //remove loader
                return false;
            }else{
                render_accessions_table(data)
                if (tableLoader) tableLoader.remove(); //remove loader

                 // Remove items
                if ($(document).data("showAllCOPOAccessions")){
                    // On accessions dashboard
                    $(".copo_accessions").hide()
                }else{
                    // On accessions web page for a given profile
                    $(".copo_accessions").show()
                    $('.copo-page-icons').show()
                    $('.accessions-legend').hide()
                    $('.toggle-view').hide()
                }
            }
        },
        error: function () {
            alert("Couldn't retrieve " + componentMeta.component + " data!");
        }
    });
}

function toggle_accessions_view() {
    $(this).find('.btn').toggleClass('active');

    if ($(this).find('.btn-success').size() > 0) {
        $(this).find('.btn').toggleClass('btn-success');
    }

    $(this).find('.btn').toggleClass('btn-default');

    if ($(this).find('.active').text().includes("Stand-alone")) {
        $(document).data("isSampleProfileTypeStandalone", true)
        load_accessions_records()
    } else {
        $(document).data("isSampleProfileTypeStandalone", false)
        load_accessions_records()
    }
} // End of func

function set_toggle_button(){
    $('.toggle-view').find('.btn').toggleClass('active');
    $('.toggle-view').find('.btn').toggleClass('btn-success');
    $('.toggle-view').find('.btn').toggleClass('btn-default');
}