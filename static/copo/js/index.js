$(document).ready(function () {

    // test
    // test ends

    //******************************Event Handlers Block*************************//
    // get table data to display via the DataTables API
    var component = "profile";
    var copoFormsURL = "/copo/copo_forms/";
    var copoVisualsURL = "/copo/copo_visualize/";
    var copoDeleteProfile = "/copo/delete_profile/"
    var copoTolDashboardURL = "/copo/dashboard/tol"
    csrftoken = $.cookie('csrftoken');

    const componentMeta = get_component_meta(component);

    $(document).on("click", "#accept_reject_shortcut", function (evt) {
        document.location = "/copo/accept_reject_sample"
    })
    $(document).on("click", "#copo_tol_dashboard_shortcut", function (evt) {
        document.location = copoTolDashboardURL
    })
    $(document).on("click", ".expanding_menu > div", function (e) {
        const el = $(e.currentTarget);
        el.closest("tr").removeClass("selected")

    })
    $(document).on("click", ".item a", function (e) {
        let url;
        const el = $(e.currentTarget);
        if (el.hasClass("action")) {
            const action_type = el.data("action_type");
            let id = el.closest(".expanding_menu").attr("id");
            id = id.split("_")[1]
            if (action_type === "dtol" || action_type === "erga") {
                url = "/copo/copo_samples/" + id + "/view"
            } /*else if (action_type === "reads") {
                url = "/copo/copo_reads/" + id + "/view"
            } else if (action_type === "assembly") {
                url = "/copo/copo_assembly/" + id + "/view"
            } else if (action_type === "seq_annotation") {
                url = "/copo/copo_seq_annotation/" + id + "/view"
            } else if (action_type === "files") {
                url = "/copo/copo_files/" + id + "/view"
            } */ else {
                url = "/copo/copo_" + action_type + "/" + id + "/view"
            }
            document.location = url
        }
    })
    //load work profiles
    const tableLoader = $('<div class="copo-i-loader"></div>');
    $("#component_table_loader").append(tableLoader);
    load_profiles();
    let body = $('body')

    //trigger refresh of profiles list
    body.on('refreshtable', function (event) {
        do_render_profile_table(globalDataBuffer);
    });

    //handle task button event
    body.on('addbuttonevents', function (event) {
        do_record_task(event);
    });

    //add new profile button
    $(document).on("click", ".new-component-template", function (event) {
        initiate_form_call(component);
    });

    // //Hide 'associated_type' div label if there are no associated profile types
    // let associated_type_div_label = $('.associated_type_div_label');
    // $('.associated_type_ulTag li').length === 0 ?
    //     associated_type_div_label.text('') //.hide().css("visibility", "hidden")
    //     : associated_type_div_label.text('Associated Profile Type(s):') //.show().css("visibility", "visible");

    refresh_tool_tips();


    //******************************Functions Block******************************//


    function do_render_profile_table(data) {
        const dtd = data.table_data.dataSet;

        set_empty_component_message(dtd.length); //display empty profile message for potential first time users

        if (dtd.length === 0) {
            return false;
        }

        const tableID = componentMeta.tableID;

        const dataSet = [];

        for (let i = 0; i < dtd.length; ++i) {
            let data = dtd[i];

            //get profile id
            let record_id = '';
            let result = $.grep(data, function (e) {
                return e.key === "_id";
            });

            if (result.length) {
                record_id = result[0].data;
            }

            //get title
            let title = '';
            result = $.grep(data, function (e) {
                return e.key === "title";
            });
            if (result.length) {
                title = result[0].data;
            }

            //get type
            let type = '';
            result = $.grep(data, function (e) {
                return e.key === "type"
            });
            if (result.length) {
                type = result[0].data
            }

            //get associated type
            let associated_type = "";
            result = $.grep(data, function (e) {
                return e.key === "associated_type"
            });
            if (result.length) {
                associated_type = result[0].data
            }

            //get shared
            let shared = false;
            result = $.grep(data, function (e) {
                return e.key === "shared_profile";
            });
            if (result.length) {
                shared = result[0].data;
            }


            //get description
            let description = '';
            result = $.grep(data, function (e) {
                return e.key === "description";
            });

            if (result.length) {
                description = result[0].data;
            }

            //get date
            let profile_date = '';
            result = $.grep(data, function (e) {
                return e.key === "date_created";
            });

            if (result.length) {
                profile_date = result[0].data;
            }

            if (record_id) {
                const option = {};
                option["title"] = title;
                option["description"] = description;
                option["profile_date"] = profile_date;
                option["record_id"] = record_id;
                option["shared"] = shared
                option["type"] = type
                option["associated_type"] = associated_type
                dataSet.push(option);
            }
        }


        //set data
        let table = null;

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
                    [4, "desc"]
                ],
                columns: [
                    {
                        "data": null,
                        "orderable": false,
                        "render": function (data) {
                            const renderHTML = $(".datatables-panel-template")
                                .clone()
                                .removeClass("datatables-panel-template")
                                .addClass("copo-records-panel");


                            //set heading
                            if (data.type.includes("DTOL_ENV")) {
                                renderHTML.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
                                    ' style="">' + data.title + '&nbsp<small>(DTOL-ENV)</small></span>');
                                renderHTML.find(".panel-heading").css('background-color', "#fb7d0d")
                            } else if (data.type.includes("DTOL")) {
                                renderHTML.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
                                    ' style="">' + data.title + '&nbsp<small>(DTOL)</small></span>');
                                renderHTML.find(".panel-heading").css("background-color", "#16ab39")
                            } else if (data.type.includes("ASG")) {
                                renderHTML.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
                                    ' style="">' + data.title + '&nbsp<small>(ASG)</small></span>');
                                renderHTML.find(".panel-heading").css("background-color", "#5829bb")
                            } else if (data.type.includes("ERGA")) {
                                renderHTML.find(".panel-heading").find(".row-title").html('<span style="">' + data.title + '&nbsp<small>(ERGA)</small></span>');
                                renderHTML.find(".panel-heading").css("background-color", "#E61A8D")
                            } else {
                                if (!data.shared) {
                                    renderHTML.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
                                        ' style="font-weight: bold">' + data.title + '&nbsp<small>(Standalone)</small></span>');
                                    renderHTML.find(".panel-heading").css("background-color", "#009c95")
                                } else {
                                    renderHTML.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
                                        ' style="">' + data.title + '&nbsp<small>(Shared With Me)</small></span>');
                                    renderHTML.find(".panel-heading").css("background-color", "#f26202")
                                }
                            }

                            //set body
                            const bodyRow = $('<div class="row"></div>');

                            const menu = $("#expanding_menu").clone();
                            $(menu).attr("id", "menu_" + data.record_id)
                            let component_buttons;
                            component_buttons = append_component_buttons(data.record_id)
                            $(menu).find(".comp").append(component_buttons)

                            // Display "Associated Profile Type(s)" label only if the profile has associated types
                            let associated_type_label_div = $('<div/>',
                                {
                                    class: "associated_type_div_label"
                                });
                            data.associated_type.length !== 0
                                ? associated_type_label_div.text('Associated Profile Type(s):').show().css("visibility", "visible")
                                : associated_type_label_div.text('').hide().css("visibility", "hidden")

                            // Display associated types(s) (if any exists) as bullet points
                            let associated_type_div = $('<div/>',
                                {
                                    style: "margin-bottom:10px;"
                                });
                            associated_type_div.append(create_ul_Tag(data.associated_type))

                            const colsHTML = $('<div class="col-sm-12 col-md-12 col-lg-12"></div>')
                                .append('<div>Created:</div>')
                                .append('<div style="margin-bottom: 10px;">' + data.profile_date + '</div>')
                                .append('<div>Description:</div>')
                                .append('<div style="margin-bottom: 10px;">' + data.description + '</div>')
                                .append(associated_type_label_div)
                                .append(associated_type_div)
                                .append(menu);


                            bodyRow.append(colsHTML);
                            renderHTML.find(".panel-body").html(bodyRow);
                            renderHTML.attr("profile_type", data.type);
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
                        "data": "associated_type",
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
        filter_action_menu()
    } //end of func

    function set_selected_rows(dt) {
        const tableID = dt.table().node().id;

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
        const components = get_profile_components();
        const componentsDIV = $('<div/>', {
            class: "item"
        });


        components.forEach(function (item) {
            //skip profile entry metadata
            if (item.component === "profile") {
                return false;
            }

            let component_link = '#';

            try {
                component_link = $("#" + item.component + "_url").val().replace("999", record_id);
            } catch (err) {
                console.log(item.title);
            }

            const buttonHTML = $(".pcomponent-button").clone();
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
            const stats = data.profiles_counts;

            for (let i = 0; i < stats.length; ++i) {
                const stats_id = stats[i].profile_id + "_";
                if (stats[i].counts) {
                    for (let k in stats[i].counts) {
                        if (stats[i].counts.hasOwnProperty(k)) {
                            const count_id = stats_id + k;
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

    function filter_action_menu() {
        $(".copo-records-panel").each(function (idx, el) {
            const t = $(el).attr("profile_type");
            if (t.includes("ERGA")) {
                $(el).find("a[profile_component='stand-alone']").hide()
                //$(el).find("a[anchor_type='reads']").hide()
                //$(el).find("a[anchor_type='assembly']").hide()
                //$(el).find("a[anchor_type='annotation']").hide()
                //$(el).find("a[anchor_type='dtol_option']").hide()
            } else if (t.includes("DTOL") || t.includes("ASG")) {
                $(el).find("a[profile_component='stand-alone']").hide()
                //$(el).find("a[anchor_type='reads']").hide()
                //$(el).find("a[anchor_type='assembly']").hide()
                //$(el).find("a[anchor_type='annotation']").hide()
                //$(el).find("a[anchor_type='erga_option']").hide()
            } else if (t.includes("Stand-alone")) {
                $(el).find("a[profile_component='dtol']").hide()
                //$(el).find("a[anchor_type='dtol_option']").hide()
                //$(el).find("a[anchor_type='erga_option']").hide()
            }
        })
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
                filter_action_menu()
            },
            error: function () {
                alert("Couldn't retrieve profiles!");
            }
        });
    }

    function do_record_task(event) {
        let csrftoken;
        const task = event.task.toLowerCase(); //action to be performed e.g., 'Edit', 'Delete'
        const tableID = event.tableID; //get target table

        //retrieve target records and execute task
        const table = $('#' + tableID).DataTable();
        const records = []; //
        $.map(table.rows('.selected').data(), function (item) {
            records.push(item);
        });

        //add task
        if (task === "add") {
            initiate_form_call(component);

            return false;
        }


        //edit task
        if (task === "edit") {
            csrftoken = $.cookie('csrftoken');
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
        if (task === "validate_and_delete") {
            csrftoken = $.cookie('csrftoken');
            $.ajax({
                url: copoDeleteProfile,
                type: "POST",
                headers: {'X-CSRFToken': csrftoken},
                data: {
                    'task': 'validate_and_delete',
                    'componenent': component,
                    'target_id': records, //maybe i need to make a list of all record_id in records
                }
            }).done(function (data_response) {
                BootstrapDialog.show({
                    title: "Profile/s deleted",
                    message: "All profile/s selected have been deleted.",
                    cssClass: "copo-modal1",
                    closable: true,
                    animate: true,
                    type: BootstrapDialog.TYPE_INFO
                });
                for (let i = 0; i < records.length; i++) {
                    document.getElementById(records[i]["record_id"]).closest(".copo-records-panel").style.display = 'none';
                }
            }).error(function (data_response) {
                BootstrapDialog.show({
                    title: "Profile deletion - error",
                    message: "One or more profiles couldn't be removed. Only profiles that have no datafiles or " +
                        "samples associated can be deleted.",
                    cssClass: "copo-modal1",
                    closable: true,
                    animate: true,
                    type: BootstrapDialog.TYPE_DANGER
                });
                for (let i = 0; i < records.length; i++) {
                    if (!data_response.responseJSON["undeleted"].includes(records[i]["record_id"])) {
                        document.getElementById(records[i]["record_id"]).closest(".copo-records-panel").style.display = 'none';
                    }
                }
                console.log(data_response)
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

    // Show "accept_reject_samples" button
    for (let g in groups) {
        if (groups[g].includes("sample_managers")) {
            $("#accept_reject_shortcut").show()
            break;
        }
    }

    // Show "tol_dashboard" button
    for (let g in groups) {
        if (groups[g].includes("sample_managers") || groups[g].includes("_users")) {
            $("#copo_tol_dashboard_shortcut").show()
            break;
        }
    }


    function create_ul_Tag(array) {
        let acronym;
        const regExp = /\(([^\)]*)\)/ // parentheses regex to get enclosed string

        // Create the ul tag element:
        const ul = document.createElement('ul');
        ul.setAttribute('class', "associated_type_ulTag");

        // Set 'ul' tag to 3 columns if the number of 'li' elements is more than or equal to 4
        //  If not, set it to 1 column
        if (array.length >= 4) {
            ul.style.columnCount = "3";
            ul.style.width = "500px";
        } else {
            ul.style.columnCount = "1";
            ul.style.width = "0px";
        }

        for (let i = 0; i < array.length; i++) {
            // Check if item contains parentheses that include a string
            // Get acronym from enclosed parentheses
            // If there are parentheses, retrieve the entire string
            acronym = (array[i]).match(regExp) !== null ? (array[i]).match(regExp).pop() : array[i];
            // If empty parentheses are returned, set the acronym as the full string excluding the parentheses
            acronym = acronym === '()' ? array[i].replace(/\(\s*\)/g, "") : acronym

            // Create the list item:
            const li = document.createElement('li');

            // Set title to list item
            li.setAttribute('title', array[i]);

            // Set its contents
            li.appendChild(document.createTextNode(acronym));

            // Add item to the list
            ul.appendChild(li);
        }

        return ul;
    }

}) //end document ready
