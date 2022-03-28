$(document).ready(function () {

        // test starts
        // test ends
        //******************************Event Handlers Block*************************//
        var component = "submission";

        var copoFormsURL = "/copo/copo_forms/";
        var copoVisualsURL = "/copo/copo_visualize/";
        var csrftoken = $.cookie('csrftoken');

        show_submission_status_codes();

        var componentMeta = get_component_meta(component);


        load_submissions();

        // handle/attach events to table buttons
        $('body').on('addbuttonevents', function (event) {
            do_record_task(event);
        });


        //trigger submission status update for a submission record
        $(document).on('trigger_submission_status', function (event) {
            get_submission_information([event.elementId]);
        });

        //

        //create a web socket to manage submission progress reports
        var profileId = $('#profile_id').val();


        var wsprotocol = 'ws://';

        if (window.location.protocol == "https:") {
            wsprotocol = 'wss://';
        }

        var submissionSocket = new ReconnectingWebSocket(
            wsprotocol + window.location.host +
            '/ws/submission_status/' + profileId + '/');

        submissionSocket.onmessage = function (e) {
            var data = JSON.parse(e.data);

            if (data.hasOwnProperty('type') && data.type == "submission_status") {
                var event_target_id = '';
                try {
                    event_target_id = data.submission_id;
                } catch (err) {

                }

                if (event_target_id) {
                    get_submission_information([event_target_id]);
                }

            } else if (data.hasOwnProperty('type') && data.type == "file_transfer_status") {
                var event_target_id = '';
                var event_status_message = '';
                try {
                    event_target_id = data.submission_id;
                    event_status_message = data.status_message;
                } catch (err) {

                }

                if (event_target_id && event_status_message) {
                    var eventOpt = {'submission_id': event_target_id, 'status_message': event_status_message};
                    get_file_transfer_status(eventOpt);
                }
            }


        };

    //submissionSocket.send(JSON.stringify({
    //    'message': message
    //}));
    submissionSocket.onconnecting = function (e) {
        console.log("connecting" + e)
    }
    submissionSocket.onclose = function (e) {
        console.log(e)
        console.error('Submission socket closed unexpectedly' + e);
    };

    //submission tasks
    $(document).on('click', '.submissionmenu', function (event) {
        event.preventDefault();
        dispatch_submission_events($(this));
    });

        //handle destination repository change
        $(document).on('destination_repo_change', function (event) {
            handle_repo_change_event($("#" + event.elementId).closest(".submission-panel").attr("data-id"));
        });


        $(document).on('click', '#publish_dataset', function (event) {
            e = $(event.currentTarget)
            sub_id = $(e).data('submission_id')
            $.ajax({
                url: "/copo/dataverse_publish/",
                type: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    'sub_id': sub_id
                },
                success: function (data) {
                    console.log(data)
                },
                error: function (data) {
                    console.log(data)
                }
            });
        });

        //show submission metadata
        $(document).on('click', '.show-sub-meta', function (event) {
            let elem = $(this);
            show_submission_metadata($(this).attr("data-submission-id"))
        });

        refresh_tool_tips();

        //******************************Functions Block******************************//

        function show_submission_status_codes() {
            var message = $('<div class="webpop-content-div"></div>');

            var infoPanelElement = trigger_global_notification();

            var codeList = '<div style="margin-top: 10px;"><ul class="list-group">\n' +
                '  <li class="list-group-item active" style="background: #31708f; text-shadow: none; border-color: #d9edf7; color: #fff;">Submission status codes</li>\n' +
                '  <li class="list-group-item"><i title="" class=" icon stop large circle outline grey"></i>Pending<div class="small">Submission is pending. Use the submit option from the actions menu to commence submission.</div></li>\n' +
                '  <li class="list-group-item"><i title="" class=" icon stop large circle outline green"></i>Completed<div class="small">Submission has been completed. Use the view accessions option from the actions menu to view accessions or DOIs.</div></li>\n' +
                '  <li class="list-group-item"><i title="" class=" icon stop large circle outline orange"></i>Processing<div class="small">Submission is currently being processed or has been scheduled for processing. Updates will be provided.</div></li>\n' +
                '  <li class="list-group-item"><i title="" class=" icon stop large circle outline red"></i>Error<div class="small">Submission has issues. Use the view issues option from the menu for more information. Resolve the issues and resubmit.</div></li>\n' +
                '</ul></div>'


            message.append(codeList);
            infoPanelElement.prepend(message);
        }

        function get_table_dataset(dtd) {
            var dataSet = [];

            for (var i = 0; i < dtd.length; ++i) {
                var data = dtd[i];

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

                //get row id
                var DT_RowId = '';
                if (data.hasOwnProperty("DT_RowId")) {
                    DT_RowId = data.DT_RowId;
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
                    var option = {};
                    option["s_n"] = s_n;
                    option["DT_RowId"] = DT_RowId;
                    option["repository_type"] = repository_type;
                    option["bundle_name"] = bundle_name;
                    option["repository_name"] = repository_name;
                    option["date_modified"] = date_modified;
                    option["record_id"] = record_id;
                    option["complete"] = complete;
                    dataSet.push(option);
                }
            }

            return dataSet;
        }

        function do_display_submissions(data) {
            var dtd = data.table_data.dataSet;
            set_empty_component_message(dtd.length); //display empty submission message.

            if (dtd.length == 0) {
                return false;
            }

            var dataSet = get_table_dataset(dtd);
            var tableID = componentMeta.tableID;

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

                                renderHTML.find(".panel-header-1").html(bundle_name);

                                var attrHTML = renderHTML.find(".attr-placeholder").first().clone().css("display", "block");
                                attrHTML.find(".attr-key").html("Repository:");

                                var target_repository = '';
                                if (rowdata.repository_name && rowdata.repository_type) {
                                    target_repository = rowdata.repository_name + " (" + rowdata.repository_type + ")";
                                } else {
                                    disabled_items.push('view_repo_details');
                                    target_repository = 'N/A <i data-html="A destination repository is yet to be assigned. Please select <strong>submit</strong> from the tasks menu to assign a repository and submit the record." class="info circle white icon copo-tooltip"></i>';
                                }

                                attrHTML.find(".attr-value").html(target_repository);
                                renderHTML.find(".attr-placeholder").parent().append(attrHTML);

                                var attrHTML = renderHTML.find(".attr-placeholder").first().clone().css("display", "block");
                                attrHTML.find(".attr-key").html("Last modified:");
                                attrHTML.find(".attr-value").html(rowdata.date_modified);
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
                                componentMenu.append('<div data-task="submit" class="item submissionmenu">Submit</div>');
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
                            "data": "s_n",
                            "title": "S/N",
                            "visible": false
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

            // update status for submission records
            get_submission_information(submission_ids);
        }

        function load_submissions() {
            var loader = $('<div class="copo-i-loader" style="margin-left: 40%;"></div>');
            $("#cover-spin-bundle").html(loader);

            $.ajax({
                url: copoVisualsURL,
                type: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    'task': 'table_data',
                    'component': component
                },
                success: function (data) {
                    loader.remove();
                    do_display_submissions(data);
                },
                error: function (data) {
                    loader.remove();
                    alert("Couldn't retrieve submissions!");
                }
            });
        }

        function get_file_transfer_status(transfer_update) {
            var submission_id = transfer_update.submission_id;
            var status_message = transfer_update.status_message;
            var viewPort = trigger_global_notification();
            var messageClass = "info";

            var messageTitle = "";
            var getInstructionsPane = format_feedback_message(status_message, messageClass, messageTitle);

            try {
                viewPort.find("#file-transfer-transcript" + submission_id).remove();
            } catch (err) {
            }

            var feedbackDiv = $('<div/>',
                {
                    id: "file-transfer-transcript" + submission_id,
                    style: "cursor:pointer;"
                });


            feedbackDiv.append(getInstructionsPane);
            viewPort.prepend(feedbackDiv);

            feedbackDiv.mouseover(function () {
                $('.submission-panel[data-id="' + submission_id + '"]').find(".panel-body").addClass("transfer-highlight-1");

                $('html, body').animate({
                    scrollTop: $('.submission-panel[data-id="' + submission_id + '"]').closest(".submission-panel").offset().top - 60
                }, 'slow');
            });

            feedbackDiv.mouseout(function () {
                $('.submission-panel[data-id="' + submission_id + '"]').find(".panel-body").removeClass("transfer-highlight-1");
            });
        }

        function get_submission_information(submission_ids) {
            $.ajax({
                url: "/rest/get_submission_status/",
                type: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    'submission_ids': JSON.stringify(submission_ids)
                },
                success: function (data) {
                    for (const key of Object.keys(data)) {
                        //update submission record status and submission status message
                        var table = $('#' + componentMeta.tableID).DataTable();
                        var rec = data[key];
                        var submission_data = table.row('#row_' + rec.record_id).data();
                        submission_data.complete = rec.complete;
                        table.row('#row_' + rec.record_id).data(submission_data).draw();

                        //display submission status message
                        if (rec.hasOwnProperty('transcript_status') && rec.hasOwnProperty('transcript_message')
                            && rec.transcript_status != '' && rec.transcript_message != '') {
                            var viewPort = get_viewport(rec.record_id);
                            var messageClass = "success";

                            if (rec.transcript_status == "error") {
                                messageClass = "negative"
                            } else if (rec.transcript_status == "info") {
                                messageClass = "info"
                            }

                            var messageTitle = "";
                            var getInstructionsPane = format_feedback_message(rec.transcript_message, messageClass, messageTitle);
                            viewPort.prepend(getInstructionsPane);
                        }
                    }
                },
                error: function () {
                    console.log("Couldn't retrieve submission status!");
                }
            });
        }

        function dispatch_submission_events(elem) {
            var submission_id = elem.closest(".submission-panel").attr("data-id");

            var viewPort = elem.closest(".submission-panel").find(".pbody");
            elem.addClass("active");
            var task = elem.data("task");

            $('html, body').animate({
                scrollTop: elem.closest(".submission-panel").offset().top - 60
            }, 'slow');

            if (task == "submit") {
                do_submit_task(submission_id);
            } else if (task == "view_datafiles") {
                show_submission_datafiles(submission_id);
            } else if (task == "view_in_remote") {
                view_in_remote(submission_id);
            } else if (task == "view_accessions") {
                view_accessions(submission_id);
            } else if (task == "view_repo_details") {
                view_repo_details(submission_id);
            } else if (task == "delete_submission") {
                delete_submission_record(submission_id);
            } else if (task == "lift_embargo") {
                lift_submission_embargo(submission_id);
            }
        }

        function lift_submission_embargo(submission_id) {
            var viewPort = get_viewport(submission_id);

            viewPort.html('');

            let table = $('#' + componentMeta.tableID).DataTable();
            let submission_data = table.row('#row_' + submission_id).data();
            var submission_name = "";
            if (submission_data.hasOwnProperty("bundle_name")) {
                submission_name = submission_data.bundle_name;
            }
            var messageContent = `Are you sure you want to lift embargo on the submission <strong>${submission_name}</strong>?`;

            var message = $('<div/>', {class: "webpop-content-div MessageDiv"});
            message.append(messageContent);
            message.append('<div style="margin-top:5px;">Please note that this submission will be made public should you choose to proceed.</div>')

            var doTidyClose = {
                closeIt: function (dialogRef) {
                    dialogRef.close();

                    var loader = $('<div class="copo-i-loader" style="margin-left: 40%;"></div>');
                    viewPort.html(loader);

                    $.ajax({
                        url: copoFormsURL,
                        type: "POST",
                        headers: {
                            'X-CSRFToken': csrftoken
                        },
                        data: {
                            'task': 'lift_submission_embargo',
                            'component': component,
                            'target_id': submission_id,
                        },
                        success: function (data) {
                            viewPort.html('');
                            var messageClass = "info";
                            var status_message = "Request returned no feedback";
                            if (data.hasOwnProperty('status') && data.hasOwnProperty('message')) {

                                var status = data.status.toString();

                                if (status == "success" || status == "true") {
                                    messageClass = "success";
                                } else if (status == "error" || status == "false") {
                                    messageClass = "error";
                                }

                                if (data.message != "") {
                                    status_message = data.message;
                                }

                                var messageTitle = "Lift submission embargo";
                                var getInstructionsPane = format_feedback_message(status_message, messageClass, messageTitle);
                                viewPort.prepend(getInstructionsPane);
                            }

                        },
                        error: function (data) {
                            console.log(data.responseText);

                            let feedbackControl = get_alert_control();
                            let alertClass = "alert-danger";

                            feedbackControl
                                .removeClass("alert-success")
                                .addClass(alertClass);
                            feedbackControl.find(".alert-message").html("Encountered an error. Please check that you are connected to a network and try again.");

                            return true;
                        }
                    });
                }
            };

            BootstrapDialog.show({
                title: "Lift embargo on submission",
                message: message,
                // cssClass: 'copo-modal2',
                closable: false,
                animate: true,
                type: BootstrapDialog.TYPE_WARNING,
                size: BootstrapDialog.SIZE_NORMAL,
                buttons: [
                    {
                        id: 'btn-cancel-embargo-lift',
                        label: 'Cancel',
                        cssClass: 'tiny ui basic button',
                        action: function (dialogRef) {
                            dialogRef.close();
                        }
                    },
                    {
                        label: '<i style="padding-right: 5px;" class="fa fa-cloud-upload" aria-hidden="true"></i> Lift embargo',
                        cssClass: 'tiny ui basic orange button',
                        action: function (dialogRef) {
                            doTidyClose["closeIt"](dialogRef);
                        }
                    }
                ]
            });
        }

        function view_in_remote(submission_id) {
            var viewPort = get_viewport(submission_id);

            var loader = $('<div class="copo-i-loader" style="margin-left: 40%;"></div>');
            viewPort.html(loader);

            $.ajax({
                url: copoVisualsURL,
                type: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    'task': "view_submission_remote",
                    'component': componentMeta.component,
                    'target_id': submission_id
                },
                success: function (data) {
                    viewPort.html('');
                    var messageClass = "info";
                    var status_message = "Request returned no feedback";

                    if (data.hasOwnProperty('status')) {
                        var status = data.status.toString();

                        status_message = '';

                        if (data.hasOwnProperty('message') && data.message != "") {
                            status_message = data.message;
                        }

                        if (data.hasOwnProperty('urls') && data.urls.length != 0) {
                            status_message = $('<div/>');

                            var view_pane = $('<ul/>');
                            for (let i = 0; i < data.urls.length; ++i) {
                                var resource = data.urls[i];
                                view_pane.append('<li><a href="' + resource + '" target="_blank">' + resource + '</a></li>');
                            }

                            status_message.append(status_message).append(view_pane);
                            status_message = status_message.html();

                        } else if (status == "error" || status == "false") {
                            messageClass = "error";
                        }
                    }

                    viewPort.prepend(format_feedback_message(status_message, messageClass, "View in Remote"));

                },
                error: function () {
                    viewPort.html('');

                    let feedback = get_alert_control();
                    feedback
                        .removeClass("alert-success")
                        .addClass("alert-danger")
                        .addClass("page-notifications-node");

                    feedback.find(".alert-message").html("Encountered an error. Please check that you are connected to a network and try again.");
                    viewPort.append(feedback);
                }
            });
        }

        function delete_submission_record(submission_id) {
            var viewPort = get_viewport(submission_id);

            viewPort.html('');

            let table = $('#' + componentMeta.tableID).DataTable();
            let submission_data = table.row('#row_' + submission_id).data();
            var submission_name = "";
            if (submission_data.hasOwnProperty("bundle_name")) {
                submission_name = submission_data.bundle_name;
            }
            var messageContent = `Are you sure you want to delete the submission record <strong>${submission_name}</strong>?`;

            var message = $('<div/>', {class: "webpop-content-div MessageDiv"});
            message.append(messageContent);

            BootstrapDialog.show({
                title: "Delete submission record",
                message: message,
                // cssClass: 'copo-modal2',
                closable: false,
                animate: true,
                type: BootstrapDialog.TYPE_DANGER,
                size: BootstrapDialog.SIZE_NORMAL,
                buttons: [
                    {
                        id: "btn-cancel-delete-repo",
                        label: 'Cancel',
                        cssClass: 'tiny ui basic button',
                        action: function (dialogRef) {
                            dialogRef.close();
                        }
                    },
                    {
                        id: "btn-delete-repo",
                        label: '<i style="padding-right: 5px;" class="fa fa-trash-o" aria-hidden="true"></i> Delete',
                        cssClass: 'tiny ui basic red button',
                        action: function (dialogRef) {
                            var $button = this;
                            $button.disable();
                            $button.spin();

                            var btnCancel = dialogRef.getButton('btn-cancel-delete-repo');
                            btnCancel.disable();


                            $.ajax({
                                url: copoFormsURL,
                                type: "POST",
                                headers: {
                                    'X-CSRFToken': csrftoken
                                },
                                data: {
                                    'task': 'validate_and_delete',
                                    'component': component,
                                    'target_id': submission_id,
                                },
                                success: function (data) {
                                    if (data.hasOwnProperty("status") && data.status == "success") {
                                        var tableID = componentMeta.tableID;
                                        if ($.fn.dataTable.isDataTable('#' + tableID)) {
                                            var table = $('#' + tableID).DataTable();
                                            table.row("#row_" + submission_id).remove().draw();

                                            var infoPanelElement = trigger_global_notification();

                                            let feedback = get_alert_control();
                                            feedback
                                                .removeClass("alert-success")
                                                .addClass("alert-info")
                                                .addClass("page-notifications-node");

                                            feedback.find(".alert-message").html("Successfully deleted submission!");
                                            infoPanelElement.prepend(feedback);
                                        }
                                        dialogRef.close();

                                    } else if (data.hasOwnProperty("status") && data.status == "error") {
                                        let feedbackControl = get_alert_control();
                                        let alertClass = "alert-danger";

                                        feedbackControl
                                            .removeClass("alert-success")
                                            .addClass(alertClass);
                                        feedbackControl.find(".alert-message").html(data.message);

                                        dialogRef.getModalBody().find(".MessageDiv").html(feedbackControl);

                                        btnCancel.enable();
                                        $button.stopSpin();

                                        return true;
                                    }
                                },
                                error: function (data) {
                                    console.log(data.responseText);

                                    let feedbackControl = get_alert_control();
                                    let alertClass = "alert-danger";

                                    feedbackControl
                                        .removeClass("alert-success")
                                        .addClass(alertClass);
                                    feedbackControl.find(".alert-message").html("Encountered an error. Please check that you are connected to a network and try again.");

                                    dialogRef.getModalBody().find(".MessageDiv").html(feedbackControl);

                                    btnCancel.enable();
                                    $button.stopSpin();

                                    return true;
                                }
                            });

                            return true;
                        }
                    }
                ]
            });

        }


        function view_repo_details(submission_id) {
            var viewPort = get_viewport(submission_id);

            var loader = $('<div class="copo-i-loader" style="margin-left: 40%;"></div>');
            viewPort.html(loader);

            $.ajax({
                url: copoVisualsURL,
                type: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    'task': "get_destination_repo",
                    'component': componentMeta.component,
                    'target_id': submission_id
                },
                success: function (data) {
                    loader.remove();
                    let result = data.result;

                    var feedbackMessage = "Full details of the destination repository are provided below.";
                    var messageClass = "";
                    var messageTitle = "Repository details";

                    var getInstructionsPane = format_feedback_message(feedbackMessage, messageClass, messageTitle);

                    viewPort.append(getInstructionsPane);

                    var view_pane = $('<div/>', {
                        style: "margin-top:30px;",
                    });

                    viewPort.append(view_pane);


                    var tbl = $('<table class="ui compact definition selectable celled table"></table>');
                    view_pane.append(tbl);

                    var tbody = $('<tbody/>');
                    for (let i = 0; i < result.length; ++i) {
                        tbody.append('<tr><td>' + result[i].label + '</td><td>' + result[i].value + '</td></tr>');
                    }


                    var thead = $('<thead><tr><th></th><th></th></tr></thead>');
                    tbl
                        .append(thead)
                        .append(tbody);

                },
                error: function (data) {
                    console.log(data.responseText);

                    viewPort.html('');

                    let feedback = get_alert_control();
                    feedback
                        .removeClass("alert-success")
                        .addClass("alert-danger")
                        .addClass("page-notifications-node");

                    feedback.find(".alert-message").html("Encountered an error. Please check that you are connected to a network and try again.");
                    viewPort.append(feedback);
                }
            });
        }

        function handle_repo_change_event(submission_id) {
            var viewPort = get_viewport(submission_id);

            var destination_repo_id = $("#submission_destination_repo_" + submission_id).val();
            var previous_value = viewPort.find("#destination_repository_id_prv_" + submission_id).val();

            if (destination_repo_id == previous_value) { //nothing's change
                // other matters section
                var otherMattersSection = $('<div/>',
                    {
                        class: "submission-proceed-section",
                    });

                viewPort.append(otherMattersSection);
                proceed_submission(submission_id)
                return false;
            }

            //retain new value
            viewPort.find("#destination_repository_id_prv_" + submission_id).val(destination_repo_id);

            if (!destination_repo_id) {
                viewPort.find(".no-repo-feedback").show();
                viewPort.find(".submission-proceed-section").remove();
                return false;
            }


            //update submission record with the new value
            $.ajax({
                url: "/copo/set_destination_repository/",
                type: "POST",
                dataType: "json",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    'destination_repo_id': destination_repo_id,
                    'submission_id': submission_id,
                },
                success: function (data) {

                    var dtd = data.dataSet;
                    if (dtd.length) {
                        var dataSet = get_table_dataset(dtd);

                        //update submission table
                        let table = $('#' + componentMeta.tableID).DataTable();
                        let submission_data = table.row('#row_' + submission_id).data();
                        let new_data = dataSet[0];
                        new_data.s_n = submission_data.s_n;

                        table.row('#row_' + submission_id).data(new_data).draw();
                        do_submit_task(submission_id); //refresh submit panel
                    }
                },
                error: function () {
                    console.log("Couldn't update repository information!");
                }
            });
        }

        function proceed_submission(submission_id) {
            //function handles submission routines based on repository types -
            // those with special routines should be given a special case, all those can fall to the default handler


            var destination_repo_id = $("#submission_destination_repo_" + submission_id).val();
            var valueObject = selectizeObjects["submission_destination_repo_" + submission_id].options[destination_repo_id];
            var repo_type = valueObject.repo_type_unresolved;

            var viewPort = get_viewport(submission_id);

            // $('html, body').animate({
            //     scrollTop: viewPort.find(".submission-proceed-section").offset().top
            // }, 'slow');

            switch (repo_type) {
                case 'dataverse':
                    process_dataverse(submission_id);
                    break;
                case 'ckan':
                    process_ckan(submission_id);
                    break;
                case 'dspace':
                    process_dspace(submission_id);
                    break;
                default:
                    process_default(submission_id);
            }
        }

        function process_default(submission_id) {
            var processPanel = get_viewport(submission_id).find(".submission-proceed-section");

            //invoke submit button when all submission conditions are met.

            processPanel.append(submit_submission_record(submission_id));
            refresh_tool_tips();

            return true
        }

        function process_dataverse(submission_id) {
            var processPanel = get_viewport(submission_id).find(".submission-proceed-section");

            let params = {
                'submission_id': submission_id,
                "submission_context": "dataverse"
            };

            get_dataverse_display(processPanel, params);
            return true
        }

        function process_ckan(submission_id) {
            var processPanel = get_viewport(submission_id).find(".submission-proceed-section");

            let params = {
                'submission_id': submission_id,
                "submission_context": "new"
            };

            get_ckan_display(processPanel, params);
            return true
        }

        function process_dspace(submission_id) {
            var processPanel = get_viewport(submission_id).find(".submission-proceed-section");

            let params = {
                'submission_id': submission_id,
                "submission_context": "new"
            };

            get_dspace_display(processPanel, params);
            return true
        }


        function do_submit_task(submission_id) {
            var viewPort = get_viewport(submission_id);

            var loader = $('<div class="copo-i-loader" style="margin-left: 40%;"></div>');
            viewPort.html(loader);

            //get current and relevant repositories to support this submission
            $.ajax({
                url: copoVisualsURL,
                type: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    'task': "get_submission_meta_repo",
                    'component': componentMeta.component,
                    'target_id': submission_id
                },
                success: function (data) {
                    loader.remove();
                    let result = data.result;

                    //display any error
                    if (result.hasOwnProperty("status") && result.status == "error") {
                        var feedback = get_alert_control();
                        feedback
                            .removeClass("alert-success")
                            .addClass("alert-danger");

                        var message = $('<div/>', {class: "webpop-content-div"});
                        message
                            .append($('<div/>',
                                {
                                    html: "Please resolve the following issue(s) to proceed",
                                    style: "font-weight: bold"
                                }
                            ))
                            .append($('<div/>',
                                {
                                    html: result.message,
                                }
                            ));

                        feedback.find(".alert-message").append(message);
                        viewPort.append(feedback);

                        return false;
                    }

                    // description template section
                    var dTempSection = $('<div/>',
                        {
                            class: "submission-metadata-section",
                        });

                    viewPort.append(dTempSection);

                    if (result.hasOwnProperty("description_template")) {
                        var feedback = get_alert_control();
                        feedback
                            .removeClass("alert-success")
                            .addClass("alert-info");

                        var message = $('<div/>', {class: "webpop-content-div"});
                        message
                            .append($('<div/>',
                                {
                                    html: "Metadata template",
                                    style: "font-weight: bold"
                                }
                            ))
                            .append($('<div/>',
                                {
                                    html: result.description_template,
                                }
                            ));

                        feedback.find(".alert-message").append(message);

                        dTempSection
                            .append(feedback)
                            .append($('<input/>',
                                {
                                    type: "hidden",
                                    id: "description_template_" + submission_id,
                                    name: "description_template_" + submission_id,
                                    value: result.description_template
                                })
                            );
                    }

                    // destination repository section
                    var dRepoSection = $('<div/>',
                        {
                            class: "submission-destination-section",
                        });

                    viewPort.append(dRepoSection);

                    var feedback = get_alert_control();
                    feedback
                        .removeClass("alert-success")
                        .addClass("alert-warning no-repo-feedback");

                    var message = $('<div/>', {class: "webpop-content-div"});
                    message
                        .append($('<div/>',
                            {
                                html: "Destination repository required!",
                                style: "font-weight: bold"
                            }
                        ))
                        .append($('<div/>',
                            {
                                html: "Select a destination repository from the list below to proceed. Please contact an administrator if there are no repository options to select from.",
                            }
                        ));

                    feedback.find(".alert-message").append(message);
                    dRepoSection
                        .append(feedback)
                        .append($('<input/>',
                            {
                                type: "hidden",
                                id: "destination_repository_id_prv_" + submission_id,
                                name: "destination_repository_id_prv_" + submission_id,
                                value: result.destination_repository_id
                            })
                        );

                    if (result.hasOwnProperty("destination_repository_id") && result.destination_repository_id != "") {
                        dRepoSection.find(".no-repo-feedback").hide();
                        dRepoSection.find("#destination_repository_id_prv_" + submission_id).val(result.destination_repository_id);
                    }

                    // user repositories section
                    var userRepoSection = $('<div/>',
                        {
                            class: "submission-repositories-section",
                        });
                    viewPort.append(userRepoSection);

                    if (result.hasOwnProperty("relevant_repositories")) {
                        var option_values = [];
                        for (var i = 0; i < result.relevant_repositories.length; ++i) {
                            var option = {};
                            option.value = result.relevant_repositories[i]._id;
                            option.label = result.relevant_repositories[i].name;
                            option.type = result.relevant_repositories[i].type;
                            option.url = result.relevant_repositories[i].url;
                            option.repo_type_unresolved = result.relevant_repositories[i].repo_type_unresolved;
                            option.submission_id = submission_id;
                            option_values.push(option);
                        }


                        var formElem = {
                            "help_tip": "Please select a destination repository from the list.",
                            "default_value": result.destination_repository_id,
                            "ref": "",
                            "hidden": "false",
                            "label": "Destination repository",
                            "id": "submission_destination_repo_" + submission_id,
                            "placeholder": "Select a destination repository...",
                            "value_change_event": "destination_repo_change",
                            "type": "string",
                            "control": "copo-general-ontoselect",
                            "control_id_field": "value",
                            "control_label_field": "label",
                            "api_schema": [
                                {
                                    "id": "label",
                                    "label": "Name",
                                    "show_in_table": true
                                },
                                {
                                    "id": "type",
                                    "label": "Type",
                                    "show_in_table": true
                                },
                                {
                                    "id": "url",
                                    "label": "URL",
                                    "show_in_table": true
                                }
                            ],
                            "option_values": option_values
                        }

                        var elemValue = formElem.default_value;
                        userRepoSection.append(dispatchFormControl[controlsMapping[formElem.control.toLowerCase()]](formElem, elemValue));
                        userRepoSection.find(".constraint-label").remove();
                        refresh_tool_tips();
                    }
                },
                error: function () {
                    viewPort.html('');

                    let feedback = get_alert_control();
                    feedback
                        .removeClass("alert-success")
                        .addClass("alert-danger")
                        .addClass("page-notifications-node");

                    feedback.find(".alert-message").html("Encountered an error. Please check that you are connected to a network and try again.");
                    viewPort.append(feedback);
                }
            });
        }

        function view_accessions(submission_id) {
            var viewPort = get_viewport(submission_id);

            var loader = $('<div class="copo-i-loader" style="margin-left: 40%;"></div>');
            viewPort.html(loader);

            var tableID = 'submission_accessions_view_tbl' + submission_id;
            var tbl = $('<table/>',
                {
                    id: tableID,
                    "class": "ui cell table hover copo-noborders-table",
                    cellspacing: "0",
                    width: "100%"
                });

            var table_div = $('<div/>')
                .css({"margin-top": "20px"})
                .append(tbl);

            $.ajax({
                url: copoVisualsURL,
                type: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    'task': "get_submission_accessions",
                    'component': componentMeta.component,
                    'target_id': submission_id
                },
                success: function (data) {
                    loader.remove();
                    let dataSet = data.submission_accessions.dataSet;
                    let columns = data.submission_accessions.columns;
                    let message = "No accessions recorded!";

                    if (data.submission_accessions.hasOwnProperty("message") && data.submission_accessions.message != "") {
                        message = data.submission_accessions.message
                    }

                    if (dataSet.length == 0) {
                        let feedback = get_alert_control();
                        feedback
                            .removeClass("alert-success")
                            .addClass("alert-info");

                        feedback.find(".alert-message").html(message);
                        viewPort.append(feedback);

                        return false;
                    }

                    viewPort.append(table_div);

                    let rowGroup = null;
                    let groupAcessionRepos = ["ena"];
                    if (data.submission_accessions.hasOwnProperty('repository') && groupAcessionRepos.indexOf(data.submission_accessions.repository) > -1) {
                        rowGroup = {dataSrc: 3};
                    }

                    //set data
                    var table = null;

                    if ($.fn.dataTable.isDataTable('#' + tableID)) {
                        //if table instance already exists, do refresh
                        table = $('#' + tableID).DataTable();
                    }

                    var table = $('#' + tableID).DataTable({
                        data: dataSet,
                        columns: columns,
                        select: true,
                        searchHighlight: true,
                        ordering: true,
                        lengthChange: true,
                        order: [[3, 'asc']],
                        rowGroup: rowGroup,
                        columnDefs: [
                            {
                                "width": "10%",
                                "targets": [1]
                            }
                        ],
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
                                filename: "copo_accessions_" + String(submission_id) + "_data"
                            }
                        ],
                        language: {
                            "info": "Showing _START_ to _END_ of _TOTAL_ records",
                            "search": " ",
                            "lengthMenu": "show _MENU_ records",
                            buttons: {
                                selectAll: "Select all",
                                selectNone: "Clear selection"
                            }
                        },
                        fnDrawCallback: function () {
                            refresh_tool_tips();
                        },
                        createdRow: function (row, data, index) {
                            //add class to row for ease of selection later
                            var recordId = index;
                            try {
                                recordId = data.record_id;
                            } catch (err) {
                            }

                            $(row).addClass(tableID + recordId);
                        },
                        dom: 'Bfr<"row"><"row info-rw" i>tlp',
                    });

                    table
                        .buttons()
                        .nodes()
                        .each(function (value) {
                            $(this)
                                .removeClass("btn btn-default")
                                .addClass('tiny ui button');
                        });


                    refresh_tool_tips();

                    $('#' + tableID + '_wrapper')
                        .find(".dataTables_filter")
                        .find("input")
                        .removeClass("input-sm")
                        .attr("placeholder", "Search accessions")
                        .attr("size", 25);

                },
                error: function () {
                    viewPort.html('');

                    let feedback = get_alert_control();
                    feedback
                        .removeClass("alert-success")
                        .addClass("alert-danger")
                        .addClass("page-notifications-node");

                    feedback.find(".alert-message").html("Encountered an error. Please check that you are connected to a network and try again.");
                    viewPort.append(feedback);
                }
            });

        } // end of function


        function show_submission_datafiles(submission_id) {
            var parentElem = $('.submission-panel[data-id="' + submission_id + '"]');
            var viewPort = parentElem.find(".pbody");

            var loader = $('<div class="copo-i-loader" style="margin-left: 40%;"></div>');
            viewPort.html(loader);

            var tableID = 'submission_datafiles_view_tbl' + submission_id;
            var tbl = $('<table/>',
                {
                    id: tableID,
                    "class": "ui cell table hover copo-noborders-table",
                    cellspacing: "0",
                    width: "100%"
                });

            var table_div = $('<div/>')
                .css({"margin-top": "20px"})
                .append(tbl);

            $.ajax({
                url: copoVisualsURL,
                type: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    'task': "get_submission_datafiles",
                    'component': componentMeta.component,
                    'target_id': submission_id
                },
                success: function (data) {
                    loader.remove();

                    viewPort.append(table_div);
                    var dataSet = data.table_data.dataSet;
                    var cols = data.table_data.columns;

                    //set data
                    var table = null;

                    if ($.fn.dataTable.isDataTable('#' + tableID)) {
                        //if table instance already exists, then do refresh
                        table = $('#' + tableID).DataTable();
                    }

                    var table = $('#' + tableID).DataTable({
                        data: dataSet,
                        select: true,
                        searchHighlight: true,
                        ordering: true,
                        lengthChange: true,
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
                                filename: "copo_submission_datafiles_" + String(submission_id) + "_data"
                            }
                        ],
                        language: {
                            "info": "Showing _START_ to _END_ of _TOTAL_ records",
                            "search": " ",
                            "lengthMenu": "show _MENU_ records",
                            select: {
                                rows: {
                                    _: "%d records selected",
                                    0: "<span class='extra-table-info'>Click <span class='fa-stack' style='color:green; font-size:10px;'><i class='fa fa-circle fa-stack-2x'></i><i class='fa fa-plus fa-stack-1x fa-inverse'></i></span> beside a record for extra information</span>",
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
                        },
                        createdRow: function (row, data, index) {
                            //add class to row for ease of selection later
                            var recordId = index;
                            try {
                                recordId = data.record_id;
                            } catch (err) {
                            }

                            $(row).addClass(tableID + recordId);
                        },
                        dom: 'Bfr<"row"><"row info-rw" i>tlp',
                    });

                    table
                        .buttons()
                        .nodes()
                        .each(function (value) {
                            $(this)
                                .removeClass("btn btn-default")
                                .addClass('tiny ui button');
                        });


                    refresh_tool_tips();

                    $('#' + tableID + '_wrapper')
                        .find(".dataTables_filter")
                        .find("input")
                        .removeClass("input-sm")
                        .attr("placeholder", "Search files in submission")
                        .attr("size", 25);

                    //handle event for table details
                    $('#' + tableID + ' tbody')
                        .off('click', 'td.summary-details-control')
                        .on('click', 'td.summary-details-control', function (event) {
                            event.preventDefault();

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
                                        'component': 'datafile',
                                        'target_id': row.data().record_id
                                    },
                                    success: function (data) {
                                        if (data.component_attributes.columns) {
                                            // expand row

                                            var contentHtml = $('<table/>', {
                                                cellspacing: "0",
                                                border: "0",
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

                },
                error: function () {
                    viewPort.html('');

                    let feedback = get_alert_control();
                    feedback
                        .removeClass("alert-success")
                        .addClass("alert-danger")
                        .addClass("page-notifications-node");

                    feedback.find(".alert-message").html("Encountered an error. Please check that you are connected to a network and try again.");
                    viewPort.append(feedback);
                }
            });

        } // end of function

        //handles button events on a record or group of records
        function do_record_task(event) {
            var task = event.task.toLowerCase(); //action to be performed e.g., 'Edit', 'Delete'
            var tableID = event.tableID; //get target table


            //retrieve target records and execute task
            var table = $('#' + tableID).DataTable();
            var records = []; //
            $.map(table.rows('.selected').data(), function (item) {
                records.push(item);
            });

            if (records.length == 0) {
                return false;
            }

            if (task == "delete") {
                //will need to think this again...in terms of deletion policy
            }
            //table.rows().deselect(); //deselect all rows

        } //end of func


    }
) //end document ready


function get_viewport(submission_id) {
    return $('.submission-panel[data-id="' + submission_id + '"]').find(".pbody");
}


function submit_submission_record(submission_id) {
    //function places submit button on the panel, and processes its event

    var btn = $('<button class="ui blue big button">Submit</button>');

    btn.click(function (event) {
        event.preventDefault();

        btn.addClass("loading");
        btn.prop('disabled', true);

        $.ajax({
            url: "/rest/submit_to_repo/",
            type: "POST",
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: {
                'submission_id': submission_id
            },
            success: function (data) {
                var feedback = get_alert_control();
                feedback.removeClass("alert-success");

                // get response status
                if (data.hasOwnProperty("status")) {
                    var status = data.status.toString();

                    if (status == "success" || status == "true") {
                        feedback.addClass("alert-success");
                    } else if (status == "info") {
                        feedback.addClass("alert-info");
                    } else if (status == "error" || status == "false") {
                        feedback.addClass("alert-danger");
                    } else {
                        feedback.addClass("alert-warning");
                    }

                } else {
                    feedback.addClass("alert-warning");
                }

                //get response message
                if (data.hasOwnProperty("message")) {
                    feedback.find(".alert-message").append(data.message);
                } else {
                    feedback.find(".alert-message").append('No status message received.');
                }

                let viewPort = get_viewport(submission_id);
                viewPort
                    .html('')
                    .append(feedback);

                $('html, body').animate({
                    scrollTop: $('.submission-panel[data-id="' + submission_id + '"]').closest(".submission-panel").offset().top - 60
                }, 'slow');

                //trigger event to get status
                let controlEvent = jQuery.Event("trigger_submission_status");
                controlEvent.elementId = submission_id;
                $('body').trigger(controlEvent);
            },
            error: function (data) {
                var feedback = get_alert_control();
                feedback
                    .removeClass("alert-success")
                    .addClass("alert-danger");

                feedback.find(".alert-message").append(data.statusText + " - Error " + data.responseText);

                let viewPort = get_viewport(submission_id);
                viewPort
                    .html('')
                    .append(feedback);

                $('html, body').animate({
                    scrollTop: $('.submission-panel[data-id="' + submission_id + '"]').closest(".submission-panel").offset().top - 60
                }, 'slow');
            }
        });

    });

    var rowElement = $('<div/>', {
        class: "row"
    });


    var colElement = $('<div/>', {
        class: "col-sm-6"
    });


    rowElement
        .append(colElement);

    colElement
        .append('<hr/>')
        .append('<div class="webpop-content-div" style="margin-bottom: 10px; font-weight: bold;">Please click submit to proceed...</div>')
        .append(btn);

    return rowElement;
}

function show_submission_metadata(submission_id) {
    var tableID = 'view_existing_metadata_details';
    var tbl = $('<table/>',
        {
            id: tableID,
            "class": "ui compact definition selectable celled table",
            cellspacing: "0",
            width: "100%"
        });

    var $dialogContent = $('<div/>');
    var table_div = $('<div/>').append(tbl);
    var error_div = $('<div/>');
    var filter_message = $('<div style="margin-bottom: 20px;"><div class="text-info" style="margin-bottom: 5px;">Metadata associated with submission</div></div>');
    var spinner_div = $('<div/>', {style: "margin-left: 40%; padding-top: 15px; padding-bottom: 15px;"}).append($('<div class="copo-i-loader"></div>'));

    var dialog = new BootstrapDialog({
        type: BootstrapDialog.TYPE_PRIMARY,
        size: BootstrapDialog.SIZE_NORMAL,
        title: function () {
            return $('<span>Submission metadata</span>');
        },
        closable: false,
        animate: true,
        draggable: false,
        onhide: function (dialogRef) {
            //nothing to do for now
        },
        onshown: function (dialogRef) {
            $.ajax({
                url: '/copo/get_submission_metadata/',
                type: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    'submission_id': submission_id,
                },
                success: function (data) {
                    spinner_div.remove();

                    if (data.hasOwnProperty('status')
                        && (data.status.toString() == "success" || data.status.toString() == "true")
                        && data.hasOwnProperty("meta")) {

                        let result = data.meta;
                        let dataSet = [];

                        for (let indx in result) {
                            let item = result[indx];
                            var option = {};
                            option["label"] = item.label;
                            option["vals"] = item.vals;
                            dataSet.push(option);
                        }

                        $('#' + tableID).DataTable({
                            data: dataSet,
                            searchHighlight: true,
                            dom: 'fr<"row"><"row info-rw" i>tlp',
                            columns: [
                                {title: "Field", data: "label"},
                                {title: "Value", data: "vals"},
                            ]
                        });

                        $('#' + tableID + '_wrapper')
                            .find(".dataTables_filter")
                            .find("input")
                            .removeClass("input-sm")
                            .attr("placeholder", "Search metadata")
                            .attr("size", 15);
                    } else {
                        let feedback = get_alert_control();
                        feedback
                            .removeClass("alert-success")
                            .addClass("alert-danger");

                        var feedbackMessage = "Submission metadata found!";
                        if (data.hasOwnProperty("message") && data.message != "") {
                            feedbackMessage = data.message;
                        }

                        feedback.find(".alert-message").html(feedbackMessage);
                        error_div.append(feedback);
                        table_div = $('<div/>');
                    }

                },
                error: function () {
                    let feedback = get_alert_control();
                    feedback
                        .removeClass("alert-success")
                        .addClass("alert-danger");

                    feedback.find(".alert-message").html("Encountered an error. Please check that you are connected to a network and try again.");
                    error_div.append(feedback);
                }
            });
        },
        buttons: [
            {
                label: 'Close',
                cssClass: 'tiny ui button',
                action: function (dialogRef) {
                    dialogRef.close();
                }
            }
        ]
    });

    $dialogContent.append(filter_message).append(table_div).append(error_div).append(spinner_div);
    dialog.realize();
    dialog.setMessage($dialogContent);
    dialog.open();
}
