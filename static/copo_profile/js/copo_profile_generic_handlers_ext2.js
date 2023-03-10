//**some re-usable functions across different modules
var copoFormsURL = "/copo/copo_forms/";
var copoVisualsURL = "/copo/copo_visualize/";
var server_side_select = {}; //holds selected ids for table data - needed in server-side processing

$(document).ready(function () {

    //dismiss alert
    $(document).on("click", ".alertdismissOK", function () {
        WebuiPopovers.hideAll();
    });

});

function set_empty_component_message(dataRows, table_id = "*") {
    //decides, based on presence of record, to display table or getting started info

    if (dataRows == 0) {
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

function place_task_buttons(componentMeta) {
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

    //table action buttons
    do_table_buttons_events();
}

function do_crud_action_feedback(meta) {
    var feedbackClass;

    if (["success", "green", "positive"].indexOf(meta.status) > -1) {
        feedbackClass = "alert-success";
    } else if (["error", "red", "danger", "negative"].indexOf(meta.status) > -1) {
        feedbackClass = "alert-danger";
    } else if (["warning"].indexOf(meta.status) > -1) {
        feedbackClass = "alert-warning";
    } else {
        feedbackClass = "alert-info";
    }

    var infoPanelElement = trigger_global_notification();

    var feedback = get_alert_control();
    feedback
        .removeClass("alert-success")
        .addClass(feedbackClass)
        .addClass("page-notifications-node");

    feedback.find(".alert-message").html(meta.message);
    infoPanelElement.prepend(feedback);
}

function format_feedback_message(message, messageClass, messageTitle) {
    let feedback = '<div class="ui small ' + messageClass + ' message">\n' +
        '  <i class="close icon"></i>\n' +
        '  <div class="header">\n' +
        '    ' + messageTitle + '\n' +
        '  </div>\n' +
        '  <div class="webpop-content-div copo-alert-message" style="margin-top: 10px;">' + message + '</div>\n' +
        '</div>'

    return feedback;

}

function do_table_buttons_events() {
    //attaches events to table buttons

    $(document).on("click", ".copo-dt", function (event) {
        event.preventDefault();

        $('.copo-dt').webuiPopover('destroy');


        var elem = $(this);
        var task = elem.attr('data-action').toLowerCase(); //action to be performed e.g., 'Edit', 'Delete'
        var tableID = elem.attr('data-table'); //get target table
        var btntype = elem.attr('data-btntype'); //type of button: single, multi, all
        var title = elem.find(".action-label").html();
        var message = elem.attr("data-error-message");

        if (!message) {
            message = "No records selected for " + title + " action";
        }

        //validate event before passing to handler
        var table = $('#' + tableID).DataTable();
        var selectedRows = table.rows({
            selected: true
        }).count(); //number of rows selected

        var triggerEvent = true;

        //do button type validation based on the number of records selected
        if (btntype == "single" || btntype == "multi") {
            if (selectedRows == 0) {
                triggerEvent = false;
            } else if (selectedRows > 1 && btntype == "single") { //sort out 'single record buttons'
                triggerEvent = false;
            }
        }

        if (triggerEvent) { //trigger button event, else deal with error
            var event = jQuery.Event("addbuttonevents");
            event.tableID = tableID;
            event.task = task;
            event.title = title;
            $('body').trigger(event);
        } else {
            //alert user
            button_event_alert(message);
        }

    });
}


function do_table_buttons_events_server_side(component) {
    //attaches events to table buttons - server-side processing version to function with similar name

    $(document)
        .off("click", ".copo-dt")
        .on("click", ".copo-dt", function (event) {
            event.preventDefault();

            $('.copo-dt').webuiPopover('destroy');


            var elem = $(this);
            var task = elem.attr('data-action').toLowerCase(); //action to be performed e.g., 'Edit', 'Delete'
            var tableID = elem.attr('data-table'); //get target table
            var btntype = elem.attr('data-btntype'); //type of button: single, multi, all
            var title = elem.find(".action-label").html();
            var message = elem.attr("data-error-message");

            if (!message) {
                message = "No records selected for " + title + " action";
            }

            //validate event before passing to handler
            var selectedRows = server_side_select[component].length;

            var triggerEvent = true;

            //do button type validation based on the number of records selected
            if (btntype == "single" || btntype == "multi") {
                if (selectedRows == 0) {
                    triggerEvent = false;
                } else if (selectedRows > 1 && btntype == "single") { //sort out 'single record buttons'
                    triggerEvent = false;
                }
            }

            if (triggerEvent) { //trigger button event, else deal with error
                var event = jQuery.Event("addbuttonevents");
                event.tableID = tableID;
                event.task = task;
                event.title = title;
                $('body').trigger(event);
            } else {
                //alert user
                button_event_alert(message);
            }

        });
}

function button_event_alert(message) {
    BootstrapDialog.show({
        title: "Record action",
        message: message,
        cssClass: 'copo-modal3',
        closable: false,
        animate: true,
        type: BootstrapDialog.TYPE_WARNING,
        buttons: [{
            label: 'OK',
            cssClass: 'tiny ui basic orange button',
            action: function (dialogRef) {
                dialogRef.close();
            }
        }]
    });
}


function display_copo_alert(alertType, alertMessage, displayDuration) {
    //function displays alert or info to the user
    //alertType:  'success', 'warning', 'info', 'danger' - modelled after bootstrap alert classes
    //alertMessage: the actual message to be displayed to the user
    //displayDuration: how long should the alert be displayed for before taking it down

    var infoPanelElement = $("#page_alert_panel");

    if (infoPanelElement.length) {
        //reveal tab if not already shown
        $('.copo-sidebar-tabs a[href="#copo-sidebar-info"]').tab('show');

        var alertElement = $(".alert-templates").find(".alert-" + alertType).clone();
        alertElement.find(".alert-message").html(alertMessage);

        infoPanelElement.prepend(alertElement);
    }

}

function deselect_records(tableID) {
    var table = $('#' + tableID).DataTable();
    table.rows().deselect();
}

function do_render_server_side_table(componentMeta) {
    //use this function for server-side processing of large tables

    try {
        componentMeta.table_columns = JSON.parse($("#table_columns").val());

    } catch (err) {
    }

    var tableID = componentMeta.tableID;
    var component = componentMeta.component;

    var columnDefs = [];

    //add special formatting here for datafile name column to break on length file names

    if (component == "datafile") {
        var target = -1;
        for (var i = 0; i < componentMeta.table_columns.length; ++i) {
            if (componentMeta.table_columns[i].data == "name") {
                columnDefs.push({
                    render: function (data, type, full, meta) {
                        return "<div style='word-wrap: break-word; width:400px;'>" + data + "</div>";
                    },
                    targets: i
                });

                break
            }
        }
    }

    var table = null;

    if ($.fn.dataTable.isDataTable('#' + tableID)) {
        // get table instance
        table = $('#' + tableID).DataTable();
    }

    if (table) {
        //if table instance already exists, refresh
        table.draw();
    } else {
        server_side_select[component] = [];

        table = $('#' + tableID).DataTable({
            "paging": true,
            "processing": true,
            "serverSide": true,
            "searchDelay": 850,
            "columns": componentMeta.table_columns,
            ajax: {
                url: copoVisualsURL,
                type: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    'task': 'server_side_table_data',
                    'component': component
                },
                dataFilter: function (data) {
                    var json = jQuery.parseJSON(data);
                    json.recordsTotal = json.records_total;
                    json.recordsFiltered = json.records_filtered;
                    json.data = json.data_set;

                    return JSON.stringify(json); // return JSON string
                }
            },
            "rowCallback": function (row, data) {
                if ($.inArray(data.DT_RowId, server_side_select[component]) !== -1) {
                    $(row).addClass('selected');
                }
            },
            createdRow: function (row, data, index) {
                $(row).addClass("draggable_tr");
            },
            fnDrawCallback: function () {
                refresh_tool_tips();
                var event = jQuery.Event("posttablerefresh"); //individual compnents can trap and handle this event as they so wish
                $('body').trigger(event);

                if (server_side_select[component].length > 0) {
                    var message = server_side_select[component].length + " records selected";
                    if (server_side_select[component].length == 1) {
                        message = server_side_select[component].length + " record selected";
                    }
                    $('#' + tableID + '_info').append("<span class='select-item select-item-1'>" + message + "</span>");
                }
            },
            buttons: [
                {
                    text: 'Select visible records',
                    action: function (e, dt, node, config) {
                        //remove custom select info
                        $('#' + tableID + '_info').find(".select-item-1").remove();

                        dt.rows().select();
                        var selectedRows = table.rows('.selected').ids().toArray();

                        for (var i = 0; i < selectedRows.length; ++i) {
                            var index = $.inArray(selectedRows[i], server_side_select[component]);

                            if (index === -1) {
                                server_side_select[component].push(selectedRows[i]);
                            }
                        }

                        $('#' + tableID + '_info')
                            .find(".select-row-message")
                            .html(server_side_select[component].length + " records selected");
                    }
                },
                {
                    text: 'Clear selection',
                    action: function (e, dt, node, config) {
                        dt.rows().deselect();
                        server_side_select[component] = [];
                        $('#' + tableID + '_info').find(".select-item-1").remove();
                    }
                }
            ],
            columnDefs: columnDefs,
            language: {
                select: {
                    rows: {
                        _: "<span class='select-row-message'>%d records selected</span>",
                        0: "",
                        1: "%d record selected"
                    }
                },
                "processing": "<div class='copo-i-loader'></div>"
            },
            dom: 'Bfr<"row"><"row info-rw" i>tlp'
        });

        table
            .buttons()
            .nodes()
            .each(function (value) {
                $(this)
                    .removeClass("btn btn-default")
                    .addClass('tiny ui button');
            });

        place_task_buttons(componentMeta); //this will place custom buttons on the table for executing tasks on records
        do_table_buttons_events_server_side(component);

        table.on('click', 'tr >td', function () {
            var classList = ["annotate-datafile", "summary-details-control", "detail-hover-message"]; //don't select on columns with these classes
            var foundClass = false;

            var tdList = this.className.split(" ");

            for (var i = 0; i < tdList.length; ++i) {
                if ($.inArray(tdList[i], classList) > -1) {
                    foundClass = true;
                    break;
                }
            }

            if (foundClass) {
                return false;
            }

            var elem = $(this).closest("tr");

            var id = elem.attr("id");
            var index = $.inArray(id, server_side_select[component]);

            if (index === -1) {
                server_side_select[component].push(id);
            } else {
                server_side_select[component].splice(index, 1);
            }

            elem.toggleClass('selected');

            //selected message
            $('#' + tableID + '_info').find(".select-item-1").remove();
            var message = ''

            if ($('#' + tableID + '_info').find(".select-row-message").length) {
                if (server_side_select[component].length > 0) {
                    message = server_side_select[component].length + " records selected";
                    if (server_side_select[component].length == 1) {
                        message = server_side_select[component].length + " record selected";
                    }

                    $('#' + tableID + '_info')
                        .find(".select-row-message")
                        .html(message);
                } else {
                    $('#' + tableID + '_info')
                        .find(".select-row-message")
                        .html("");
                }
            } else {
                if (server_side_select[component].length > 0) {
                    message = server_side_select[component].length + " records selected";
                    if (server_side_select[component].length == 1) {
                        message = server_side_select[component].length + " record selected";
                    }
                    $('#' + tableID + '_info').append("<span class='select-item select-item-1'>" + message + "</span>");
                }
            }

        });
    }


    $('#' + tableID + '_wrapper')
        .find(".dataTables_filter")
        .find("input")
        .removeClass("input-sm")
        .attr("placeholder", "Search " + componentMeta.title)
        .attr("size", 30);

    //handle event for table details
    $('#' + tableID + ' tbody')
        .off('click', 'td.summary-details-control')
        .on('click', 'td.summary-details-control', function (event) {
            event.preventDefault();

            var event = jQuery.Event("posttablerefresh"); //individual components can trap and handle this event as they so wish
            $('body').trigger(event);

            var tr = $(this).closest('tr');
            var row = table.row(tr);
            tr.addClass('showing');

            if (row.child.isShown()) {
                // This row is already open - close it
                row.child('');
                row.child.hide();
                tr.removeClass('showing');
                tr.removeClass('shown');
            } else {
                $.ajax({
                    url: copoVisualsURL,
                    type: "POST",
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    data: {
                        'task': "attributes_display",
                        'component': componentMeta.component,
                        'target_id': row.data().record_id
                    },
                    success: function (data) {
                        if (data.component_attributes.columns) {
                            // expand row

                            var contentHtml = $('<table/>', {
                                cellspacing: "0",
                                border: "0",
                                class: "ui compact definition selectable celled table"
                            });

                            for (var i = 0; i < data.component_attributes.columns.length; ++i) {
                                var colVal = data.component_attributes.columns[i];

                                var colTR = $('<tr/>');
                                contentHtml.append(colTR);

                                colTR
                                    .append($('<td/>').append(colVal.title))
                                    .append($('<td/>').append("<div style='width:300px; word-wrap: break-word;'>" + data.component_attributes.data_set[colVal.data] + "</div>"));
                            }

                            row.child($('<div></div>').append(contentHtml).html()).show();
                            tr.removeClass('showing');
                            tr.addClass('shown');
                        }
                    },
                    error: function () {
                        alert("Couldn't retrieve " + component + " attributes!");
                        return '';
                    }
                });
            }
        });

    //handle event for annotation of of datafile
    $('#' + tableID + ' tbody')
        .off('click', 'td.annotate-datafile')
        .on('click', 'td.annotate-datafile', function (event) {
            event.preventDefault();

            var tr = $(this).closest('tr');
            var record_id = tr.attr("id");
            record_id = record_id.split("row_").slice(-1)[0];
            var loc = $("#file_annotate_url").val().replace("999", record_id);
            window.location.replace(loc);
        });

} //end of func


function do_render_component_table(data, componentMeta) {
    var tableID = componentMeta.tableID;
    var dataSet = data.table_data.dataSet;
    var cols = data.table_data.columns;

    set_empty_component_message(dataSet.length); //display empty component message when there's no record

    if (dataSet.length == 0) {
        return false;
    }

    //set data
    var table = null;

    if ($.fn.dataTable.isDataTable('#' + tableID)) {
        //if table instance already exists, then do refresh
        table = $('#' + tableID).DataTable();
    }

    if (table) {
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
    } else {
        table = $('#' + tableID).DataTable({
            data: dataSet,
            select: true,
            searchHighlight: true,
            fixedHeader: true,
            ordering: true,
            lengthChange: true,
            scrollX: true,
            scrollY: 350,
            buttons: [
                'selectAll',
                {
                    text: 'Select filtered',
                    action: function (e, dt, node, config) {
                        var filteredRows = dt.rows({order: 'index', search: 'applied'});
                        if (filteredRows.count() > 0) {
                            dt.rows().deselect();
                            filteredRows.select();
                        }
                    }
                },
                'selectNone',
                {
                    extend: 'csv',
                    text: 'Export CSV',
                    title: null,
                    filename: "copo_" + String(tableID) + "_data"
                }
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
                buttons: {
                    selectAll: "Select all",
                    selectNone: "Clear selection"
                }
            },
            order: [[1, 'asc']],
            columns: cols,
            fnDrawCallback: function () {
                refresh_tool_tips();
                var event = jQuery.Event("posttablerefresh"); //individual compnents can trap and handle this event as they so wish
                $('body').trigger(event);
            },
            "columnDefs": [{
                "targets": "_all",
                "createdCell": function (td, cellData, rowData, row, col) {
                    if (cellData == "") {
                        $(td).addClass("cell-no-content")
                    }
                }
            }],
            createdRow: function (row, data, index) {
                //add class to row for ease of selection later
                var recordId = index;
                try {
                    recordId = data.record_id;
                } catch (err) {
                }

                $(row).addClass(tableID + recordId);
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

        place_task_buttons(componentMeta); //this will place custom buttons on the table for executing tasks on records
    }

    $('#' + tableID + '_wrapper')
        .find(".dataTables_filter")
        .find("input")
        .removeClass("input-sm")
        .attr("placeholder", "Search " + componentMeta.title)
        .attr("size", 30);


    //handle event for table details
    $('#' + tableID + ' tbody')
        .off('click', 'td.summary-details-control')
        .on('click', 'td.summary-details-control', function (event) {
            event.preventDefault();

            var event = jQuery.Event("posttablerefresh"); //individual compnents can trap and handle this event as they so wish
            $('body').trigger(event);

            var tr = $(this).closest('tr');
            var row = table.row(tr);
            tr.addClass('showing');

            if (row.child.isShown()) {
                // This row is already open - close it
                row.child('');
                row.child.hide();
                tr.removeClass('showing');
                tr.removeClass('shown');
            } else {
                $.ajax({
                    url: copoVisualsURL,
                    type: "POST",
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    data: {
                        'task': "attributes_display",
                        'component': componentMeta.component,
                        'target_id': row.data().record_id
                    },
                    success: function (data) {
                        if (data.component_attributes.columns) {
                            // expand row

                            var contentHtml = $('<table/>', {
                                // cellpadding: "5",
                                cellspacing: "0",
                                border: "0",
                                // style: "padding-left:50px;"
                            });

                            for (var i = 0; i < data.component_attributes.columns.length; ++i) {
                                var colVal = data.component_attributes.columns[i];

                                var colTR = $('<tr/>');
                                contentHtml.append(colTR);

                                colTR
                                    .append($('<td/>').append(colVal.title))
                                    .append($('<td/>').append(data.component_attributes.data_set[colVal.data]));

                            }

                            row.child($('<div></div>').append(contentHtml).html()).show();
                            tr.removeClass('showing');
                            tr.addClass('shown');
                        }
                    },
                    error: function () {
                        alert("Couldn't retrieve " + component + " attributes!");
                        return '';
                    }
                });
            }
        });

} //end of func


function load_records(componentMeta) {
    var csrftoken = $.cookie('csrftoken');

    //loader
    var tableLoader = null;
    if ($("#component_table_loader").length) {
        tableLoader = $('<div class="copo-i-loader"></div>');
        $("#component_table_loader").append(tableLoader);
    }

    $.ajax({
        url: copoVisualsURL,
        type: "POST",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            'task': 'table_data',
            'component': componentMeta.component
        },
        success: function (data) {
            do_render_component_table(data, componentMeta);

            //remove loader
            if (tableLoader) {
                tableLoader.remove();
            }
        },
        error: function () {
            alert("Couldn't retrieve " + componentMeta.component + " data!");
        }
    });
}
