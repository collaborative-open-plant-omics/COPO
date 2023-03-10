$(document).ready(function () {
    //****************************** Event handlers block *************************//
    $(document).data("sort_method", "ASC")

    // Get data to display
    const component = "profile";
    const componentMeta = get_component_meta(component);
    const copoFormsURL = "/copo/copo_forms/";
    const copoVisualsURL = "/copo/copo_visualize/";
    const copoDeleteProfile = "/copo/delete_profile/";
    const copoProfileIndexURL = "/copo/";
    const copoAcceptRejectURL = "/copo/accept_reject_sample"
    const copoSamplesURL = "/copo/copo_samples/"
    const copoENAReadManifestValidateURL = "/copo/ena_read_manifest_validate/"
    const copoENAAssemblyURL = "/copo/ena_assembly/"
    const tableLoader = $('<div class="copo-i-loader"></div>');
    let body = $('body')
    let page = 1;
    let block_request = false;
    let end_pagination = false;
    let grid_count = $('#grid-count');
    let grid_total = $('#grid-total');

    csrftoken = $.cookie('csrftoken');

    // Load work profiles
    // If there are no profiles, display an empty profile message else show loader
    if (profiles.length === 0) {
        console.log('No records to show')
    } else {
        $("#component_table_loader").append(tableLoader);
        tableLoader.remove();
    }

    set_empty_component_message(profiles_total); // Display an empty profile message for potential first time users
    //load_profiles(copoVisualsURL, csrftoken, component, componentMeta, tableLoader);
    grid_count.text(profiles.length); // Number of profile records visible
    grid_total.text(profiles_total); //  Total number of profile records for the user

    // Trigger refresh of profiles list
    body.on('refreshtable', function () {
        // set_empty_component_message(profiles_total); // Display an empty profile message for potential first time users
        // grid_count.text(profiles.length); // Number of profile records visible
        // grid_total.text(profiles_total); //  Total number of profile records for the user
        tableLoader.remove();

        //do_render_profile_table(globalDataBuffer);
    });

    //handle task button event
    body.on('addbuttonevents', function (event) {
        do_record_task(event, component, copoDeleteProfile, copoFormsURL);
    });

    // Groups
    for (let g in groups) {
        if (groups[g].includes("sample_managers")) {
            $("#accept_reject_shortcut").show()
            break;
        }
    }

    // Show popover option to edit/delete a profile record once it has been selected
    $('.vertical-ellipsis > i').webuiPopover({
        //title: 'Edit',
        content: function () {
            return '\
                    <div>\
                        <button id="editProfileRecord" type="button" class="btn btn-sm btn-success"><i class="fa fa-pencil-square-o"></i>&nbsp;Edit</button>\
                        &emsp;\
                        <button  id="deleteProfileRecord"  type="button" class="btn btn-sm btn-danger"><i class="fa fa-trash-o"></i>&nbsp;Delete</button>\
                    </div>\
                    ';
        },
        width: 220,
        placement: 'right',
        animation: 'pop',
        dismissible: true,
        closeable: true, //display close button or not
        onShow: function ($element) {
            set_selected_profile_record($element)

        },
    });

    $(document).on("click", "#accept_reject_shortcut", function () {
        document.location = copoAcceptRejectURL
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
                url = copoSamplesURL + id + "/view"
            } else if (action_type === "reads") {
                url = copoENAReadManifestValidateURL + id
            } else if (action_type === "assembly") {
                url = copoENAAssemblyURL + id
            }
            document.location = url
        }
    })

    // Toggle the visibility of the button to sort in
    // ascending order and descending order
    // $(".dropdown-toggle").val("Date Created").change();
    $(document).on("click", "#sortIconID", function (e) {
        $(this).toggleClass("fa fa-sort-up")
        $(this).toggleClass("fa fa-sort-down")

        // Configure the 'padding-top' CSS style and set sort method
        if ($(this).hasClass("fa fa-sort-up")) {
            $(this).css('padding-top', '12px')
            $(document).data("sort_method", "ASC")
        } else {
            $(this).css('padding-top', '5px');
            $(document).data("sort_method", "DSC")
        }
        console.log('Sorting by', $(document).data("sort_method"))
        e.preventDefault();
    });

    $('.dropdown-sort').on('click', '.dropdown-menu li a', function () {
        console.log('I have been clicked')
        const target = $(this).html();

        //Adds active class to selected item
        $(this).parents('.dropdown-menu').find('li').removeClass('active');
        $(this).parent('li').addClass('active');

        //Displays selected text on dropdown-toggle button
        $(this).parents('.dropdown-sort').find('.dropdown-toggle').html(target + ' <span class="caret"></span>');
    });


    // Add new profile button
    $(document).on("click", ".new-component-template", function () {
        initiate_form_call(component);
    });

    // Edit profile button
    $(document).on("click", "#editProfileRecord", function (event) {
        console.log(event.task.toLowerCase());
        // do_record_task(event, component, copoDeleteProfile, copoFormsURL);
    });

    // Delete profile button
    $(document).on("click", "#deleteProfileRecord", function (event) {
        console.log(event.task.toLowerCase());
        // do_record_task(event, component, copoDeleteProfile, copoFormsURL);
    });

    // Show the option to edit/delete a profile record
    // once the vertical ellipsis is clicked

    // Profiles - Trigger infinite scroll once user scrolls downwards and display more profile records
    $(window).scroll(function () {
        const margin = $(document).height() - $(window).height() - 200;
        // Scroll downwards
        if ($(window).scrollTop() > margin && end_pagination === false && block_request === false) {
            block_request = true;
            page += 1;

            $.ajax({
                type: 'GET',
                url: copoProfileIndexURL,
                data: {
                    "page": page
                },
                success: function (data) {
                    if (data.end_pagination === true) {
                        end_pagination = true;
                    } else {
                        block_request = false;
                    }
                    // Appends the html template from the 'copo_profile_record.html' to the 'copo_profiels_table' div
                    $('#copo_profiles_table').append(data.content);

                    // Increment the number profile records displayed
                    grid_count.text($('.grid').length)
                    // tableLoader.remove();
                },
                error: function () {
                    alert("Couldn't retrieve profiles!");
                }
            })
        }

    });
}); // End document ready

//****************************** Functions Block ******************************//
function createProfileGrid(data) {
    // <div className="item">
    //     <a href="${'https://www.imdb.com/title/' + data.imdbID}" className="item__link" target="_blank">
    //         <div className="item__img"><img className="item__img__img" src="${data.Poster}"
    //                                         onError="this.src='https://placehold.co/185x278'" width="185" height="278"/>
    //         </div>
    //         <h1 className="item__title">${data.Title}</h1>
    //         <div className="item__year">${data.Year}</div>
    //         <div className="item__rating" title="IMDB Rating">${data.imdbRating}</div>
    //     </a>
    // </div>
    const template = `<div class="grid" style="background-color: rgb(255, 255, 255);">
      <div class="copo-records-panel" profile_type="${data.type}">
          <div class="panel">
              <div class="panel-heading" style="background-color: rgb(230, 26, 141);">
                  <div class="row">
                      <div class="col-sm-10 col-md-10 col-lg-10 row-title">
                        <span style="">${data.title}&nbsp;<small>(ERGA)</small></span>
                      </div>
                      <div class="col-sm-2 col-md-2 col-lg-2 row-ellipsis">
                              <div id="${data.record_id}" class="pull-right vertical-ellipsis" title="View profile options">
                                <i class="fa fa-ellipsis-v" style="font-size:14px"></i>
                              </div>
                      </div>
                  </div>
              </div>
              <div class="panel-body">
                <div class="row">
                    <div class="col-sm-12 col-md-12 col-lg-12">
                      <div>Created:</div>
                      <div style="margin-bottom: 10px;">${data.profile_date}</div>
                      <div>Description:</div>
                      <div style="margin-bottom: 10px;">${data.description}</div>
                     <!--  ${data.associated_type} != ""
                       ?-->
                      <div class="associated_type_div_label" style="display: block; visibility: visible;">Associated Profile Type(s):</div>
                      <div style="margin-bottom:20px;">
                          <ul class="associated_type_ulTag" style="column-count: 1; width: 200px;">
                              <li title="Aquatic Symbiosis Genomics (ASG)">ASG</li>
                              <li title="Darwin Tree of Life Environmental Samples (DTOL_ENV)">DTOL_ENV</li>
                              <li title="European Reference Genome Atlas - Pilot (ERGA_PILOT)">ERGA_PILOT</li>
                          </ul>
                      </div>
                     <!-- : <div></div>-->
                      <span class="ui vertical menu expanding_menu" id="menu_63f4920c45cab8fe877feb56">
                            <div class="ui left pointing dropdown link item" tabindex="0">
                                Actions
                                <i class="dropdown icon"></i>
                                <div class="menu" tabindex="-1">
                                    <a class="item action" anchor_type="reads" data-action_type="reads">Submit Reads</a>
                                    <a class="item action" anchor_type="assembly" data-action_type="assembly">Submit Assembly</a>
                                    <a class="item action" anchor_type="dtol_option" data-action_type="dtol">Submit DTOL/ASG manifest</a>
                                    <a class="item action" anchor_type="erga_option" data-action_type="erga">Submit ERGA Manifest</a>
                                </div>
                            </div>
                            <div class="ui left pointing dropdown link item" tabindex="0">
                                Components
                                <i class="dropdown icon"></i>
                                <div class="menu comp" tabindex="-1">
                    
                                    <div class="item">
                                        <a class="tiny ui labeled button pcomponent-button" tabindex="0" style="margin: 3px;" title="Navigate to Samples" href="/copo/copo_samples/63f4920c45cab8fe877feb56/view">
                                            <div class="tiny ui button pcomponent-color olive">
                                                <i class="pcomponent-icon  fa fa-filter"></i>
                                                <span class="pcomponent-name" style="padding-left: 3px;">Samples</span>
                                            </div>
                                            <div class="tiny ui basic pcomponent-color left pointing label olive">
                                                <span class="pcomponent-count" id="63f4920c45cab8fe877feb56_num_sample"><i class="fa fa-spinner fa-pulse" style="font-size: 10px;"></i></span>
                                            </div>
                                        </a>
                                        <a class="tiny ui labeled button pcomponent-button" tabindex="0" style="margin: 3px;" title="Navigate to Datafiles" href="/copo/copo_data/63f4920c45cab8fe877feb56/view">
                                            <div class="tiny ui button pcomponent-color black">
                                                <i class="pcomponent-icon  fa fa-database"></i>
                                                <span class="pcomponent-name" style="padding-left: 3px;">Datafiles</span>
                                            </div>
                                            <div class="tiny ui basic pcomponent-color left pointing label black">
                                                <span class="pcomponent-count" id="63f4920c45cab8fe877feb56_num_data"><i class="fa fa-spinner fa-pulse" style="font-size: 10px;"></i></span>
                                            </div>
                                        </a>
                                        <a class="tiny ui labeled button pcomponent-button" tabindex="0" style="margin: 3px;" title="Navigate to Submissions" href="/copo/copo_submissions/63f4920c45cab8fe877feb56/view">
                                            <div class="tiny ui button pcomponent-color green">
                                                <i class="pcomponent-icon  fa fa-envelope"></i>
                                                <span class="pcomponent-name" style="padding-left: 3px;">Submissions</span>
                                            </div>
                                            <div class="tiny ui basic pcomponent-color left pointing label green">
                                                <span class="pcomponent-count" id="63f4920c45cab8fe877feb56_num_submission"><i class="fa fa-spinner fa-pulse" style="font-size: 10px;"></i></span>
                                            </div>
                                        </a>
                                        <a class="tiny ui labeled button pcomponent-button" tabindex="0" style="margin: 3px;" title="Navigate to Publications" href="/copo/copo_publications/63f4920c45cab8fe877feb56/view">
                                            <div class="tiny ui button pcomponent-color orange">
                                                <i class="pcomponent-icon  fa fa-paperclip"></i>
                                                <span class="pcomponent-name" style="padding-left: 3px;">Publications</span>
                                            </div>
                                            <div class="tiny ui basic pcomponent-color left pointing label orange">
                                                <span class="pcomponent-count" id="63f4920c45cab8fe877feb56_num_pub"><i class="fa fa-spinner fa-pulse" style="font-size: 10px;"></i></span>
                                            </div>
                                        </a>
                                        <a class="tiny ui labeled button pcomponent-button" tabindex="0" style="margin: 3px;" title="Navigate to Metadata Template" href="/copo/view_templates/63f4920c45cab8fe877feb56/view">
                                            <div class="tiny ui button pcomponent-color blue">
                                                <i class="pcomponent-icon  fa fa-table"></i>
                                                <span class="pcomponent-name" style="padding-left: 3px;">Metadata Template</span>
                                            </div>
                                            <div class="tiny ui basic pcomponent-color left pointing label blue">
                                                <span class="pcomponent-count" id="63f4920c45cab8fe877feb56_num_temp"><i class="fa fa-spinner fa-pulse" style="font-size: 10px;"></i></span>
                                            </div>
                                        </a>
                                        <a class="tiny ui labeled button pcomponent-button" tabindex="0" style="margin: 3px;" title="Navigate to People" href="/copo/copo_people/63f4920c45cab8fe877feb56/view">
                                            <div class="tiny ui button pcomponent-color red">
                                                <i class="pcomponent-icon  fa fa-users"></i>
                                                <span class="pcomponent-name" style="padding-left: 3px;">People</span>
                                            </div>
                                            <div class="tiny ui basic pcomponent-color left pointing label red">
                                                <span class="pcomponent-count" id="63f4920c45cab8fe877feb56_num_person"><i class="fa fa-spinner fa-pulse" style="font-size: 10px;"></i></span>
                                            </div>
                                        </a>
                                    </div>
                                </div>
                            </div>
                      </span>
                    </div>
                </div>
              </div>
          </div>
      </div>
  </div>
  `;

    let item = document.createElement('div');
    item.innerHTML = template.trim();

    return item.firstChild;
}

function set_profile_panel_layout(data, grid, tableID_div, copo_records_panel, panel, panel_heading, panel_heading_row, panel_heading_titleDiv, panel_heading_ellipsisDiv, panel_body, panel_body_row) {
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

    // Style the layout of actions/components button if no associated type is exists
    let colsHTML_div = '<div class="col-sm-12 col-md-12 col-lg-12"></div>'
    let descriptionDiv_content = '<div style="margin-bottom: 10px;">' + data.description + '</div>'
    let associatedTypeContentDiv_style = "margin-bottom:10px;";

    if (data.associated_type.length === 0) {
        colsHTML_div = '<div class="col-sm-12 col-md-12 col-lg-12" style="margin-top:30px"></div>'
        descriptionDiv_content = '<div style="margin-bottom: 90px;">' + data.description + '</div>'
        // associatedTypeContentDiv_style = "margin-bottom:10px;";
    } else if (data.associated_type.length === 1) {
        associatedTypeContentDiv_style = "margin-bottom:70px;";
    } else if (data.associated_type.length === 2) {
        associatedTypeContentDiv_style = "margin-bottom:45px;";
    } else {
        associatedTypeContentDiv_style = "margin-bottom:20px;";
    }

    // Display associated types(s) (if any exists) as bullet points
    let associated_type_div = $('<div/>',
        {
            style: associatedTypeContentDiv_style
        });

    associated_type_div.append(create_ul_Tag(data.associated_type))

    const colsHTML = $(colsHTML_div)
        .append('<div>Created:</div>')
        .append('<div style="margin-bottom: 10px;">' + data.profile_date + '</div>')
        .append('<div>Description:</div>')
        .append(descriptionDiv_content)
        .append(associated_type_label_div)
        .append(associated_type_div)
        .append(menu);

    // Append the html created to the profile_table_div
    panel_heading_row.append(panel_heading_titleDiv)
    panel_heading_row.append(panel_heading_ellipsisDiv)
    panel_heading.append(panel_heading_row)
    panel.append(panel_heading)

    panel_body_row.append(colsHTML);
    panel_body.html(panel_body_row);
    panel.append(panel_body)

    copo_records_panel.append(panel)
    grid.append(copo_records_panel)
    copo_records_panel.attr("profile_type", data.type)
}

function do_render_profile_table(data, copoVisualsURL, csrftoken, component, componentMeta) {
    const tableID = componentMeta.tableID;
    const dtd = data.table_data.dataSet;

    set_empty_component_message(dtd.length); //display empty profile message for potential first time users

    if (dtd.length === 0) return false;

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

    // Set data

    // place_task_buttons(componentMeta); //this will place custom buttons on the table for executing tasks on records
    // if (table) {
    //     table.on('select', function (e, dt, type, indexes) {
    //         set_selected_rows(dt);
    //     });
    //
    //     table.on('deselect', function (e, dt, type, indexes) {
    //         set_selected_rows(dt);
    //     });
    // }
    // filter_action_menu()


    // generate_profile_records_grid3(dataSet, tableID)
    update_counts(copoVisualsURL, csrftoken, component); //updates profile component counts
    return $('<div/>').append('<div/>').html();  // This enables the html to be displayed


    // //Using tables way
    // let table = null;
    // if ($.fn.dataTable.isDataTable('#' + tableID)) {
    //     //if table instance already exists, then do refresh
    //     table = $('#' + tableID).DataTable();
    // }
    //
    // if (table) {
    //     //clear old, set new data
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
    //     table = $('#' + tableID).DataTable({
    //         data: dataSet,
    //         searchHighlight: true,
    //         ordering: true,
    //         lengthChange: true,
    //         buttons: [
    //             'selectAll',
    //             'selectNone'
    //         ],
    //         select: {
    //             style: 'multi', //os, multi, api
    //             items: 'row' //row, cell, column
    //         },
    //         language: {
    //             //"info": "Showing _START_ to _END_ of _TOTAL_ profiles",
    //             "search": " ",
    //             //"lengthMenu": "show _MENU_ records",
    //             "emptyTable": "No work profiles available! Use the 'New Profile' button to create work profiles.",
    //             buttons: {
    //                 selectAll: "Select all",
    //                 selectNone: "Select none",
    //             }
    //         },
    //         order: [
    //             [4, "desc"]
    //         ],
    //         columns: [
    //             {
    //                 "data": null,
    //                 "orderable": false,
    //                 "render": function (data) {
    //                     const renderHTML = $(".datatables-panel-template")
    //                         .clone()
    //                         .removeClass("datatables-panel-template")
    //                         .addClass("copo-records-panel");
    //
    //
    //                     //set heading
    //                     if (data.type.includes("DTOL_ENV")) {
    //                         renderHTML.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
    //                             ' style="">' + data.title + '&nbsp<small>(DTOL-ENV)</small></span>');
    //                         renderHTML.find(".panel-heading").css('background-color', "#fb7d0d")
    //                     } else if (data.type.includes("DTOL")) {
    //                         renderHTML.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
    //                             ' style="">' + data.title + '&nbsp<small>(DTOL)</small></span>');
    //                         renderHTML.find(".panel-heading").css("background-color", "#16ab39")
    //                     } else if (data.type.includes("ASG")) {
    //                         renderHTML.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
    //                             ' style="">' + data.title + '&nbsp<small>(ASG)</small></span>');
    //                         renderHTML.find(".panel-heading").css("background-color", "#5829bb")
    //                     } else if (data.type.includes("ERGA")) {
    //                         renderHTML.find(".panel-heading").find(".row-title").html('<span style="">' + data.title + '&nbsp<small>(ERGA)</small></span>');
    //                         renderHTML.find(".panel-heading").css("background-color", "#E61A8D")
    //                     } else {
    //                         if (!data.shared) {
    //                             renderHTML.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
    //                                 ' style="font-weight: bold">' + data.title + '&nbsp<small>(Standalone)</small></span>');
    //                             renderHTML.find(".panel-heading").css("background-color", "#009c95")
    //                         } else {
    //                             renderHTML.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
    //                                 ' style="">' + data.title + '&nbsp<small>(Shared With Me)</small></span>');
    //                             renderHTML.find(".panel-heading").css("background-color", "#f26202")
    //                         }
    //                     }
    //
    //                     //set body
    //                     const bodyRow = $('<div class="row"></div>');
    //
    //                     const menu = $("#expanding_menu").clone();
    //                     $(menu).attr("id", "menu_" + data.record_id)
    //                     let component_buttons;
    //                     component_buttons = append_component_buttons(data.record_id)
    //                     $(menu).find(".comp").append(component_buttons)
    //
    //                     // Display "Associated Profile Type(s)" label only if the profile has associated types
    //                     let associated_type_label_div = $('<div/>',
    //                         {
    //                             class: "associated_type_div_label"
    //                         });
    //                     data.associated_type.length !== 0
    //                         ? associated_type_label_div.text('Associated Profile Type(s):').show().css("visibility", "visible")
    //                         : associated_type_label_div.text('').hide().css("visibility", "hidden")
    //
    //                     // Display associated types(s) (if any exists) as bullet points
    //                     let associated_type_div = $('<div/>',
    //                         {
    //                             style: "margin-bottom:10px;"
    //                         });
    //                     associated_type_div.append(create_ul_Tag(data.associated_type))
    //
    //                     const colsHTML = $('<div class="col-sm-12 col-md-12 col-lg-12"></div>')
    //                         .append('<div>Created:</div>')
    //                         .append('<div style="margin-bottom: 10px;">' + data.profile_date + '</div>')
    //                         .append('<div>Description:</div>')
    //                         .append('<div style="margin-bottom: 10px;">' + data.description + '</div>')
    //                         .append(associated_type_label_div)
    //                         .append(associated_type_div)
    //                         .append(menu);
    //
    //
    //                     bodyRow.append(colsHTML);
    //                     panel_body.html(bodyRow);
    //                     renderHTML.attr("profile_type", data.type);
    //                     return $('<div/>').append(renderHTML).html();
    //                 }
    //             },
    //             {
    //                 "data": "title",
    //                 "title": "Title",
    //                 "visible": false
    //             },
    //             {
    //                 "data": "profile_date",
    //                 "title": "Created",
    //                 "visible": false
    //             },
    //             {
    //                 "data": "description",
    //                 "visible": false
    //             },
    //             {
    //                 "data": "associated_type",
    //                 "visible": false
    //             },
    //             {
    //                 "data": "record_id",
    //                 "visible": false
    //             },
    //             {
    //                 "data": "shared",
    //                 "visible": false
    //             }
    //         ],
    //         "columnDefs": [],
    //         fnDrawCallback: function () {
    //             refresh_tool_tips();
    //             update_counts(); //updates profile component counts
    //         },
    //         dom: 'Bfr<"row"><"row info-rw" i>tlp',
    //     });
    //
    //     table
    //         .buttons()
    //         .nodes()
    //         .each(function (value) {
    //             $(this)
    //                 .removeClass("btn btn-default")
    //                 .addClass('tiny ui basic button');
    //         });
    //
    //     place_task_buttons(componentMeta); //this will place custom buttons on the table for executing tasks on records
    //
    //
    // }
    //
    // $('#' + tableID + '_wrapper')
    //     .find(".dataTables_filter")
    //     .find("input")
    //     .removeClass("input-sm")
    //     .attr("placeholder", "Search Work Profiles")
    //     .attr("size", 30);
    //
    //
    // if (table) {
    //     table.on('select', function (e, dt, type, indexes) {
    //         set_selected_rows(dt);
    //     });
    //
    //     table.on('deselect', function (e, dt, type, indexes) {
    //         set_selected_rows(dt);
    //     });
    // }
    // filter_action_menu()


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

function update_counts(copoVisualsURL, csrftoken, component) {
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
            $(el).find("a[anchor_type='reads']").hide()
            $(el).find("a[anchor_type='assembly']").hide()
            $(el).find("a[anchor_type='dtol_option']").hide()
        } else if (t.includes("DTOL") || t.includes("ASG")) {
            $(el).find("a[anchor_type='reads']").hide()
            $(el).find("a[anchor_type='assembly']").hide()
            $(el).find("a[anchor_type='erga_option']").hide()
        } else if (t.includes("Stand-alone")) {
            $(el).find("a[anchor_type='dtol_option']").hide()
            $(el).find("a[anchor_type='erga_option']").hide()
        }
    })
}

function load_profiles(copoVisualsURL, csrftoken, component, componentMeta, tableLoader,) {
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
            do_render_profile_table(data, copoVisualsURL, csrftoken, component, componentMeta);
            tableLoader.remove();
            filter_action_menu()
        },
        error: function () {
            alert("Couldn't retrieve profiles!");
        }
    });
}

function do_record_task(event, component, copoDeleteProfile, copoFormsURL) {
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
                'target_id': records[0].record_id // only allowing row action for edit, hence first record taken as target
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
        }).done(function () {
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

function create_ul_Tag(array) {
    let abbreviation;
    const regExp = /\(([^\)]*)\)/ // parentheses regex to get enclosed string

    // Create the ul tag element:
    const ul = document.createElement('ul');
    ul.setAttribute('class', "associated_type_ulTag");

    // Set 'ul' tag to 3 columns if the number of 'li' elements is more than 3
    //  If not, set it to 1 column
    if (array.length > 3) {
        ul.style.columnCount = "3";
        ul.style.width = "500px";
    } else {
        ul.style.columnCount = "1";
        ul.style.width = "200px"; //"0px"
    }

    for (let i = 0; i < array.length; i++) {
        // Check if item contains parentheses that include a string
        // Get abbreviation from enclosed parentheses
        // If there are parentheses, retrieve the entire string
        abbreviation = (array[i]).match(regExp) !== null ? (array[i]).match(regExp).pop() : array[i];
        // If empty parentheses are returned, set the abbreviation as the full string excluding the parentheses
        abbreviation = abbreviation === '()' ? array[i].replace(/\(\s*\)/g, "") : abbreviation

        // Create the list item:
        const li = document.createElement('li');

        // Set title to list item
        li.setAttribute('title', array[i]);

        // Set its contents
        li.appendChild(document.createTextNode(abbreviation));

        // Add item to the list
        ul.appendChild(li);
    }

    return ul;
}

function set_profile_heading(data, panel) {
    if (data.type.includes("DTOL_ENV")) {
        panel.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
            ' style="">' + data.title + '&nbsp<small>(DTOL-ENV)</small></span>');
        panel.find(".panel-heading").find(".row-ellipsis").html('<div id="' + data.record_id +
            '" class="pull-right vertical-ellipsis" title="View profile options"><i class="fa fa-ellipsis-v" style="font-size:14px"></i></div>');

        panel.find(".panel-heading").css('background-color', "#fb7d0d")
    } else if (data.type.includes("DTOL")) {
        panel.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
            ' style="">' + data.title + '&nbsp<small>(DTOL)</small></span>');
        panel.find(".panel-heading").find(".row-ellipsis").html('<div id="' + data.record_id +
            '" class="pull-right vertical-ellipsis" title="View profile options"><i class="fa fa-ellipsis-v" style="font-size:14px"></i></div>');

        panel.find(".panel-heading").css("background-color", "#16ab39")
    } else if (data.type.includes("ASG")) {
        panel.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
            ' style="">' + data.title + '&nbsp<small>(ASG)</small></span>');
        panel.find(".panel-heading").find(".row-ellipsis").html('<div id="' + data.record_id +
            '" class="pull-right vertical-ellipsis" title="View profile options"><i class="fa fa-ellipsis-v" style="font-size:14px"></i></div>');

        panel.find(".panel-heading").css("background-color", "#5829bb")
    } else if (data.type.includes("ERGA")) {
        panel.find(".panel-heading").find(".row-title").html('<span style="">' + data.title + '&nbsp<small>(ERGA)</small></span>');
        panel.find(".panel-heading").find(".row-ellipsis").html('<div id="' + data.record_id +
            '" class="pull-right vertical-ellipsis" title="View profile options"><i class="fa fa-ellipsis-v" style="font-size:14px"></i></div>');

        panel.find(".panel-heading").css("background-color", "#E61A8D")
    } else {
        if (!data.shared) {
            panel.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
                ' style="font-weight: bold">' + data.title + '&nbsp<small>(Standalone)</small></span>');
            panel.find(".panel-heading").find(".row-ellipsis").html('<div id="' + data.record_id +
                '" class="pull-right vertical-ellipsis" title="View profile options"><i class="fa fa-ellipsis-v" style="font-size:14px"></i></div>');

            panel.find(".panel-heading").css("background-color", "#009c95")
        } else {
            panel.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
                ' style="">' + data.title + '&nbsp<small>(Shared With Me)</small></span>');
            panel.find(".panel-heading").find(".row-ellipsis").html('<div id="' + data.record_id +
                '" class="pull-right vertical-ellipsis" title="View profile options"><i class="fa fa-ellipsis-v" style="font-size:14px"></i></div>');

            panel.find(".panel-heading").css("background-color", "#f26202")
        }
    }
}

function set_profile_heading1(data) {
    const panel = $('.panel')
    if (data.type.includes("DTOL_ENV")) {
        panel.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
            ' style="">' + data.title + '&nbsp<small>(DTOL-ENV)</small></span>');
        panel.find(".panel-heading").find(".row-ellipsis").html('<div id="' + data.record_id +
            '" class="pull-right vertical-ellipsis" title="View profile options"><i class="fa fa-ellipsis-v" style="font-size:14px"></i></div>');

        panel.find(".panel-heading").css('background-color', "#fb7d0d")
    } else if (data.type.includes("DTOL")) {
        panel.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
            ' style="">' + data.title + '&nbsp<small>(DTOL)</small></span>');
        panel.find(".panel-heading").find(".row-ellipsis").html('<div id="' + data.record_id +
            '" class="pull-right vertical-ellipsis" title="View profile options"><i class="fa fa-ellipsis-v" style="font-size:14px"></i></div>');

        panel.find(".panel-heading").css("background-color", "#16ab39")
    } else if (data.type.includes("ASG")) {
        panel.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
            ' style="">' + data.title + '&nbsp<small>(ASG)</small></span>');
        panel.find(".panel-heading").find(".row-ellipsis").html('<div id="' + data.record_id +
            '" class="pull-right vertical-ellipsis" title="View profile options"><i class="fa fa-ellipsis-v" style="font-size:14px"></i></div>');

        panel.find(".panel-heading").css("background-color", "#5829bb")
    } else if (data.type.includes("ERGA")) {
        panel.find(".panel-heading").find(".row-title").html('<span style="">' + data.title + '&nbsp<small>(ERGA)</small></span>');
        panel.find(".panel-heading").find(".row-ellipsis").html('<div id="' + data.record_id +
            '" class="pull-right vertical-ellipsis" title="View profile options"><i class="fa fa-ellipsis-v" style="font-size:14px"></i></div>');

        panel.find(".panel-heading").css("background-color", "#E61A8D")
    } else {
        if (!data.shared) {
            panel.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
                ' style="font-weight: bold">' + data.title + '&nbsp<small>(Standalone)</small></span>');
            panel.find(".panel-heading").find(".row-ellipsis").html('<div id="' + data.record_id +
                '" class="pull-right vertical-ellipsis" title="View profile options"><i class="fa fa-ellipsis-v" style="font-size:14px"></i></div>');

            panel.find(".panel-heading").css("background-color", "#009c95")
        } else {
            panel.find(".panel-heading").find(".row-title").html('<span id=' + data.record_id +
                ' style="">' + data.title + '&nbsp<small>(Shared With Me)</small></span>');
            panel.find(".panel-heading").find(".row-ellipsis").html('<div id="' + data.record_id +
                '" class="pull-right vertical-ellipsis" title="View profile options"><i class="fa fa-ellipsis-v" style="font-size:14px"></i></div>');

            panel.find(".panel-heading").css("background-color", "#f26202")
        }
    }
}

function set_component_buttons(data) {
    const copo_records_panel = $('.copo-records-panel');
    const panel = $('.panel');
    const panel_body = $('panel-body');
    const panel_body_row = $('<div></div>').attr({class: "row"});
    const menu = $("#expanding_menu").clone();

    copo_records_panel.attr("profile_type", data.type)
    $(menu).attr("id", "menu_" + data.record_id)
    let component_buttons;
    component_buttons = append_component_buttons(data.record_id)
    $(menu).find(".comp").append(component_buttons)

    // Display "Associated Profile Type(s)" label only if the profile has associated types
    let associated_type_label_div = $('<div></div>').attr({class: "associated_type_div_label"});

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


    panel_body_row.append(colsHTML);
    panel_body.html(panel_body_row);
    panel.append(panel_body);
    copo_records_panel.append(panel);
}

function get_profile_records(count, data) {
    get_profile_records.count++;

    let num_of_profile_records = data.length;
    let num_of_grids_per_row = 4
    let sliced_data = [];
    let startIndex;
    let endIndex;
    let row_count;

    if (num_of_profile_records % num_of_grids_per_row === 0 && num_of_profile_records !== num_of_grids_per_row) {
        row_count = num_of_profile_records / num_of_grids_per_row
    } else if (num_of_profile_records <= num_of_grids_per_row) {
        row_count = 1
    } else {
        row_count = Math.trunc((num_of_profile_records / num_of_grids_per_row) + num_of_profile_records % num_of_grids_per_row)
    }
    console.log(`Function call count: ${get_profile_records.count}; Row count: ${row_count}`)

    // Get all records once number of records is less than 4,
    // number of rows is equal to 1 and number function calls is equal to 1
    if (get_profile_records.count === 1 && row_count === 1 && num_of_profile_records <= num_of_grids_per_row) {
        startIndex = get_profile_records.lastRecordIndex
        endIndex = num_of_profile_records
        sliced_data = data.slice(startIndex, endIndex);

        get_profile_records.lastRecordIndex = num_of_profile_records
        console.log('Here: 1')
    }

    // Get 4 records per row
    if (get_profile_records.count < row_count) {
        startIndex = get_profile_records.lastRecordIndex
        endIndex = get_profile_records.lastRecordIndex + num_of_grids_per_row

        sliced_data = data.slice(startIndex, endIndex);

        get_profile_records.lastRecordIndex += num_of_grids_per_row;
        console.log('Here: 2')
    }

    // Get remaining records i.e. records that are less than 4 per row
    if (get_profile_records.count === row_count) {
        startIndex = get_profile_records.lastRecordIndex
        let records_remaining = num_of_profile_records - get_profile_records.lastRecordIndex
        endIndex = get_profile_records.lastRecordIndex + records_remaining

        sliced_data = data.slice(startIndex, endIndex);

        get_profile_records.lastRecordIndex += records_remaining
        console.log('Here: 3')
    }

    console.log(`Start index: ${startIndex}; End index: ${endIndex}`)
    console.log('Sliced data: ', sliced_data)

    return sliced_data;
}

function generate_profile_records_grid3(dataSet, tableID) {
    const gridContainer = $('#grid-container');//document.getElementById('grid-container');
    const tableID_div = $(`#${tableID}`);
    const gridCountText = $('#grid-count'); //document.getElementById('grid-count');
    const gridTotal = $('#grid-total');//document.getElementById('grid-total');
    const loadTrigger = document.getElementById('load-trigger');

    const gridLimit = dataSet.length;
    const loadLimit = 4; // number of grids per row
    let gridsShown = 0;

    const gridClass = 'grid';
    const gridItemClass = 'grid-item';

    let throttleTimer;
    const throttleTime = 1000;

    gridTotal.text(gridLimit)//gridTotal.innerText = gridLimit;

    const observer = detectScroll();

    // This function makes a request to the profile records data server
    function load_grids() {
        const newGridElements = [];
        const amountToLoad = Math.min(loadLimit, gridLimit - gridsShown);

        for (let i = 0; i < amountToLoad; i++) {
            // Create grid item and indicate grid load
            const grid = $('<div></div>').attr({class: `${gridClass} ${gridItemClass}`});

            // Include grid in 'copo_profiles_table' div
            tableID_div.append(grid)

            // Store in temp array to update with actual grid when loaded
            newGridElements.push(grid);
        }

        // Update grid count
        gridsShown += amountToLoad;
        gridCountText.text(gridsShown) //gridCountText.innerText = gridsShown;

        // Simulate delay from network request
        setTimeout(() => {
            const records = get_profile_records(amountToLoad, dataSet);

            for (let i = 0; i < records.length; i++) {
                const element = records[i];


                // Create COPO records panel
                const copo_records_panel = $('<div></div>').attr({class: "copo-records-panel"});

                // Create panel
                const panel = $('<div></div>').attr({class: "panel"});

                // Create panel heading
                const panel_heading = $('<div></div>').attr({class: "panel-heading"});

                // Create panel heading row
                const panel_heading_row = $('<div></div>').attr({class: "row"});
                // Create panel heading title div
                const panel_heading_titleDiv = $('<div></div>').attr({class: "col-sm-10 col-md-10 col-lg-10 row-title"});

                // Create panel heading ellipsis div
                const panel_heading_ellipsisDiv = $('<div></div>').attr({class: "col-sm-2 col-md-2 col-lg-2 row-ellipsis"});

                // Create panel body
                const panel_body = $('<div></div>').attr({class: "panel-body"});

                // Create panel body row
                const panel_body_row = $('<div></div>').attr({class: "row"}); //$('<div class="row"></div>');

                newGridElements[i].removeClass(gridItemClass) //newGridElements[i].classList.remove(gridItemClass);
                newGridElements[i].css("background-color", "white") //newGridElements[i].style.backgroundColor = "white";
                //newGridElements[i].text(element.title) //newGridElements[i].innerText = element.title;

                // Set layout
                set_profile_panel_layout(element, newGridElements[i], tableID_div, copo_records_panel, panel, panel_heading, panel_heading_row, panel_heading_titleDiv, panel_heading_ellipsisDiv, panel_body, panel_body_row)

                // Set heading
                set_profile_heading(element, panel)
            }
        }, 1500);

        if (gridsShown === gridLimit) {
            observer.unobserve(loadTrigger);
        }
    }

    function detectScroll() {
        const tableLoader = $('<div class="copo-i-loader"></div>');
        const observer = new IntersectionObserver(
            (entries) => {
                for (let entry of entries) {
                    if (entry.isIntersecting) {
                        throttle(() => {
                            $("#component_table_loader").append(tableLoader);
                            load_grids();
                            tableLoader.remove();
                        }, throttleTime);
                    }
                }
            },
            // Set "rootMargin" because of #bottom-panel
            {rootMargin: '-30px'}
        );

        observer.observe(loadTrigger);

        return observer;
    }

    function throttle(callback, time) {
        // Prevent additional calls until timeout elapses
        if (throttleTimer) {
            console.log('throttling');
            return;
        }
        throttleTimer = true;

        setTimeout(() => {
            callback();

            // Allow additional calls after timeout elapses
            throttleTimer = false;
        }, time);
    }


// Infinite scroll//

    function getItemHTML({user, urls}) {
        return `<div class="photo-item">
    <img class="photo-item__image" src="${urls.regular}" alt="Photo by ${user.name}" />
    <p class="photo-item__caption">
      <a href="${user.links.html}?utm_source=infinite-scroll-demos&utm_medium=referral&utm_campaign=api-credit">${user.name}</a>
    </p>
  </div>`;
    }


}


function set_selected_profile_record(element) {
    console.log('I am clicked')
    console.log(element)

    const selected_grids = $("#copo_profiles_table div[class$='grid selected']");
    const selected_panels = $(".panel div[class$='panel-body panel-body-selected']");
    // Check if any grid is marked as 'selected',
    // if at least one exists, unmark it as 'selected' and mark the current selected grid as 'selected'

    if (selected_grids.length !== 0) {
        console.log("selected grid exists")
        selected_grids.each(function (index, item) {
            item.removeClass("selected")

        })
    }

    if (selected_panels.length !== 0) {
        console.log("selected panel exists")
        selected_panels.each(function (index, item) {
            item.removeClass("panel-body-selected")

        })
    }

    // Set grid as selected
    $(element).closest('.grid').addClass("selected")
    $(element).closest('.panel_body').addClass("panel-body-selected")

    // set_selected_rows(dt); // Highlight selected grid
}