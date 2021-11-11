$(document).ready(function () {

    // test
    // test ends

    //******************************Event Handlers Block*************************//
    // get table data to display via the DataTables API
    var component = "profile";
    var copoFormsURL = "/copo/copo_forms/";
    var copoVisualsURL = "/copo/copo_visualize/";
    csrftoken = $.cookie('csrftoken');

    var componentMeta = get_component_meta(component);


    //load work profiles
    var tableLoader = $('<div class="copo-i-loader"></div>');
    $("#component_table_loader").append(tableLoader);
    load_profiles();


    //trigger refresh of profiles list
    $('body').on('refreshtable', function (event) {
        do_render_profile_table(globalDataBuffer);
    });

    //handle task button event
    $('body').on('addbuttonevents', function (event) {
        do_record_task(event);
    });

    //add new profile button
    $(document).on("click", ".new-component-template", function (event) {
        initiate_form_call(component);
    });

    refresh_tool_tips();


    //******************************Functions Block******************************//


    function do_render_profile_table(data) {
        var dtd = data.table_data.dataSet;

        set_empty_component_message(dtd.length); //display empty profile message for potential first time users

        if (dtd.length == 0) {
            return false;
        }

        var tableID = componentMeta.tableID;

        var dataSet = [];

        for (var i = 0; i < dtd.length; ++i) {
            var data = dtd[i];

            //get profile id
            var record_id = '';
            var result = $.grep(data, function (e) {
                return e.key == "_id";
            });

            if (result.length) {
                record_id = result[0].data;
            }

            //get title
            var title = '';
            result = $.grep(data, function (e) {
                return e.key == "title";
            });
            if (result.length) {
                title = result[0].data;
            }

            //get type
            var type = '';
            result = $.grep(data, function (e) {
                return e.key == "type"
            });
            if (result.length) {
                type = result[0].data
            }

            //get shared
            var shared = false
            result = $.grep(data, function (e) {
                return e.key == "shared_profile";
            });
            if (result.length) {
                shared = result[0].data;
            }


            //get description
            var description = '';
            result = $.grep(data, function (e) {
                return e.key == "description";
            });

            if (result.length) {
                description = result[0].data;
            }

            //get date
            var profile_date = '';
            result = $.grep(data, function (e) {
                return e.key == "date_created";
            });

            if (result.length) {
                profile_date = result[0].data;
            }

            if (record_id) {
                var option = {};
                option["title"] = title;
                option["description"] = description;
                option["profile_date"] = profile_date;
                option["record_id"] = record_id;
                option["shared"] = shared
                option["type"] = type
                dataSet.push(option);
            }
        }


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
                lengthChange: true,
                buttons: [
                    'selectAll',
                    'selectNone'
                ],
                select: {
                    style: 'multi', //os, multi, api
                    items: 'row' //row, cell, column
                },
                language: {
                    //"info": "Showing _START_ to _END_ of _TOTAL_ profiles",
                    "search": " ",
                    //"lengthMenu": "show _MENU_ records",
                    "emptyTable": "No work profiles available! Use the 'New Profile' button to create work profiles.",
                    buttons: {
                        selectAll: "Select all",
                        selectNone: "Select none",
                    }
                },
                order: [
                    [2, "desc"]
                ],
                columns: [
                    {
                        "data": null,
                        "orderable": false,
                        "render": function (data) {
                            var renderHTML = $(".datatables-panel-template")
                                .clone()
                                .removeClass("datatables-panel-template")
                                .addClass("copo-records-panel");

                            //set heading
                            if (data.type.includes("DTOL_EI")) {
                                renderHTML.find(".panel-heading").find(".row-title").html('<span style="">' + data.title + '&nbsp<small>(DTOL-EI)</small></span>');
                                renderHTML.find(".panel-heading").css('background-color', "#16ab39")
                            } else if (data.type.includes("DTOL")) {
                                renderHTML.find(".panel-heading").find(".row-title").html('<span style="">' + data.title + '&nbsp<small>(DTOL)</small></span>');
                                renderHTML.find(".panel-heading").css("background-color", "#16ab39")
                            } else if (data.type.includes("ASG")) {
                                renderHTML.find(".panel-heading").find(".row-title").html('<span style="">' + data.title + '&nbsp<small>(ASG)</small></span>');
                                renderHTML.find(".panel-heading").css("background-color", "#5829bb")
                            } else {
                                if (!data.shared) {
                                    renderHTML.find(".panel-heading").find(".row-title").html('<span style="font-weight: bolder">' + data.title + '&nbsp<small>(Standalone)</small></span>');
                                    renderHTML.find(".panel-heading").css("background-color", "#009c95")
                                } else {
                                    renderHTML.find(".panel-heading").find(".row-title").html('<span style="">' + data.title + '&nbsp<small>(Shared With Me)</small></span>');
                                    renderHTML.find(".panel-heading").css("background-color", "#f26202")
                                }
                            }
                            //set body
                            var bodyRow = $('<div class="row"></div>');

                            var colsHTML = $('<div class="col-sm-12 col-md-12 col-lg-12"></div>')
                                .append('<div>Created:</div>')
                                .append('<div style="margin-bottom: 10px;">' + data.profile_date + '</div>')
                                .append('<div>Description:</div>')
                                .append('<div style="margin-bottom: 10px;">' + data.description + '</div>')
                                .append(append_component_buttons(data.record_id));


                            bodyRow.append(colsHTML);
                            renderHTML.find(".panel-body").html(bodyRow);

                            return $('<div/>').append(renderHTML).html();
                        }
                    },
                    {
                        "data": "title",
                        "title": "Title",
                        "visible": false
                    },
                    {
                        "data": "profile_date",
                        "title": "Created",
                        "visible": false
                    },
                    {
                        "data": "description",
                        "visible": false
                    },
                    {
                        "data": "record_id",
                        "visible": false
                    },
                    {
                        "data": "shared",
                        "visible": false
                    }
                ],
                "columnDefs": [],
                fnDrawCallback: function () {
                    refresh_tool_tips();
                    update_counts(); //updates profile component counts
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

            place_task_buttons(componentMeta); //this will place custom buttons on the table for executing tasks on records
        }

        $('#' + tableID + '_wrapper')
            .find(".dataTables_filter")
            .find("input")
            .removeClass("input-sm")
            .attr("placeholder", "Search Work Profiles")
            .attr("size", 30);


        if (table) {
            table.on('select', function (e, dt, type, indexes) {
                set_selected_rows(dt);
            });

            table.on('deselect', function (e, dt, type, indexes) {
                set_selected_rows(dt);
            });
        }

    } //end of func

    function set_selected_rows(dt) {
        var tableID = dt.table().node().id;

        $('#' + tableID + ' tbody').find('tr').each(function () {
            $(this).find(".panel:first").find(".row-select-icon").children('i').eq(0).removeClass("fa fa-check-square-o");
            // $(this).find(".copo-records-panel").children('.panel').eq(0).removeClass("panel-primary");

            $(this).find(".panel:first").find(".row-select-icon").children('i').eq(0).addClass("fa fa-square-o");
            // $(this).find(".copo-records-panel").children('.panel').eq(0).addClass("panel-default");

            if ($(this).hasClass('selected')) {
                $(this).find(".panel:first").find(".row-select-icon").children('i').eq(0).removeClass("fa fa-square-o");
                // $(this).find(".copo-records-panel").children('.panel').eq(0).removeClass("panel-default");

                $(this).find(".panel:first").find(".row-select-icon").children('i').eq(0).addClass("fa fa-check-square-o");
                // $(this).find(".copo-records-panel").children('.panel').eq(0).addClass("panel-primary");
            }
        });
    }

    function append_component_buttons(record_id) {
        //components row
        var components = get_profile_components();
        var componentsDIV = $('<div/>', {
            class: "pull-right",
            style: "margin-top:15px;"
        });


        components.forEach(function (item) {
            //skip profile entry metadata
            if (item.component == "profile") {
                return false;
            }

            var component_link = '#';

            try {
                component_link = $("#" + item.component + "_url").val().replace("999", record_id);
            } catch (err) {
                console.log(item.title);
            }

            var buttonHTML = $(".pcomponent-button").clone();
            buttonHTML.attr("title", "Navigate to " + item.title);
            buttonHTML.attr("href", component_link);
            buttonHTML.find(".pcomponent-icon").addClass(item.iconClass);
            buttonHTML.find(".pcomponent-name").html(item.title);
            buttonHTML.find(".pcomponent-color").addClass(item.color);
            buttonHTML.find(".pcomponent-count").attr("id", record_id + "_" + item.countsKey);

            componentsDIV.append(buttonHTML);
        });

        return componentsDIV;
    }

    function do_render_profile_counts(data) {
        if (data.profiles_counts) {
            var stats = data.profiles_counts;

            for (var i = 0; i < stats.length; ++i) {
                var stats_id = stats[i].profile_id + "_";
                if (stats[i].counts) {
                    for (var k in stats[i].counts) {
                        if (stats[i].counts.hasOwnProperty(k)) {
                            var count_id = stats_id + k;
                            $("#" + count_id).html(stats[i].counts[k]);
                        }
                    }
                }
            }
        }
    }

    function update_counts() {
        console.log()
        $.ajax({
            url: copoVisualsURL,
            type: "POST",
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: {
                'task': 'profiles_counts',
                'component': component
            },
            success: function (data) {
                do_render_profile_counts(data);
            },
            error: function () {
                alert("Couldn't retrieve profiles information!");
            }
        });
    }

    function load_profiles() {
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
                do_render_profile_table(data);
                tableLoader.remove();
            },
            error: function () {
                alert("Couldn't retrieve profiles!");
            }
        });
    }

    function do_record_task(event) {
        var task = event.task.toLowerCase(); //action to be performed e.g., 'Edit', 'Delete'
        var tableID = event.tableID; //get target table

        //retrieve target records and execute task
        var table = $('#' + tableID).DataTable();
        var records = []; //
        $.map(table.rows('.selected').data(), function (item) {
            records.push(item);
        });

        //add task
        if (task == "add") {
            initiate_form_call(component);
            return false;
        }


        //edit task
        if (task == "edit") {
            $.ajax({
                url: copoFormsURL,
                type: "POST",
                headers: {'X-CSRFToken': csrftoken},
                data: {
                    'task': 'form',
                    'component': component,
                    'target_id': records[0].record_id //only allowing row action for edit, hence first record taken as target
                },
                success: function (data) {
                    json2HtmlForm(data);
                },
                error: function () {
                    alert("Couldn't build profile form!");
                }
            });
        }

        //delete task
        if (task == "validate_and_delete") {
            //alert("coming soon")
            $.ajax({
                url: copoFormsURL,
                type: "POST",
                headers: {'X-CSRFToken': csrftoken},
                data: {
                    'task': 'validate_and_delete',
                    'componenent': component,
                    'target_id': records, //maybe i need to make a list of all record_id in records
                },
                success: function (data) {
                    alert("removed");
                },
                error: function f() {
                    alert("something not working")
                }
            });
        }

        //table.rows().deselect(); //deselect all rows

        //handle button actions
        // if (ids.length > 0) {
        //     if (task == "edit") {
        //         $.ajax({
        //             url: copoFormsURL,
        //             type: "POST",
        //             headers: {'X-CSRFToken': csrftoken},
        //             data: {
        //                 'task': 'form',
        //                 'component': component,
        //                 'target_id': ids[0] //only allowing row action for edit, hence first record taken as target
        //             },
        //             success: function (data) {
        //                 json2HtmlForm(data);
        //             },
        //             error: function () {
        //                 alert("Couldn't build publication form!");
        //             }
        //         });
        //     } else if (task == "delete") { //handles delete, allows multiple row delete
        //         var deleteParams = {component: component, target_ids: ids};
        //         do_component_delete_confirmation(deleteParams);
        //     }
        // }
    }


}) //end document ready
