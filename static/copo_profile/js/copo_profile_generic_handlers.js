//** Generic handlers for copo profile web page
const quickTourMessages = quick_tour_messages(); //holds quick tour messages
let quickTourArray = []; //holds quick tour elements
let quickTourFlag = true; //flag to decide whether or not to display quick tour

$(document).ready(function () {
    let componentName = $("#nav_component_name").val();
    //set up global navigation components
    do_page_controls(componentName);

    //global_help_call
    do_global_help(componentName);

    //context help event
    do_context_help_event();

    // Generic handler: dismiss alert
    $(document).on("click", ".alertdismissOK", function () {
        WebuiPopovers.hideAll();
    });
});

function set_empty_profile_component_message(dataRows, table_id = "*") {
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

function do_crud_profile_action_feedback(meta) {
    let feedbackClass;

    if (["success", "green", "positive"].indexOf(meta.status) > -1) {
        feedbackClass = "alert-success";
    } else if (["error", "red", "danger", "negative"].indexOf(meta.status) > -1) {
        feedbackClass = "alert-danger";
    } else if (["warning"].indexOf(meta.status) > -1) {
        feedbackClass = "alert-warning";
    } else {
        feedbackClass = "alert-info";
    }

    const infoPanelElement = trigger_global_notification();

    const feedback = get_alert_control();
    feedback
        .removeClass("alert-success")
        .addClass(feedbackClass)
        .addClass("page-notifications-node");

    feedback.find(".alert-message").html(meta.message);
    infoPanelElement.prepend(feedback);
}

function refresh_profile_tool_tips() {
    $("[data-toggle='tooltip']").tooltip();
    $("[data-toggle='popover']").popover();
    $('.ui.dropdown').dropdown();
    $('.copo-tooltip').popup();
    apply_color();
    refresh_selectbox();
    refresh_multiselect2box();
} //end of func   ****************

function refresh_validator(formObject) {
    formObject.validator('update');

} //end of func

//refreshes selectboxes to pick up events
function refresh_selectbox() {
    $('.copo-select').each(function () {
        const elem = $(this);

        if (!(/selectize/i.test(elem.attr('class')))) { // if not already instantiated
            elem.selectize({
                delimiter: ',',
                plugins: ['remove_button'],
                persist: false,
                create: function (input) {
                    return {
                        value: input,
                        text: input
                    };
                }
            });
        }
    });

} //end of function

function refresh_multiselect2box() {
    $('.copo-multi-select2').each(function () {
        const elem = $(this);

        //if (!elem.hasClass("select2-hidden-accessible")) {
            elem.select2({
                data: JSON.parse(elem.attr("data-optionsList")),
                maximumSelectionLength: elem.attr("data-maximumSelectionLength"),
                // dropdownParent: $(this).closest(".copo-form-group")
            });

            elem.val(JSON.parse(elem.attr("data-currentValue")));
            elem.trigger('change');
        //}

    });

} //end of function

// Set COPO frontpage properties in this dictionary
function get_profile_component_meta(component) {
    let componentMeta = null;
    const components = get_copo_profile_components();

    components.forEach(function (comp) {
        if (comp.component === component) {
            componentMeta = comp;
            return false;
        }
    });

    return componentMeta
}

function get_copo_profile_components() {
    return [
        {
            component: 'profile',
            title: 'Work Profiles',
            buttons: ["quick-tour-template", "new-component-template"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help", "copo-sidebar-profiles-legend"],
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
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
            colorClass: "samples_color",
            color: "olive",
            profile_component: "dtol",
            tableID: 'sample_table',
            recordActions: ["show_sample_source", "describe_record_all", "edit_record_single"],
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
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
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
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
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
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
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
            recordActions: ["add_record_all" ],   // "delete_record_multi, submit_assembly_multi, , "edit_record_single"
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
            recordActions: ["add_record_all", "edit_record_single", "delete_record_multi",  "submit_annotation_multi"],
            visibleColumns: 5
        },
        {
            component: 'files',
            title: 'Files',
            iconClass: "fa fa-file",
            semanticIcon: "file",
            countsKey1_deleted: "num_assembly",
            buttons: ["new_local_file", "new_terminal_file"],
            sidebarPanels: ["copo-sidebar-info"],
            colorClass: "files_color",
            color: "blue",
            tableID: 'files_table',
            profile_component: "stand-alone",
            recordActions: ["add_local_all", "add_terminal_all", "delete_record_multi"],   // "delete_record_multi, submit_assembly_multi , "edit_record_single" 
            visibleColumns: 5
        },
        {
            component: 'taggedseq',
            title: 'Tagged Sequences',
            iconClass: "fa fa-database",
            semanticIcon: "database",
            countsKey1: "num_barcode_manifest",
            buttons: [],
            sidebarPanels: ["copo-sidebar-info"],
            colorClass: "data_color",
            color: "red",
            tableID: 'tagged_seq_table',
            profile_component: "dtol",
            recordActions: [ "delete_record_multi",  "submit_tagged_seq_multi"],
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
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help", "copo-sidebar-annotate"],
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
    ]
}

//builds component-page navbar
function do_page_controls(componentName) {
    let component = null;
    const components = get_copo_profile_components();

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
            sidebarPanels.find(".profiles-legend").append(sidebarPanels2.find(".profiles-legend").find("." + item));
        });

        sideBar
            .append(sidebarPanels.find(".nav-tabs"))
            .append(sidebarPanels.find(".tab-content"))
            .append(sidebarPanels.find(".profiles-legend"));


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

        const components = get_profile_components();

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
    quick_tour_event();
    refresh_profile_tool_tips();
}

function toggle_display_help_tips(state, parentElement) {
    if (!state) {
        parentElement.find(".copo-form-group").webuiPopover('destroy');
        parentElement.find(".copo-form-group").attr("data-helptip", "no");
    } else {
        parentElement.find(".copo-form-group").attr("data-helptip", "yes");
    }
}

function get_spinner_image() {
    const loaderObject = $('<div>', {
        style: 'text-align: center',
        html: "<span class='fa fa-spinner fa-pulse fa-3x'></span>"
    });

    return loaderObject.clone();
}

function sanitise_help_list(contextHelpList) {
    const dataSet = [];

    if (contextHelpList.properties) {
        const dtd = contextHelpList.properties;

        for (let i = 0; i < dtd.length; ++i) {
            const option = {};
            option["id"] = i + 1;
            option["title"] = dtd[i].title;
            option["content"] = dtd[i].content;
            option["context"] = dtd[i].context;
            let helpID = Math.random() + Math.random() + Math.random();
            helpID = helpID.toString();
            option["help_id"] = "context_help_" + i + "_" + helpID.replace(".", "_");
            dataSet.push(option);
        }
    }

    return dataSet;
}

function do_context_help(data) {
    //does current page request context help?
    const tableID = 'page-context-help';
    const helpComponent = $("#" + tableID);

    //if true then page requests context help control to be added
    if (!helpComponent.length) {
        return false;
    }


    const dtd = sanitise_help_list(data);

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
            .add(dtd);
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
            data: dtd,
            searchHighlight: true,
            "lengthChange": false,
            order: [
                [0, "asc"]
            ],
            pageLength: 5,
            language: {
                "info": " _START_ to _END_ of _TOTAL_ topics",
                "lengthMenu": "_MENU_ tips",
                "search": " ",
            },
            columns: [
                {
                    "data": "id",
                    "visible": false
                },
                {
                    "orderable": false,
                    "width": "2%",
                    "data": null,
                    "render": function (data, type, row, meta) {
                        var iconSpan = '<span data-target="' + data.help_id + '" class="side-help-trigger" aria-hidden="true" title="View help content"></span>';

                        var parentDiv = $('<div></div>');
                        parentDiv.append(iconSpan);

                        return $('<div></div>').append(parentDiv).html();
                    }
                },
                {
                    "data": null,
                    "title": "Help Topics",
                    "render": function (data, type, row, meta) {
                        var helpTopicID = data.help_id;

                        var helpTitleDiv = $('<div></div>')
                            .attr("id", "title_" + helpTopicID)
                            .html('<div>' + data.title + '</div>');

                        var helpContentDiv = $('<div></div>')
                            .attr("id", helpTopicID)
                            .attr("class", "collapse context-help-collapse")
                            .css("margin-top", "10px")
                            .html('<div>' + data.content + '</div>');


                        return $('<div></div>').append(helpTitleDiv).append(helpContentDiv).html();
                    }
                },
                {
                    "data": "content",
                    "visible": false
                }
            ],
            dom: 'lft<"row">rip',
            "columnDefs": [{
                "orderData": 0,
            }]
        });
    }


    $('#' + tableID + '_wrapper')
        .find(".dataTables_filter")
        .find("input")
        .removeClass("input-sm")
        .attr("placeholder", "Search Help")
    // .attr("size", 30);
}

function do_global_help(component) {
    let copoVisualsURL = "/copo/copo_profile_visualise/";
    let csrftoken = $.cookie('csrftoken');
    //global help

    $.ajax({
        url: copoVisualsURL,
        type: "POST",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            'task': 'help_messages',
            'component': component
        },
        success: function (data) {

            //set quick tour message and trigger display event
            try {
                do_context_help(data.context_help);
                // quickTourFlag = data.quick_tour_flag;
                //
                // if (quickTourFlag && data.user_has_email) {
                //     //$(".takeatour").trigger("click");
                // }

            } catch (err) {
            }
        },
        error: function () {
            alert("Couldn't retrieve page help!");
        }
    });
}

function do_context_help_event() {
    //handles collapsing of help topics

    $(document).on('click', '.side-help-trigger', function (e) {
        const dataTargetID = $(this).attr('data-target');

        if ($(this).parent().hasClass("shown")) {
            $(this).parent().removeClass("shown");
            $("#" + dataTargetID).collapse("hide");
        } else {
            $(this).parent().addClass("shown");
            $("#" + dataTargetID).collapse("show");
        }
    });
}

function update_quick_tour_flag() {
    let copoVisualsURL = "/copo/copo_profile_visualise/";
    let csrftoken = $.cookie('csrftoken');

    WebuiPopovers.hideAll(); //hide all shown popovers

    $.ajax({
        url: copoVisualsURL,
        type: "POST",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            'task': 'update_quick_tour_flag',
            'quick_tour_flag': false
        },
        success: function (data) {
            //set quick tour flag
            try {
                quickTourFlag = data.quick_tour_flag;
            } catch (err) {
            }
        },
        error: function () {
            alert("Couldn't update settings!");
        }
    });
}

function quick_tour_event() {
    $('.takeatour').on('click', function (e) {
        const dismissTour = '<a class="dismisstouralert pull-right" href="#" role="button" ' +
            'style="text-decoration: none; color:  #c93c00;" aria-haspopup="true" aria-expanded="false">' +
            '<i class="fa fa-times-circle " aria-hidden="true">' +
            '</i>&nbsp; Dismiss Tour</a>';

        const takeTour = '<a class="takeatouryes" href="#" role="button" ' +
            'style="text-decoration: none;" aria-haspopup="true" aria-expanded="false">' +
            '<i class="fa fa-lightbulb-o " style="color: #35637e;" aria-hidden="true">' +
            '</i>&nbsp; Take Tour</a>';


        const messageContent = 'Do you want to take a quick tour of the page? <br/><br/><span style="color: #35637e;">Please note that your screen will be dimmed, and regular page elements inaccessible in the quick tour mode.</span>' + '<hr/>' + takeTour + dismissTour;

        $(this).webuiPopover('destroy');

        $(this).webuiPopover({
            title: "Quick Tour",
            content: '<div class="webpop-content-div">' + messageContent + '</div>',
            trigger: 'sticky',
            width: 300,
            arrow: true,
            closeable: true,
            placement: 'bottom-right'
        });
    });

    $(document).on("click", ".takeatouryes", function (e) {
        quickTourArray = [];
        WebuiPopovers.hideAll(); //hide all shown popovers

        //retain quick tour elements with defined messages
        $('[data-copo-tour-id]').each(function () {
            if (quickTourMessages.hasOwnProperty($(this).attr("data-copo-tour-id"))) {
                if ($(this).is(":visible")) { //only consider elements that are visible on the DOM
                    quickTourArray.push($(this));
                }
            }
        });

        if (quickTourArray.length > 0) {
            quick_tour_select();
        }

    });

    $(document).on("click", ".quicktournext", function () {
        if (quickTourArray.length > 0) {
            quick_tour_select();
        }
    });

    $(document).on("click", ".endcopotour", function () {
        quickTourArray = [];
        WebuiPopovers.hideAll(); //hide all shown popovers
    });

    $(document).on("click", ".dismisstouralert", function () {
        update_quick_tour_flag();
    });
}

function quick_tour_select() {
    // display tour elements

    const item = quickTourArray[0];
    const itemMessage = quickTourMessages[item.attr("data-copo-tour-id")];

    const endTour = '<a class="endcopotour pull-right" href="#" role="button" ' +
        'style="text-decoration: none; color:  #c93c00;" aria-haspopup="true" aria-expanded="false">' +
        '<i class="fa fa-times-circle " aria-hidden="true">' +
        '</i>&nbsp; End Tour</a>';

    let nextTip = endTour;


    if (quickTourArray.length > 1) {
        nextTip = '<a class="quicktournext" href="#" role="button" ' +
            'style="text-decoration: none;" aria-haspopup="true" aria-expanded="false">' +
            '<i class="fa fa-lightbulb-o " style="color: #35637e;" aria-hidden="true">' +
            '</i>&nbsp; Next Tip</a>';

        nextTip += endTour;
    }

    const messageContent = itemMessage.content + '<hr/>' + nextTip;

    item.webuiPopover('destroy');
    item.webuiPopover({
        title: itemMessage.title,
        content: '<div class="webpop-content-div">' + messageContent + '</div>',
        trigger: 'sticky',
        width: 300,
        arrow: true,
        closeable: true,
        placement: 'auto-bottom',
        backdrop: true,
    });

    for (let i = 0; i < quickTourArray.length; i++) {
        if (quickTourArray[i].attr("data-copo-tour-id") === item.attr("data-copo-tour-id")) {
            quickTourArray.splice(i, 1);
            break;
        }
    }
} //end of func

function quick_tour_messages() {
    const qt = {
        "description": "Provides messages for creating quick tour of system components/elements:",
        "properties": {
            "new_profile_button": {
                "title": "Create New Profile",
                "content": "Click here to create a new Profile. A COPO Profile is a collection of 'research objects' or components that form part of a research project or study."
            },
            "documentation_button": {
                "title": "Documentation",
                "content": "Click here to access COPO's documentation."
            },
            "notifications_button": {
                "title": "Notifications",
                "content": "Click here to access notifications."
            },
            "global_notification_button": {
                "title": "Notification Component",
                "content": "Click this button to view system notifications."
            },
            "global_user_authenticated_button": {
                "title": "Authenticated User",
                "content": "Click here to access the following tasks: <ul><li>View your ORCiD profile</li><li>View obtained tokens</li><li>Logout of the system</li></ul>"
            },
            "profile_links_button_group": {
                "title": "Profile Links",
                "content": "Shortcut buttons for accessing profile components."
            },
            "copo_data_upload_tab": {
                "title": "File Upload",
                "content": "Select this tab to access the file upload view. <br/>For more information about this control, including a demonstration of its usage, please use the help component."
            },
            "copo_data_inspect_tab": {
                "title": "File Inspect Tab",
                "content": "Select this tab to view files uploaded to COPO. <br/>For more information about this control, including a demonstration of its usage, please use the help component."
            },
            "copo_data_describe_tab": {
                "title": "File Describe Tab",
                "content": "Select this tab to view the file description wizard and files currently being described. <br/>For more information about this control, including a demonstration of its usage, please use the help component."
            },
            "copo_data_upload_file_button": {
                "title": "Upload File Button",
                "content": "Click this button to upload files to COPO. Multiple files can be selected and uploaded at once. <p>Uploaded files are displayed in the <strong>Inspect</strong> pane. "
            },
            "datafile_table_describe": {
                "title": "Describe Button",
                "content": "Use this button to activate the datafile description wizard. Please note that one or more files must be selected before clicking the describe button. Once clicked, the view will change to display the wizard, where the target datafiles may be described."
            },
            "profile_details_panel": {
                "title": "Profile Details",
                "content": "View a profile details here having selected a profile record."
            },
            "page_context_help_panel": {
                "title": "Help",
                "content": "Interact with the help pane to find help topics relevant to the page and/or current task."
            },
            "profile_table": {
                "title": "Profile Records",
                "content": "Profile records list.<ol><li>Click on any component (e.g., Samples) within a profile to access any particular component's page</li><li>Use the action buttons (e.g., Select all, Add) to interact with profile records</li><li>Use the profile search control to display a filtered listing of records, based on matched terms</li></ol>"
            },
            "new_publication_button": {
                "title": "Create New Publication",
                "content": "Click here to create a new Publication. You will be provided with the following options: <ol><li>Manually enter a new publication record using the publication form</li><li>Resolve a Digital Object Identifier (DOI) to retrieve a target publication record from an external service</li><li>Resolve a PubMed ID to retrieve a target publication record from an external service</li></ol>"
            },
            "page_activity_panel": {
                "title": "Task",
                "content": "Interact with the task pane to perform available tasks on selected records. <ol><li>Select one or more records by clicking on target rows</li><li>Select the required task from available tasks to perform</li></ol>"
            }
        }
    };

    return qt.properties;
}

function get_alert_control() {
    let alert = $('<div class="alert alert-success alert-dismissable fade in copo-alert-message" style="background-image: none; border: none;">\n' +
        '            <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>\n' +
        '            <span class="webpop-content-div alert-message"></span>\n' +
        '        </div>');

    return alert.clone();
}