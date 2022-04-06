$(document).ready(function () {
    load_manifest_submission_list();
    $(document).on("click", ".submit_button_clicked", submit_button_clicked)
})

function load_manifest_submission_list() {
    var csrftoken = $('[name="csrfmiddlewaretoken"]').val();
    $.ajax({
        url: "/copo/get_manifest_submission_list/",
        headers: {
            'X-CSRFToken': csrftoken
        }
    }).done(function (data) {
        data = JSON.parse(data)
        out = {}
        out.table_data = {}
        out.table_data.dataSet = data
        do_display_manifest_submissions(out)
    })
}

function do_display_manifest_submissions(data) {
    var dtd = data.table_data.dataSet;
    var tableID = "manifest_table";
    set_empty_component_message(dtd.length, "#" + tableID); //display empty submission message.

    if (dtd.length == 0) {
        return false;
    }

    var dataSet = get_manifest_table_dataset(dtd);


    //set data
    var table = null;

    if ($.fn.dataTable.isDataTable('#' + tableID)) {
        //if table instance already exists, then do refresh
        table = $('#' + tableID).DataTable();
    }

    if (table) {
        //clear old, set new data
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

            searchHighlight: true,
            ordering: true,
            lengthChange: false,
            buttons: [],
            select: false,
            language: {
                "emptyTable": "No submission data available.",
            },
            order: [
                [1, "desc"]
            ],
            columns: [
                {
                    "data": null,
                    "orderable": false,

                    "render": function (rowdata) {
                        var renderHTML = get_card_panel();
                        var disabled_items = [];


                        renderHTML
                            .removeClass("component-type-panel")
                            .addClass("submission-panel")
                            .attr({"data-id": rowdata.record_id});


                        //set attributes
                        var bundle_name = rowdata.bundle_name;
                        if (!bundle_name) {
                            bundle_name = 'No associated bundle';
                        }

                        //renderHTML.find(".panel-header-1").html(bundle_name);

                        var attrHTML = renderHTML.find(".attr-placeholder").first().clone().css("display", "block");
                        attrHTML.find(".attr-key").html("Repository:");

                        var target_repository = '';
                        if (rowdata.repository_type) {
                            target_repository = " (" + rowdata.repository_type + ")";
                        } else {
                            disabled_items.push('view_repo_details');
                            target_repository = 'N/A <i data-html="A destination repository is yet to be assigned. Please select <strong>submit</strong> from the tasks menu to assign a repository and submit the record." class="info circle white icon copo-tooltip"></i>';
                        }

                        attrHTML.find(".attr-value").html(target_repository);
                        renderHTML.find(".attr-placeholder").parent().append(attrHTML);

                        var attrHTML = renderHTML.find(".attr-placeholder").first().clone().css("display", "block");
                        attrHTML.find(".attr-key").html("Last modified:");

                        renderHTML.find(".attr-placeholder").parent().append(attrHTML);

                        //define status
                        var defined_status_codes = ["completed", "pending", "error", "processing"];
                        var submission_status = rowdata.complete.toString().toLowerCase();

                        if (submission_status == "true") {
                            submission_status = "completed";
                        } else if (!defined_status_codes.includes(submission_status)) {
                            submission_status = "pending";
                        }

                        var submissionStatus = renderHTML.find(".bundle-status");

                        if (submission_status == 'completed') {
                            submissionStatus.addClass("stop circle outline green");
                            submissionStatus.prop('title', 'Completed submission');
                            disabled_items.push('submit');
                            disabled_items.push('delete_submission');
                        } else if (submission_status == 'pending') {
                            submissionStatus.addClass("stop circle outline grey");
                            submissionStatus.prop('title', 'Pending submission');
                        } else if (submission_status == 'error') {
                            submissionStatus.addClass("stop circle outline red");
                            submissionStatus.prop('title', 'Error in submission');
                        } else if (submission_status == 'processing') {
                            submissionStatus.addClass("stop circle outline orange");
                            submissionStatus.prop('title', 'Processing submission');
                            disabled_items.push('submit');
                            disabled_items.push('delete_submission');
                        }

                        //define menu
                        var componentMenu = renderHTML.find(".component-menu");
                        componentMenu.html('');
                        componentMenu.append('<div id="submit_' + rowdata["record_id"] + '" class="submit_button_clicked item">Submit</div>');
                        componentMenu.append('<div class="divider"></div>');
                        componentMenu.append('<div data-task="view_datafiles" class="item submissionmenu">View Datafiles</div>');
                        componentMenu.append('<div data-task="view_accessions" class="item submissionmenu">View Accessions</div>');
                        componentMenu.append('<div data-task="view_repo_details" class="item submissionmenu">View Repo Details</div>');
                        componentMenu.append('<div data-task="view_in_remote" class="item submissionmenu">View in Remote</div>');
                        componentMenu.append('<div class="divider"></div>');
                        componentMenu.append('<div data-task="lift_embargo" class="item submissionmenu">Lift Embargo</div>');
                        componentMenu.append('<div class="divider"></div>');
                        componentMenu.append('<div data-task="delete_submission" class="item submissionmenu">Delete Submission</div>');

                        //process disabled item list
                        componentMenu.find(".submissionmenu").each(function (indx, menuitem) {
                            if (disabled_items.indexOf($(menuitem).attr("data-task")) > -1) {
                                $(menuitem).addClass("disabled");
                            }
                        });


                        return $('<div/>').append(renderHTML).html();
                    }


                },

                {
                    "data": "record_id",
                    "visible": false
                },
            ],
            "columnDefs": [],
            fnDrawCallback: function () {
                refresh_tool_tips();
            },
            createdRow: function (row, data, index) {
            },
            dom: 'Bfr<"row"><"row info-rw" i>tlp',

        });

        table
            .buttons()
            .nodes()
            .each(function (value) {
                $(this)
                    .removeClass("btn btn-default")
                    .addClass('tiny ui basic button');
            });
    }
    /*
    $('#' + tableID + '_wrapper')
        .find(".dataTables_filter")
        .find("input")
        .removeClass("input-sm")
        .attr("placeholder", "Search submissions")
        .attr("size", 20);

    //get visible records
    var visibleRows = table.rows({page: 'current'}).ids().toArray();
    var submission_ids = [];
    for (var i = 0; i < visibleRows.length; ++i) {
        submission_ids.push(visibleRows[i].split("row_").slice(-1)[0])
    }
*/
    // update status for submission records
    //get_submission_information(submission_ids);
}


function get_manifest_table_dataset(dtd) {
    var dataSet = [];

    for (var i = 0; i < dtd.length; ++i) {
        var data = dtd[i];
        // get submission type
        var manifest_submission = null
        if (data.hasOwnProperty("manifest_submission")) {
            manifest_submission = 1
        } else {
            manifest_submission = 0
        }
        //get s_n
        var s_n = '';
        if (data.hasOwnProperty("s_n")) {
            s_n = data.s_n;
        }

        //get submission id
        var record_id = '';
        if (data.hasOwnProperty("record_id")) {
            record_id = data.record_id;
        }
        if (data.hasOwnProperty("_id")) {
            record_id = data._id.$oid
        }

        //get row id
        var DT_RowId = '';
        if (data.hasOwnProperty("DT_RowId")) {
            DT_RowId = data.DT_RowId;
        } else {
            DT_RowId = "row_" + data._id.$oid
        }

        //get repository_name
        var repository_name = '';
        if (data.hasOwnProperty("repository_name")) {
            repository_name = data.repository_name;
        }

        //get repository_type
        var repository_type = '';
        if (data.hasOwnProperty("repository_type")) {
            repository_type = data.repository_type;
        }
        if (data.hasOwnProperty("repository")) {
            repository_type = data.repository
        }

        //get bundle name
        var bundle_name = '';
        if (data.hasOwnProperty("bundle_name")) {
            bundle_name = data.bundle_name;
        }

        //get complete status
        var complete = 'false';
        if (data.hasOwnProperty("complete")) {
            complete = data.complete;
        }

        //get date modified
        var date_modified = '';
        if (data.hasOwnProperty("date_modified")) {
            date_modified = data.date_modified;
        }


        if (record_id) {
            let option = {};
            if (manifest_submission) {
                option["record_id"] = record_id;
                option["complete"] = complete;
                option["repository_type"] = repository_type;
                option["s_n"] = s_n;
                option["DT_RowId"] = DT_RowId;
            } else {
                option["s_n"] = s_n;
                option["DT_RowId"] = DT_RowId;
                option["repository_type"] = repository_type;
                option["bundle_name"] = bundle_name;
                option["repository_name"] = repository_name;
                option["date_modified"] = date_modified;
                option["record_id"] = record_id;
                option["complete"] = complete;
            }
            dataSet.push(option);
        }
    }

    return dataSet;
}

function submit_button_clicked(evt) {
    evt.preventDefault()
    let sub_id = evt.currentTarget.id.split("_")[1]

    $.ajax({
        url: "/copo/init_manifest_submission/",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {"submission_id": sub_id},
        method: "POST"
    }).done(function () {

    })

}
