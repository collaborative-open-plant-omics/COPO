//**some re-usable functions across different modules
var AnnotationEventAdded = false;
var selectizeObjects = {}; //stores reference to selectize objects initialised on the page
var copoVisualsURL = "/copo/copo_visualize/";
var csrftoken = $.cookie('csrftoken');
var quickTourMessages = quick_tour_messages(); //holds quick tour messages
var quickTourArray = []; //holds quick tour elements
var quickTourFlag = true; //flag to decide whether or not to display quick tour

$(document).ready(function () {
    var componentName = $("#nav_component_name").val();

    setup_autocomplete()

    //set up global navigation components
    do_page_controls(componentName);

    //global_help_call
    do_global_help(componentName);

    //context help event
    do_context_help_event();

    //input fields help tips event
    //set_inputs_help();

    //add event for ontology field change
    ontology_value_change();

    //add selectize control event
    set_selectize_select_event();

    ontology_link_event();

    select2_mouse_event();

    select2_data_view_event();

    setup_dismissable_message();

    setup_collapsible_event();

    setup_copo_general_lookup_event();

});


function setup_collapsible_event() {
    $(document).on('show.bs.collapse', '.copo-details-coll.collapse', function (event) {
        $(this).prev(".panel-heading").find(".fa").removeClass("fa-plus").addClass("fa-minus");
    }).on('hide.bs.collapse', '.copo-details-coll.collapse', function () {
        $(this).prev(".panel-heading").find(".fa").removeClass("fa-minus").addClass("fa-plus");
    });
}

function setup_copo_general_lookup_event() {
    $(document).on('click', '.copo-tag ', function (event) {
        var content = $(this).closest(".copo-item").find(".copo-tag-content");
        content.slideToggle("slow");
    })
}

function setup_autocomplete() {
    var copoFormsURL = "/copo/copo_forms/";
    $(document).on('focus', 'input[id^="annotator-field"]', function (e) {
        t = e.currentTarget
        $('.annotator-listing').find('ul').empty()
        $(t).addClass('ontology-field')

        if (!AnnotationEventAdded) {
            $(t).attr('data-autocomplete', '/copo/ajax_search_ontology/999/')

            auto_complete();
            AnnotationEventAdded = true;
        }
    })
    auto_complete();
}

function setup_dismissable_message() {
    $(document).on("click", ".message .close", function () {
        $(this).closest(".message").remove();
    });
}

function get_feedback_pane() {
    return $('<div class="ui success message" style="margin-bottom: 10px;">\n' +
        '                        <i class="close icon"></i>\n' +
        '                        <div class="header"></div>\n' +
        '                        <p></p>\n' +
        '                        <div class="m-body"></div>\n' +
        '                    </div>');
}

function select2_data_view_event() {
    $(document).on("click", ".copo-embedded", function () {
        var item = $(this);
        lookupsURL = $("#ajax_search_copo_local").val();
        var localolsURL = lookupsURL.replace("999", item.data("source"));
        var accession = item.data("accession");

        item.find(".fa").addClass("fa-spin");
        item.addClass("text-primary");
        item.webuiPopover('destroy');

        $.ajax({
            url: localolsURL,
            type: "GET",
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: {
                "accession": accession
            },
            success: function (data) {
                if (data.hasOwnProperty('result') && data.result.length > 0) {
                    var desc = data.result[0].description;
                    WebuiPopovers.updateContent(item, '<div class="webpop-content-div limit-text">' + desc + '</div>');

                    item.webuiPopover({
                        content: '<div class="webpop-content-div limit-text">' + desc + '</div>',
                        trigger: 'sticky',
                        width: 300,
                        arrow: true,
                        placement: 'right',
                        dismissible: true,
                        closeable: true
                    });

                    item.removeClass("text-primary");
                    item.find(".fa").removeClass("fa-spin");
                }
            },
            error: function () {
                item.removeClass("text-primary");
                item.find(".fa").removeClass("fa-spin");
                item.webuiPopover('destroy');
                alert("Couldn't retrieve item's details!");
            }
        });
    });
}

function select2_mouse_event() {
    $(document).on("mouseover", ".server-desc", function () {
        var item = $(this);

        var parentElem = item.closest(".parentSpan");
        var url = parentElem.attr("data-url");
        var accession = parentElem.attr("data-id");

        if (!(url && accession)) {
            return false;
        }

        WebuiPopovers.updateContent(item, '<div class="webpop-content-div"><span class="fa fa-spinner fa-pulse fa-2x"></span></div>');

        $.ajax({
            url: url,
            type: "GET",
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: {
                "accession": accession
            },
            success: function (data) {
                if (data.hasOwnProperty('result') && data.result.length > 0) {
                    var desc = data.result[0].description;
                    WebuiPopovers.updateContent(item, '<div class="webpop-content-div limit-text">' + desc + '</div>');

                }
            },
            error: function () {
                console.log("Couldn't retrieve item's details!");
            }
        });


    });

}

function ontology_value_change() {
    //handles 'change of mind by user while entering value', to clear associated fields
    $(document).on('keyup', '.ontology-field', function () {
        var elem = $(this);
        elem.closest(".ontology-parent").find(".ontology-field-hidden").each(function () {
            $(this).val('');
        });
    });
}

function ontology_link_event() {
    $(document).on('click', '.non-free-text', function () {
        $(this).closest(".onto-label").find(".onto-label-more").toggle();
    });
}

function set_selectize_select_event() {
    $(document).on("keyup keypress", function (event) {
        var keyCode = event.keyCode || event.which;
        if (keyCode === 38 || keyCode === 40) {
            if ($(event.target).closest(".onto-select").length) {
                var item = $(event.target).closest(".onto-select");
                var activeElem = item.find(".selectize-dropdown-content .active").find(".onto-label");

                var desc = activeElem.attr("data-desc");
                var prefix = activeElem.attr("data-prefix");
                var label = activeElem.attr("data-label");
                var accession = activeElem.attr("data-accession");

                showontopop(item, label, prefix, desc, accession);
            } else if ($(event.target).closest(".general-onto").length) {
                var item = $(event.target).closest(".general-onto");
                var activeElem = item.find(".selectize-dropdown-content .active").find(".onto-label");

                var indx = activeElem.data("indx");
                var parentid = activeElem.data("parentid");
                var lblField = activeElem.data("lblfield");
                var elemFields = JSON.parse(activeElem.closest(".ontology-parent").find(".elem-fields").val());

                try {
                    var valueObject = selectizeObjects[parentid].options[indx];
                    showgeneraldetails(item, valueObject, elemFields, lblField);
                } catch (e) {
                    console.log("Couldn't retrieve control value object [value, parent id]: [" + indx + "," + parentid + "]");
                }

            } else if ($(event.target).closest(".copo-multi-search").length) {
                var eventTarget = $(event.target).closest(".copo-multi-search");
                var item = eventTarget.find(".selectize-dropdown-content .active");
                var recordId = item.attr("data-value");
                var associatedComponent = item.find(".caption-component").attr("data-component");
                var popTarget = item.closest(".copo-form-group");

                if (associatedComponent) {
                    resolve_element_view(recordId, associatedComponent, popTarget);
                }
            } else if ($(event.target).closest(".copo-lookup").length) {
                var item = $(event.target).closest(".copo-lookup");
                var activeElem = item.find(".selectize-dropdown-content .active").find(".lookup-label");
                var desc = activeElem.attr("data-desc");
                var label = activeElem.attr("data-label");
                var accession = activeElem.attr("data-accession");
                var url = activeElem.attr("data-url");
                var serverSide = activeElem.attr("data-serverside");

                showlkup(item, label, desc, accession, url, serverSide);

            }
        }
    });


    $(document).on("mouseenter", ".selectize-dropdown-content .active", function (event) {
        if ($(this).closest(".selectize-control.onto-select").length) {
            var item = $(this).closest(".selectize-control.onto-select");

            var desc = $(this).find(".onto-label").attr("data-desc");
            var prefix = $(this).find(".onto-label").attr("data-prefix");
            var label = $(this).find(".onto-label").attr("data-label");
            var accession = $(this).find(".onto-label").attr("data-accession");

            showontopop(item, label, prefix, desc, accession);
        } else if ($(this).closest(".selectize-control.general-onto").length) {
            var item = $(this).closest(".selectize-control.general-onto");
            var activeElem = $(this).find(".onto-label");

            var indx = $(this).find(".onto-label").data("indx");
            var parentid = activeElem.data("parentid");
            var lblField = activeElem.data("lblfield");
            var elemFields = JSON.parse(activeElem.closest(".ontology-parent").find(".elem-fields").val());

            try {
                var valueObject = selectizeObjects[parentid].options[indx];
                showgeneraldetails(item, valueObject, elemFields, lblField);
            } catch (e) {
                console.log("Couldn't retrieve control value object [value, parent id]: [" + indx + "," + parentid + "]");
            }
        } else if ($(this).closest(".selectize-control.copo-multi-search").length) {
            var item = $(this).closest(".selectize-control.copo-multi-search");

            var recordId = item.find(".selectize-dropdown-content .active").attr("data-value");
            var associatedComponent = item.find(".caption-component").attr("data-component");
            var popTarget = item.closest(".copo-form-group");

            if (associatedComponent) {
                resolve_element_view(recordId, associatedComponent, popTarget);
            }
        } else if ($(this).closest(".selectize-control.copo-lookup").length) {
            var item = $(this).closest(".selectize-control.copo-lookup");

            var desc = $(this).find(".lookup-label").attr("data-desc");
            var label = $(this).find(".lookup-label").attr("data-label");
            var accession = $(this).find(".lookup-label").attr("data-accession");

            var url = $(this).find(".lookup-label").attr("data-url");
            var serverSide = $(this).find(".lookup-label").attr("data-serverside");

            showlkup(item, label, desc, accession, url, serverSide);
        }

    });
}

function showlkup(item, label, desc, accession, url, serverSide) {

    var show_lkup_details = function () {

        var result = $('<div/>',
            {
                class: "limit-text"
            });

        item.webuiPopover('destroy');

        if (String(accession) != 'undefined' && String(label) != 'undefined') {

            //ontology accession
            var lookupAccession = $('<div/>');

            if (accession != '') {
                lookupAccession.css('margin-top', '5px')
                $('<span>', {
                    class: "ontology-accession-link",
                    html: "<span style='text-decoration-line: underline; color:#2759a5'>" + accession + "</span>"
                }).appendTo(lookupAccession);
            }

            result.append(lookupAccession);


            //ontology description
            var lookupDescription = $('<div/>');

            if (desc != '') {
                lookupDescription.css('margin-top', '5px');
                lookupDescription.html(desc);

            }

            result.append(lookupDescription);

            item.webuiPopover({
                title: label,
                content: '<div class="webpop-content-div">' + $('<div/>').append(result).html() + '</div>',
                trigger: 'sticky',
                width: 300,
                arrow: true,
                placement: 'right',
                dismissible: true
            });
        }
    }

    if (serverSide) {//resolve item description from the server
        $.ajax({
            url: url,
            type: "POST",
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: {
                "accession": accession
            },
            success: function (data) {
                if (data.hasOwnProperty('result') && data.result.length > 0) {
                    desc = data.result[0].description;
                    show_lkup_details();
                }

            },
            error: function () {
                console.log("Couldn't retrieve item's details!");
            }
        });

    } else {
        show_lkup_details();
    }


}

function showontopop(item, label, prefix, desc, accession) {
    var result = $('<div/>',
        {
            class: "limit-text"
        });

    // var result = '<div class="limit-text"><ul class="list-group list-group-flush"><li style="border: none;" class="list-group-item">Value: ' + label + '</li><li style="border: none;" class="list-group-item">Accession: ' + accession + '</li><li style="border: none;" class="list-group-item">Description: ' + desc + '</li></ul></div>';

    item.webuiPopover('destroy');

    if (String(accession) != 'undefined' && String(label) != 'undefined') {

        //ontology source
        var ontologySource = $('<div/>',
            {
                html: "This is a free-text value"
            });

        if (prefix != '') {
            ontologySource.html("Ontology source: " + prefix);
        }

        result.append(ontologySource);

        //ontology accession
        var ontologyAccession = $('<div/>');

        if (accession != '') {
            ontologyAccession.css('margin-top', '5px')
            $('<span>', {
                class: "ontology-accession-link",
                html: "<span style='text-decoration-line: underline; color:#2759a5'>" + accession + "</span>"
            }).appendTo(ontologyAccession);
        }

        result.append(ontologyAccession);


        //ontology description
        var ontologyDescription = $('<div/>');

        if (desc != '') {
            ontologyDescription.css('margin-top', '5px');
            ontologyDescription.html(desc);

        }

        result.append(ontologyDescription);

        item.webuiPopover({
            title: label,
            content: '<div class="webpop-content-div">' + $('<div/>').append(result).html() + '</div>',
            trigger: 'sticky',
            width: 300,
            arrow: true,
            placement: 'right',
            dismissible: true
        });
    }

}

function showgeneraldetails(item, dataObject, schema, lblField) {
    var result = $('<div/>',
        {
            class: "limit-text"
        });

    item.webuiPopover('destroy');

    let message = $('<div class="webpop-content-div"></div>');
    var codeList = $('<div class="ui relaxed divided list"></div>');

    result.append(message);
    message.append(codeList);

    for (var i = 0; i < schema.length; ++i) {
        var schemaNode = schema[i];
        if (schemaNode.hasOwnProperty("show_in_table") && (schemaNode.show_in_table.toString().toLowerCase() == "true")) {
            var itemNode = $('<div class="item"></div>');
            codeList.append(itemNode);
            itemNode.append('<div class="content"><div class="header">' + schemaNode.label + '</div><div class="description webpop-content-div">' + dataObject[schemaNode.id] + '</div></div>');
        }
    }

    item.webuiPopover({
        title: dataObject[lblField],
        content: '<div class="webpop-content-div">' + $('<div/>').append(result).html() + '</div>',
        trigger: 'sticky',
        width: 300,
        arrow: true,
        placement: 'right',
        dismissible: true
    });

}

function resolve_element_view(recordId, associatedComponent, eventTarget) {
    //maps form element by id to component type e.g source, sample

    if (associatedComponent == "") {
        return false;
    }

    $.ajax({
        url: copoVisualsURL,
        type: "POST",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            'task': "attributes_display",
            'component': associatedComponent,
            'target_id': recordId
        },
        success: function (data) {
            var title = 'Attributes';
            gAttrib = build_attributes_display(data);

            if (data.component_label) {
                title = data.component_label;
            }

            eventTarget.webuiPopover('destroy');

            eventTarget.webuiPopover({
                title: title,
                content: '<div class="webpop-content-div limit-text">' + $('<div/>').append(gAttrib).html() + '</div>',
                trigger: 'sticky',
                width: 300,
                arrow: true,
                placement: 'right',
                dismissible: true
            });

        },
        error: function () {
            var message = "Couldn't retrieve attributes!";

            eventTarget.webuiPopover('destroy');

            eventTarget.webuiPopover({
                title: 'Info',
                content: '<div class="webpop-content-div">' + message + '</div>',
                trigger: 'sticky',
                width: 300,
                arrow: true,
                placement: 'right',
                dismissible: true
            });
        }
    });
}


function do_component_delete_confirmation(params) {
    var targetComponentBody = "Please confirm delete action for the selected records.";
    var targetComponentTitle = "Delete Alert!";

    var doTidyClose = {
        closeIt: function (dialogRef) {
            dialogRef.close();
        }
    };

    var code = BootstrapDialog.show({
        type: BootstrapDialog.TYPE_DANGER,
        title: $('<span>' + targetComponentTitle + '</span>'),
        message: function () {
            var $message = $('<span>' + targetComponentBody + '</span>');
            return $message;
        },
        draggable: true,
        closable: true,
        animate: true,
        onhide: function () {
        },
        buttons: [{
            label: 'Cancel',
            action: function (dialogRef) {
                doTidyClose["closeIt"](dialogRef);
            }
        },
            {
                icon: 'glyphicon glyphicon-trash',
                label: 'Delete',
                cssClass: 'btn-danger',
                action: function (dialogRef) {

                    csrftoken = $.cookie('csrftoken');
                    var target_ids = JSON.stringify(params.target_ids);

                    $.ajax({
                        url: copoFormsURL,
                        type: "POST",
                        headers: {
                            'X-CSRFToken': csrftoken
                        },
                        data: {
                            'task': "delete",
                            'component': params.component,
                            'target_ids': target_ids
                        },
                        success: function (data) {
                            do_render_table(data);
                        },
                        error: function () {
                            alert("Couldn't delete records!");
                        }
                    });

                    doTidyClose["closeIt"](dialogRef);

                }
            }
        ]
    });
}

function do_render_table(data) {
    var table = null;
    var lastRecord = null;
    var filterDivObject = null;
    var lengthDivObject = null;

    if ($.fn.dataTable.isDataTable('#' + data.table_data.table_id)) {
        //if table instance already exists, then this is probably a refresh after an CRUD operation
        table = $('#' + data.table_data.table_id).DataTable();
    }


    if (data.table_data.row_data) {
        //adding single record to table

        if (table) { //this test is probably redundant, but...you never can tell!
            //remove previously highlighted row
            table
                .rows('.row-insert-higlight')
                .nodes()
                .to$()
                .removeClass('row-insert-higlight');

            var rowNode = table
                .row.add(data.table_data.row_data)
                .draw()
                .node();

            //highlight new row
            $(rowNode)
                .addClass('row-insert-higlight')
                .animate({
                    color: 'black'
                });

            lastRecord = data.table_data.row_data;

        }
    } else {
        //probably first time rendering table, or maybe a call to refresh whole table, say after a delete action

        if (table) { //definitely a call to refresh table, as table instance exists!
            table.clear().draw();
            table.rows.add(data.table_data.dataSet); // Add new data
            table.columns.adjust().draw();
            return;
        }


        //get default ordering index;
        //ideally we would want to order by record creation date.
        //if it exists, it should be the last but one item in the columns list
        var orderIndx = 0;
        if (data.table_data.columns.length > 2) {
            orderIndx = data.table_data.columns.length - 2;
        }

        //custom column rendering
        var colDefs = [];

        //button coldefs
        var btnDef = {
            targets: -1,
            data: null,
            searchable: false,
            orderable: false,
            render: function (rdata) {
                var rndHTML = "";
                if (data.table_data.action_buttons.row_btns) {
                    var bTns = data.table_data.action_buttons.row_btns; //row buttons
                    rndHTML = '<span style="white-space: nowrap;">';
                    for (var i = 0; i < bTns.length; ++i) {
                        rndHTML += '<a data-action-target="row" data-record-action="' +
                            bTns[i].btnAction + '" data-record-id="' +
                            rdata[rdata.length - 1] +
                            '" data-toggle="tooltip" data-container="body" style="display: inline-block; white-space: normal;" title="' +
                            bTns[i].text + '" class="' + bTns[i].className + ' btn-xs"><i class="' +
                            bTns[i].iconClass + '"> </i><span></span></a>&nbsp;';
                    }
                    rndHTML += '</span>';
                }
                return rndHTML;
            }
        };

        colDefs.push(btnDef);

        //determine how columns are rendered - cols definition
        var custDef;
        var v = [];
        for (var i = 0; i < data.table_data.columns.length - 1; ++i) {
            v.push(i);
        }

        //exception for datafile table, it treats the first column differently
        if (data.table_data.table_id == 'datafile_table') {
            v.splice(0, 1);
        }

        custDef = {
            targets: v,
            data: data,
            render: function (data, type, row, meta) {
                var rndHTML = "";
                if (Object.prototype.toString.call(data[meta.col]) === '[object String]') {
                    rndHTML = data[meta.col];
                } else if (typeof data[meta.col] === "object") {
                    var collapseLink = data[data.length - 1] + "_" + meta.col;
                    rndHTML = get_data_item_collapse(collapseLink, get_data_list_panel(data[meta.col], collapseLink), data[meta.col].length);
                }

                return rndHTML;
            }
        };

        colDefs.push(custDef);


        //end cols definition

        //column def for datafile table
        if (data.table_data.table_id == 'datafile_table') {
            colDefs.push({
                targets: 0,
                data: null,
                render: function (rdata) {
                    var containerRow = $('<div/>', {
                        class: "row",
                        style: "margin-left:-10px; white-space: nowrap; margin-right: 5px;"
                    });

                    var metadataDiv = $('<div></div>')
                        .attr({
                            "class": "col-sm-1 col-md-1 col-lg-1 itemMetadata-flag",
                            "data-record-id": rdata[rdata.length - 1],
                            "style": "cursor: hand; cursor: pointer; display: inline-block;"
                        });

                    var spanPoor = $('<span/>', {
                        class: "itemMetadata-flag-ind meta-active poor",
                        style: "margin-top: 3px;"
                    });

                    var spanFair = $('<span/>', {
                        class: "itemMetadata-flag-ind fair"
                    });

                    var spanGood = $('<span/>', {
                        class: "itemMetadata-flag-ind good"
                    });

                    metadataDiv.append(spanPoor).append(spanFair).append(spanGood);

                    var dataDiv = $('<div></div>')
                        .attr({
                            "class": "col-sm-11 col-md-11 col-lg-11",
                            "style": "margin-left: -10px; margin-top: 10px; display: inline-block;"
                        });

                    var dataSpan = $('<span/>', {
                        html: rdata[0]
                    });

                    var descFlagSpan = $('<i></i>')
                        .attr({
                            "class": "fa fa-tags inDescription-flag",
                            "data-record-id": rdata[rdata.length - 1],
                            "data-toggle": "tooltip",
                            "style": "padding-left: 5px; display: none;",
                            "title": "Currently being described"
                        });

                    dataDiv.append(dataSpan).append(descFlagSpan);
                    containerRow.append(metadataDiv).append(dataDiv);

                    return $('<div></div>').append(containerRow).html();

                }
            });
        }

        var scrollX = true;

        if (data.table_data.table_id == "datafile_table") {
            //scroll has undesirable effect on this table
            scrollX = false;
        }

        table = $('#' + data.table_data.table_id).DataTable({
            data: data.table_data.dataSet,
            columns: data.table_data.columns,

            paging: true,
            ordering: true,
            scrollX: scrollX,
            lengthChange: true,
            order: [
                [orderIndx, "desc"]
            ],
            select: {
                style: 'multi'
            },
            dom: 'lf<"row button-rw">rtip',
            "fnDrawCallback": function (oSettings) {
                refresh_tool_tips();

                $('.dataTables_filter').each(function () {
                    if ($(this).attr("id") == data.table_data.table_id + "_filter") {
                        filterDivObject = $(this);
                        return false;
                    }
                });

                $('.dataTables_length').each(function () {
                    if ($(this).attr("id") == data.table_data.table_id + "_length") {
                        lengthDivObject = $(this);
                        return false;
                    }
                });

                //trigger metadata refresh for datafiles
                if (data.table_data.table_id == 'datafile_table') {
                    var event = jQuery.Event("refreshmetadataevents");
                    $('body').trigger(event);
                }

            },
            columnDefs: colDefs
        });

        //attach global action buttons
        if (data.table_data.action_buttons.global_btns) {
            var custBtns = data.table_data.action_buttons.global_btns; //global buttons
            var actBtns = ['selectAll', 'selectNone'];
            var bTns = custBtns.concat(actBtns);
            new $.fn.dataTable.Buttons(table, {
                buttons: bTns
            });

            table
                .buttons()
                .nodes()
                .each(function (value) {
                    $(this).addClass(' btn-sm');
                });

            table
                .buttons('.copo-dt')
                .nodes()
                .each(function (value) {
                    var btnImage;
                    for (var i = 0; i < bTns.length; ++i) {
                        if (bTns[i].text == this.text) {
                            btnImage = bTns[i];
                            break;
                        }
                    }

                    $(this).removeClass('btn-default'); //remove default class
                    $(this).addClass(this.className); //attach supplied class
                    $(this).attr('data-record-action', btnImage.btnAction); //data attribute to signal action type
                    $(this).attr('data-action-target', 'rows'); //data attribute to signal batch action
                    $(this).attr('data-copo-tour-id', data.table_data.table_id + "_" + btnImage.btnAction); //quick tour component: table_id + action type
                    //
                    ////attach icon to button
                    try {
                        $('<i class="' + bTns[value].iconClass + '">&nbsp;</i>').prependTo($(this));
                    } catch (err) {
                    }

                });

            $("div.button-rw").append(filterDivObject);
            $("div.button-rw").append(lengthDivObject);
            $("div.button-rw").append($(table.buttons().container()));
            $(lengthDivObject).addClass("pad-it");


        }

        //create a hook for attaching button events in individual table handlers
        if ($.fn.dataTable.isDataTable('#' + data.table_data.table_id)) {
            var tableID = data.table_data.table_id;
            var event = jQuery.Event("addbuttonevents");
            event.tableID = tableID;
            $('body').trigger(event);
        }

    }


    //handle requests for specific tables...
    if (data.table_data.table_id == "datafile_table") {
        table = $('#' + data.table_data.table_id).DataTable();
        if (table && lastRecord) { //trigger event for queuing record
            var event = jQuery.Event("addtoqueue");
            event.recordLabel = lastRecord[0];
            event.recordID = lastRecord[lastRecord.length - 1];
            $('body').trigger(event);
        }
    }

} //end of function


function refresh_tool_tips() {
    $("[data-toggle='tooltip']").tooltip();
    $("[data-toggle='popover']").popover();
    $('.ui.dropdown')
        .dropdown()
    ;
    $('.copo-tooltip')
        .popup()
    ;

    apply_color();
    refresh_selectbox();
    refresh_select2box();
    refresh_multiselectbox();
    refresh_multiselect2box();
    refresh_singleselectbox();
    refresh_multisearch();
    refresh_ontology_select();
    refresh_general_ontology_search();
    refresh_general_ontology_select();
    refresh_copo_lookup();
    refresh_copo_lookup2();

    refresh_range_slider();
    auto_complete();

    setup_datepicker();

} //end of func

function setup_datepicker() {
    var format_string
    // dtol date format and ENA date formats are sadly different, so check if we are dealing with a dtol sample
    if ($(document).data("isDtolSamplePage")) {
        format_string = "yyyy-mm-dd"
    } else {
        format_string = "dd/mm/yyyy"
    }
    $('.date-picker').datepicker({
        format: format_string
    });
}


function refresh_validator(formObject) {
    formObject.validator('update');

} //end of func

function refresh_range_slider() {
    $('.range-slider').each(function () {
        var elem = $(this);

        var outputElem = elem.closest(".range-slider-parent").find(".range-slider-output");
        var elemValue = elem.closest(".range-slider-parent").find(".elem-value");

        elem.rangeslider({

            // Feature detection the default is `true`.
            // Set this to `false` if you want to use
            // the polyfill also in Browsers which support
            // the native <input type="range"> element.
            polyfill: false,

            // Default CSS classes
            rangeClass: 'rangeslider',
            disabledClass: 'rangeslider--disabled',
            horizontalClass: 'rangeslider--horizontal',
            verticalClass: 'rangeslider--vertical',
            fillClass: 'rangeslider__fill',
            handleClass: 'rangeslider__handle',

            // Callback function
            onInit: function () {
            },

            // Callback function
            onSlide: function (position, value) {
                outputElem.html(value);
            },

            // Callback function
            onSlideEnd: function (position, value) {
                outputElem.html(value);
                elemValue.val(value);
            }
        });
    });

} //end of function


//refreshes selectboxes to pick up events
function refresh_selectbox() {
    $('.copo-select').each(function () {
        var elem = $(this);

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

//refreshes selectboxes to pick up events
function refresh_select2box() {
    $('.copo-select2').each(function () {
        var elem = $(this);

        if (!elem.hasClass("select2-hidden-accessible")) {
            elem.select2({
                tags: true,
                data: JSON.parse(elem.attr("data-currentValue")),
                // dropdownParent: $(this).closest(".copo-form-group")
            });
        }

    });

} //end of function

function refresh_multiselect2box() {
    $('.copo-multi-select2').each(function () {
        var elem = $(this);

        if (!elem.hasClass("select2-hidden-accessible")) {
            elem.select2({
                data: JSON.parse(elem.attr("data-optionsList")),
                maximumSelectionLength: elem.attr("data-maximumSelectionLength"),
                // dropdownParent: $(this).closest(".copo-form-group")
            });

            elem.val(JSON.parse(elem.attr("data-currentValue")));
            elem.trigger('change');
        }

    });

} //end of function


function refresh_singleselectbox() {
    $('.copo-single-select').each(function () {
        var elem = $(this);

        if (!elem.hasClass("select2-hidden-accessible")) {
            elem.select2({
                data: JSON.parse(elem.attr("data-optionsList")),
                dropdownParent: $(this).closest(".copo-form-group"),
                escapeMarkup: function (markup) {
                    return markup;
                }, // let our custom formatter work
                templateResult: function (state) {
                    if (!state.id) {
                        return state.text;
                    }

                    var descr = state.description || '';
                    var $state = $('<span>' + state.text + '</span>');

                    if (descr) {
                        var item = $('<i class="ui grey icon info circle" style="margin-left: 15px;"></i>');
                        item.webuiPopover('destroy');
                        item.webuiPopover({
                            content: '<div class="webpop-content-div">' + descr + '</div>',
                            arrow: true,
                            width: 200,
                            trigger: 'hover',
                        });
                        $state.append(item);
                    }

                    return $state;
                }
            });

            elem.val(JSON.parse(elem.attr("data-currentValue")));
            elem.trigger('change');
        }

    });

} //end of function

function refresh_copo_lookup2() {
    var profile_id = '';
    if ($('#profile_id').length) {
        profile_id = $('#profile_id').val();
    }

    $('.copo-lookup2').each(function () {
        var elem = $(this);

        if (!elem.hasClass("select2-hidden-accessible")) {
            elem.select2({
                maximumSelectionLength: elem.attr("data-maximumSelectionLength"),
                data: JSON.parse(elem.attr("data-currentValue")),
                dropdownParent: $(this).closest(".copo-form-group"),
                ajax: {
                    url: elem.attr("data-url"),
                    dataType: 'json',
                    type: "GET",
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    delay: 250,
                    data: function (params) {
                        return {
                            q: params.term, // search term
                            'profile_id': profile_id,
                            'referenced_field': elem.attr("data-ref")
                        };
                    },
                    processResults: function (data) {
                        var res = data.result.map(function (item) {
                            var serverSide = false;
                            if (item.hasOwnProperty('server-side')) {
                                serverSide = item['server-side'];
                            }
                            return {
                                id: item.accession,
                                text: item.label,
                                serverSide: serverSide,
                                url: elem.attr("data-url")
                            };
                        });
                        return {
                            results: res
                        };
                    },
                    cache: true
                },
                minimumInputLength: 1,
                escapeMarkup: function (markup) {
                    return markup;
                }, // for our custom formatter to work
                templateResult: function (state) {
                    var $state = $('<span  data-id="' + state.id + '" data-server="' + state.serverSide + '" data-url="' + state.url + '" class="parentSpan">' + state.text + '</span>');

                    var item = $('<i class="ui grey icon info server-desc circle" style="margin-left: 15px;"></i>');

                    item.webuiPopover('destroy');
                    item.webuiPopover({
                        content: '<div class="webpop-content-div"></div>',
                        arrow: true,
                        width: 200,
                        trigger: 'hover',
                    });

                    $state.append(item);
                    return $state;

                    //return '<span data-id="' + state.id + '" data-server="' + state.serverSide + '" data-url="' + state.url + '" class="copo-select2-info select2-minfo">' + state.text + '</span>';
                }
            });

            selectizeObjects[elem.attr("id")] = elem;
        }

    });

} //end of function

function refresh_multiselectbox() {
    $('.copo-multi-select').each(function () {
        var elem = $(this);
        var valueElem = elem.closest('.ctrlDIV').find('.copo-multi-values');
        var maxTems = 'null'; //maximum selectable items

        var parentID = valueElem.attr("id");

        if (valueElem.is("[data-maxItems]")) {
            maxTems = valueElem.attr("data-maxItems");
        }

        if (!(/selectize/i.test(elem.attr('class')))) { // if not already instantiated
            var $funSelect = elem.selectize({
                onChange: function (value) {
                    if (value) {
                        valueElem.val(value)
                            .trigger('change');
                    } else {
                        valueElem.val("");
                    }
                },
                //dropdownParent: 'body',
                maxItems: maxTems,
                plugins: ['remove_button']
            });

            //set default values
            var control = $funSelect[0].selectize;
            control.setValue(valueElem.val().split(",")); //set default value

            //retain reference to control for any future reference
            selectizeObjects[parentID] = control;
        }
    });
}

function refresh_copo_lookup() {
    $('.copo-lookup').each(function () {
        var elem = $(this);
        var url = elem.attr("data-url");
        var valueElem = elem.closest('.ctrlDIV').find('.copo-multi-values');
        var elemSpecs = JSON.parse(elem.closest('.ctrlDIV').find('.elem-json').val());

        var maxTems = 'null'; //maximum selectable items
        if (valueElem.is("[data-maxItems]")) {
            maxTems = valueElem.attr("data-maxItems");
        }

        var options = [];

        var profile_id = '';
        if ($('#profile_id').length) {
            profile_id = $('#profile_id').val();
        }

        if (elemSpecs.length > 0) {
            elemSpecs.forEach(function (item) {
                if (item.accession == valueElem.val())
                    options.push(item);
            });
        }

        if (!(/selectize/i.test(elem.attr('class')))) { // if not already instantiated
            var $funSelect = elem.selectize({
                onChange: function (value) {
                    if (value) {
                        valueElem.val(value)
                            .trigger('change');
                    } else {
                        valueElem.val("");
                    }

                    WebuiPopovers.hideAll();
                },
                onBlur: function () {
                    WebuiPopovers.hideAll();
                },
                maxItems: maxTems,
                create: false,
                plugins: ['remove_button'],
                valueField: 'accession',
                labelField: 'label',
                searchField: 'label',
                options: options,
                render: {
                    option: function (item, escape) {
                        var desc = escape(item.description);
                        var accession = escape(item.accession);
                        var label = escape(item.label);
                        var serverSide = false;
                        if (item.hasOwnProperty('server-side')) {
                            serverSide = item['server-side'];
                        }

                        return '<div>' +
                            '<span  data-serverside="' + serverSide + '" data-url="' + url + '" data-accession="' + accession + '"  data-label="' + label + '" data-desc="' + desc + '" class="webpop-content-div ontology-label lookup-label">' + escape(item.label) + '</span></div>';

                    }
                },
                load: function (query, callback) {
                    if (!query.length) return callback();
                    this.clearOptions();        // clear the data
                    this.renderCache = {};      // clear the html template cache
                    $.ajax({
                        url: url,
                        type: "POST",
                        headers: {
                            'X-CSRFToken': csrftoken
                        },
                        data: {
                            q: query,
                            'profile_id': profile_id
                        },
                        success: function (data) {
                            var items = [];

                            if (data.hasOwnProperty('result') && data.result.length > 0) {
                                items = data.result;
                            }

                            callback(items);
                        },
                        error: function () {
                            callback();
                        }
                    });
                }
            });

            //reference to selectize object
            var control = $funSelect[0].selectize;

            //set default values
            if (options.length) {
                for (var p in control.options) {
                    control.setValue(p); //set default value
                }
            }

            //retain reference to control for any future reference
            selectizeObjects[valueElem.attr("id")] = control;
        }
    });
}

function refresh_ontology_select() {
    $('.onto-select').each(function () {
        var elem = $(this);
        var url = elem.attr("data-url");
        var options = [];
        var defaultValue = {};

        var parentID = elem.closest(".ontology-parent").find(".ontology-field-hidden").attr("id");

        //set previous value
        elem.closest(".ontology-parent").find(".ontology-field-hidden").each(function () {
            defaultValue[$(this).attr("data-key")] = $(this).val();
        });

        if (defaultValue.hasOwnProperty('annotationValue') && defaultValue.annotationValue.trim() != '') {
            var option = {};
            option.labelblank = defaultValue.annotationValue
            if (option.labelblank.length > 9) {
                option.labelblank = option.labelblank.substr(0, 9) + "...";
            }
            option.label = defaultValue.annotationValue;
            option.ontology_prefix = defaultValue.termSource;
            option.iri = defaultValue.termAccession;
            option.description = defaultValue.comments;
            option.copo_values = JSON.stringify({
                'termAccession': defaultValue.termAccession,
                'termSource': defaultValue.termSource,
                'annotationValue': defaultValue.annotationValue,
                'comments': defaultValue.comments
            });

            options.push(option);
        }

        if (!(/selectize/i.test(elem.attr('class')))) { // if not already instantiated
            var $funSelect = elem.selectize({
                onChange: function (value) {
                    if (value) {
                        try {
                            value = JSON.parse(value);
                            //set value
                            var setValue = '';

                            if (typeof value === "object") {
                                elem.closest(".ontology-parent").find(".ontology-field-hidden").each(function () {
                                    var dataKey = $(this).attr("data-key");
                                    $(this).val(value[dataKey]);
                                });
                                setValue = value.annotationValue;
                            } else {
                                // a string slipped through - apparently numbers can be parsed to JSON
                                elem.closest(".ontology-parent").find(".ontology-field-hidden").each(function () {
                                    var dataKey = $(this).attr("data-key");

                                    $(this).val('');

                                    if (dataKey == 'annotationValue') {
                                        $(this).val(value);
                                        setValue = value;
                                    }
                                });
                            }

                            //set display
                            elem.closest(".ontology-parent").find(".onto-label").find("span.onto-label-span").html(setValue);
                        } catch (e) {

                            //likely an unresolved or free-text entry - set only annotationValue, all others to empty
                            elem.closest(".ontology-parent").find(".ontology-field-hidden").each(function () {
                                var dataKey = $(this).attr("data-key");

                                $(this).val('');

                                if (dataKey == 'annotationValue') {
                                    $(this).val(value);
                                }

                            });

                            //set display
                            elem.closest(".ontology-parent").find(".onto-label").find("span.onto-label-span").html(value);
                        }

                    } else {

                        //unset values
                        elem.closest(".ontology-parent").find(".ontology-field-hidden").each(function () {
                            $(this).val('');
                        });

                        //unset display
                        elem.closest(".ontology-parent").find(".onto-label").find("span.onto-label-span").html('');
                    }

                    WebuiPopovers.hideAll();
                    set_ontology_icon(elem, $funSelect[0].selectize.getValue());
                },
                onBlur: function () {
                    WebuiPopovers.hideAll();
                },
                maxItems: '1',
                create: true,
                plugins: ['remove_button'],
                valueField: 'copo_values',
                labelField: 'labelblank',
                searchField: 'label',
                options: options,
                render: {
                    option: function (item, escape) {
                        var desc = escape(item.description) != "undefined" ? escape(item.description) : ' ';
                        var prefix = escape(item.ontology_prefix) != "undefined" ? escape(item.ontology_prefix) : '';
                        var accession = escape(item.iri);
                        var label = escape(item.label);

                        return '<div>' +
                            '<span data-accession="' + accession + '"  data-label="' + label + '"data-prefix="' + prefix + '" data-desc="' + desc + '" class="webpop-content-div ontology-label onto-label">' + prefix + (prefix ? ': ' : "") + escape(item.label) + '</span></div>';

                    }
                },
                load: function (query, callback) {
                    if (!query.length) return callback();
                    this.clearOptions();        // clear the data
                    this.renderCache = {};      // clear the html template cache
                    $.ajax({
                        url: url,
                        type: 'GET',
                        dataType: 'json',
                        data: {
                            q: query
                        },
                        error: function () {
                            callback();
                        },
                        success: function (data) {
                            var ontologies = [];

                            data.response.docs.forEach(function (item) {
                                item.copo_values = JSON.stringify({
                                    'termAccession': item.iri,
                                    'termSource': item.ontology_prefix,
                                    'annotationValue': item.label,
                                    'comments': item.description
                                });

                                item.labelblank = item.label;

                                if (item.labelblank.length > 9) {
                                    item.labelblank = item.labelblank.substr(0, 9) + "...";
                                }

                                ontologies.push(item);
                            });

                            callback(ontologies);
                        }
                    });
                }
            });

            //reference to selectize object
            var control = $funSelect[0].selectize;

            //set default values
            if (options.length) {
                for (var p in control.options) {
                    control.setValue(p); //set default value
                }
            }

            set_ontology_icon(elem, control.getValue());

            //retain reference to control for any future reference
            selectizeObjects[parentID] = control;

        }
    });
}


function refresh_general_ontology_search() {
    //this control supports remote data source
    $('.general-onto-search').each(function () {
        var elem = $(this);
        var url = elem.attr("data-url");
        var elemId = elem.attr("data-element");
        var eventName = elem.attr("data-eventname");
        var api_schema = JSON.parse(elem.closest('.copo-form-group').find('.elem-fields').val());
        var call_params = JSON.parse(elem.closest('.copo-form-group').find('.elem-params').val());

        var options = [];

        if (!(/selectize/i.test(elem.attr('class')))) { // if not already instantiated
            var $funSelect = elem.selectize({
                onChange: function (selectedValue) {
                    //set value in hidden fields

                    var ontologySpan = elem.closest(".ontology-parent");
                    ontologySpan.find(".ontology-field-hidden").remove();
                    var valueObject = {};

                    if (selectedValue) {
                        var schema = JSON.parse(ontologySpan.find(".elem-fields").val());

                        try {
                            valueObject = $funSelect[0].selectize.options[selectedValue];
                            for (var i = 0; i < schema.length; ++i) {
                                var fv = schema[i];
                                ontologySpan.append($('<input/>',
                                    {
                                        type: "hidden",
                                        class: "ontology-field-hidden",
                                        id: elemId + "." + fv.id,
                                        name: elemId + "." + fv.id,
                                        value: valueObject[fv.id]
                                    }));
                            }

                        } catch (e) {
                            console.log("Couldn't retrieve control value object [value, parent id]: [" + indx + "," + parentid + "]");
                        }

                    }

                    WebuiPopovers.hideAll();
                    set_general_ontology_detail(elem, valueObject);

                    //trigger event to be handled externally
                    if (eventName) {
                        let controlEvent = jQuery.Event(eventName);
                        controlEvent.elementId = elemId;
                        controlEvent.selectedValue = selectedValue;
                        $('body').trigger(controlEvent);
                    }

                },
                onBlur: function () {
                    WebuiPopovers.hideAll();
                },
                score: function () {
                    return function () {
                        return 1; //this enables all options to be listed on upon search return
                    };
                },
                maxItems: '1',
                create: false,
                plugins: ['remove_button'],
                valueField: 'copo_idblank',
                labelField: 'copo_labelblank',
                searchField: 'copo_labelblank',
                options: options,
                sortField: [
                    {field: 'copo_labelblank', direction: 'asc'},
                ],
                render: {
                    option: function (item, escape) {

                        return '<div>' +
                            '<span data-lblfield="copo_labelblank" data-parentid="' + elemId + '"  data-indx="' + escape(item.copo_idblank) + '"  class="webpop-content-div ontology-label onto-label">' + escape(item.copo_labelblank) + '</span></div>';

                    },
                    item: function (item, escape) {
                        var lbl = escape(item.copo_labelblank);
                        if (lbl.length > 9) {
                            lbl = escape(item.copo_labelblank).substr(0, 9) + "...";
                        }
                        return '<div><span>' + lbl + '</span></div>'
                    }
                },
                load: function (query, callback) {
                    this.clearOptions();        // clear the data
                    this.close();
                    WebuiPopovers.hideAll();
                    this.renderCache = {};
                    query = query.trim();

                    if (!query.length) {
                        report_call_feedback(elem, "No query term entered", "success");
                        return callback();
                    }

                    var params = {q: query};
                    if (call_params) {
                        params = $.extend(params, call_params);
                    }
                    params.api_schema = JSON.stringify(api_schema);
                    $.ajax({
                        url: url,
                        type: 'GET',
                        dataType: 'json',
                        data: params,
                        error: function () {
                            callback();
                        },
                        success: function (data) {
                            var ontologies = [];

                            if (data.hasOwnProperty('message')) {
                                report_call_feedback(elem, data.message, data.status);
                            }

                            if (data.hasOwnProperty('api_schema')) { //backened is sending a schema, retain this
                                elem.closest(".ontology-parent").find(".elem-fields").val(JSON.stringify(data.api_schema));
                            }

                            if (data.hasOwnProperty('status') && data.status == 'success') {
                                ontologies = data.items;
                            }

                            callback(ontologies);
                        }
                    });
                }
            });

            //reference to selectize object
            selectizeObjects[elemId] = $funSelect[0].selectize;
        }
    });
}

function refresh_general_ontology_select() {
    //this control works on predefined options and doesn't support remote data source, or dynamic updates to options
    $('.general-onto-select').each(function () {
        var elem = $(this);
        var elemId = elem.attr("data-element");
        var eventName = elem.attr("data-eventname");
        var options = JSON.parse(elem.closest('.copo-form-group').find('.elem-options').val());

        var idField = 'copo_idblank';
        var labelField = 'copo_labelblank';

        if (elem.attr('data-idField')) {
            idField = elem.attr("data-idField");
        }

        if (elem.attr('data-labelField')) {
            labelField = elem.attr("data-labelField");
        }

        if (!(/selectize/i.test(elem.attr('class')))) { // if not already instantiated
            var $funSelect = elem.selectize({
                onChange: function (selectedValue) {
                    //set value in hidden fields

                    var ontologySpan = elem.closest(".ontology-parent");
                    ontologySpan.find(".ontology-field-hidden").remove();
                    var valueObject = {};

                    var valElem = document.getElementById(elemId);
                    if (selectedValue) {

                        valElem.value = selectedValue;

                        valueObject = $funSelect[0].selectize.options[selectedValue];
                    } else {
                        valElem.value = '';
                    }

                    WebuiPopovers.hideAll();
                    set_general_ontology_detail(elem, valueObject);

                    //trigger event to be handled externally
                    if (eventName) {
                        let controlEvent = jQuery.Event(eventName);
                        controlEvent.elementId = elemId;
                        controlEvent.selectedValue = selectedValue;
                        $(document).trigger(controlEvent);
                    }

                },
                onBlur: function () {
                    WebuiPopovers.hideAll();
                },
                score: function () {
                    return function () {
                        return 1; //this enables all options to be listed on upon search return
                    };
                },
                maxItems: '1',
                create: false,
                plugins: ['remove_button'],
                valueField: idField,
                labelField: labelField,
                searchField: labelField,
                options: options,
                sortField: [
                    {field: labelField, direction: 'asc'},
                ],
                render: {
                    option: function (item, escape) {

                        return '<div>' +
                            '<span data-lblfield="' + labelField + '"  data-parentid="' + elemId + '"  data-indx="' + escape(item[idField]) + '"  class="webpop-content-div ontology-label onto-label">' + escape(item[labelField]) + '</span></div>';

                    },
                    item: function (item, escape) {
                        var lbl = escape(item[labelField]);
                        if (lbl.length > 9) {
                            lbl = escape(item[labelField]).substr(0, 9) + "...";
                        }
                        return '<div><span>' + lbl + '</span></div>'
                    }
                },
            });

            var control = $funSelect[0].selectize;
            selectizeObjects[elem.attr("data-element")] = control;

            //report options tally
            var message = options.length + " option in list";
            if (options.length != 1) {
                message = options.length + " options in list";
            }

            report_call_feedback(elem, message, "success");

            //set value
            var elemValue = elem.attr("data-currentValue");
            if (elemValue) {
                for (var p in control.options) {
                    if (elemValue == p) {
                        control.setValue(p);
                    }
                }
            }
        }
    });
}

function report_call_feedback(elem, feedback, status) {
    var iconNode = elem.closest(".ontology-parent").find(".copo-tag");
    var contentNode = elem.closest(".ontology-parent").find(".copo-tag-2");
    iconNode.html("Feedback...");

    contentNode.html(feedback);

    iconNode.removeClass("green red blue");

    if (status == "error") {
        iconNode.addClass("red");
        iconNode.html("Error");
    } else if (status == "success") {
        iconNode.addClass("blue");
    }
}

function set_general_ontology_detail(elem, onto_value) {
    var contentNode = elem.closest(".ontology-parent").find(".copo-tag-content");
    contentNode.hide();

    var iconNode = elem.closest(".ontology-parent").find(".copo-tag");
    iconNode.removeClass("green red blue");

    if ($.isEmptyObject(onto_value)) {
        contentNode.html("No option selected");
        return false;
    }

    var schema = JSON.parse(elem.closest(".ontology-parent").find(".elem-fields").val());
    var result = $('<div/>',
        {
            class: "limit-text"
        });

    contentNode.html(result);

    let message = $('<div class="webpop-content-div" style="padding: 5px;"></div>');
    var codeList = $('<div class="ui relaxed divided list"></div>');

    message.append(codeList);

    for (var i = 0; i < schema.length; ++i) {
        var schemaNode = schema[i];
        if (schemaNode.hasOwnProperty("show_in_table") && (schemaNode.show_in_table.toString().toLowerCase() == "true")) {
            var itemNode = $('<div class="item"></div>');
            codeList.append(itemNode);
            itemNode.append('<div class="content"><div class="header">' + schemaNode.label + '</div><div class="description webpop-content-div">' + onto_value[schemaNode.id] + '</div></div>');
        }
    }

    result.append(message);
    iconNode.html("Click for info...");
    iconNode.addClass("green");
    // contentNode.slideToggle("slow");
}


function set_ontology_icon(elem, onto_object) {
    //function sets an appropriate icon depending on ontology or free-text value state
    var freeText = 'Value not set or free-text value not resolved to an ontology';

    try {
        onto_object = JSON.parse(onto_object);


        if (typeof onto_object === "object" && onto_object.termAccession != "") {
            elem.closest(".ontology-parent").find(".onto-label").find(".free-text").hide();
            elem.closest(".ontology-parent").find(".onto-label").find(".non-free-text").show();
            elem.closest(".ontology-parent").find(".onto-label").prop('title', 'Ontology field - click for info');
            elem.closest(".ontology-parent").find(".onto-label").find(".onto-label-more").html("").append("<div></div>");

            elem.closest(".ontology-parent").find(".onto-label").find(".onto-label-more").append('<div style="margin-top: 5px;">Ontology source: ' + onto_object.termSource + '</div> ');
            elem.closest(".ontology-parent").find(".onto-label").find(".onto-label-more").append('<a href="' + onto_object.termAccession + '" target="_blank">' + onto_object.termAccession + '</a> ');


        } else {
            elem.closest(".ontology-parent").find(".onto-label").find(".free-text").show();
            elem.closest(".ontology-parent").find(".onto-label").find(".non-free-text").hide();
            elem.closest(".ontology-parent").find(".onto-label").prop('title', freeText);
        }
    } catch (e) {
        elem.closest(".ontology-parent").find(".onto-label").find(".free-text").show();
        elem.closest(".ontology-parent").find(".onto-label").find(".non-free-text").hide();
        elem.closest(".ontology-parent").find(".onto-label").prop('title', freeText);
    }
}


function refresh_multisearch() {
    $('.copo-multi-search').each(function () {
        var elem = $(this);

        if (!(/selectize/i.test(elem.attr('class')))) { // if not already instantiated
            var valueElem = elem.closest('.copo-form-group').find('.copo-multi-values');
            var elemSpecs = JSON.parse(elem.closest('.copo-form-group').find('.elem-json').val());
            var maxTems = 'null'; //maximum selectable items
            var component = elem.attr("data-component");

            if (valueElem.is("[data-maxItems]")) {
                maxTems = valueElem.attr("data-maxItems");
            }

            var $funSelect = elem.selectize({
                onChange: function (value) {
                    if (value) {
                        valueElem.val(value)
                            .trigger('change');
                    } else {
                        valueElem.val("");
                    }

                    $(".selectize-control.copo-multi-search").closest(".copo-form-group").webuiPopover('destroy');

                },
                onBlur: function () {
                    $(".selectize-control.copo-multi-search").closest(".copo-form-group").webuiPopover('destroy');
                },
                // dropdownParent: 'body',
                maxItems: maxTems,
                persist: true,
                create: false,
                plugins: ['remove_button'],
                valueField: elemSpecs.value_field,
                labelField: elemSpecs.label_field,
                searchField: elemSpecs.search_field,
                options: elemSpecs.options,
                render: {
                    item: function (item, escape) {
                        return '<div>' +
                            (item[elemSpecs.label_field] ? '<span>' +
                                escape(item[elemSpecs.label_field]) + '</span>' : '') +
                            '</div>';
                    },
                    option: function (item, escape) {
                        var label = ''; // item[elemSpecs.label_field];
                        var caption = '<div>';
                        for (var i = 0; i < elemSpecs.secondary_label_field.length; ++i) {
                            caption += '<div>' + item[elemSpecs.secondary_label_field[i]] + '</div>';
                        }
                        caption += "</div>";

                        return '<div>' +
                            '<span class="caption caption-component" data-component="' + component + '">' + escape(label) + '</span>' +
                            (caption ? '<div class="caption">' + caption + '</div>' : '') +
                            '</div>';
                    }
                }
            });


            var control = $funSelect[0].selectize;
            control.setValue(valueElem.val().split(",")); //set default value

            //retain reference to control for any future reference
            selectizeObjects[valueElem.attr("id")] = control;
        }

    });
}


var auto_complete = function () {

    // remove all previous autocomplete divs
    $('.autocomplete').remove()
    AutoComplete({
        EmptyMessage: "No Annotations Found",
        Url: $("#elastic_search_ajax").val(),
        _Select: do_select,
        _Render: do_post,
        _Position: do_position,
        _Pre: do_pre,
    }, '.ontology-field')

    function do_pre() {
        // make loading spinner visible before request to OLS
        $(this.Input).siblings(".input-group-addon").css("visibility", "visible")
        // we can also make changes to the value sent OLS here if needs be
        return this.Input.value;
    }

    function do_select(item) {
        if ($(document).data('annotator_type') == 'txt') {
            $('#annotator-field-0').val($(item).data('annotation_value') + ' :-: ' + $(item).data('term_accession'));
        } else if ($(document).data('annotator_type') == 'ss') {
            // this function defined in copo_annotations.js
            append_to_annotation_list(item)
        } else {
            $(this.Input).val($(item).data('annotation_value'));
            $(this.Input).closest(".ontology-parent").find("[id*='termSource']").val($(item).data('term_source'));
            $(this.Input).closest(".ontology-parent").find("[id*='termAccession']").val($(item).data('term_accession'));
        }

    }

    function do_position(a, b, c) {

    }


    function do_post(response) {
        response = JSON.parse(response);

        console.log("num_found " + response.response.numFound);
        var properties = Object.getOwnPropertyNames(response);
        //Try parse like JSON data

        var empty,
            length = response.length,
            li = document.createElement("li"),
            ul = document.createElement("ul");


        for (var item in response.response.docs) {

            doc = response.response.docs[item];


            try {
                //
                //console.log(response.highlighting[doc.id])
                //console.log(doc)
                var s;
                s = response.highlighting[doc.id].label_autosuggest[0];
                if (s == undefined) {
                    s = response.highlighting[doc.id].synonym
                }
                var short_form;
                var desc = doc.description
                if (desc == undefined) {
                    desc = "Description Not Available";
                }
                if (doc.ontology_prefix == undefined) {
                    short_form = "Origin Unknown";
                } else {
                    short_form = doc.ontology_prefix
                }
                li.innerHTML = '<span title="' + doc.iri + " - " + desc + '" class="ontology-label label label-info"><span class="ontology-label-text"><img src="/static/copo/img/ontology.png"/>' + doc.ontology_prefix + ' : ' + s + ' ' + '</span>' + ' - ' + '<span class="ontology-description">' + desc + '</span></span>';


                $(li).attr('data-id', doc.id);
                var styles = {
                    margin: "2px",
                    marginTop: '4px',
                    fontSize: "large",

                };
                $(li).css(styles);
                $(li).attr('data-term_accession', doc.iri);

                $(li).attr('data-annotation_value', doc.label);

                $(li).attr('data-term_source', short_form);
                //$(li).attr("data-autocomplete-value", response.highlighting[item].label_autosuggest[0].replace('<b>', '').replace('</b>', '') + ' - ' + item);

                //console.log($(li).data('label'))

                ul.appendChild(li);
                li = document.createElement("li");
            } catch (err) {
                console.log(err);
                li = document.createElement("li");
            }
        }
        $(this.DOMResults).empty()
        this.DOMResults.append(ul)
        $(this.Input).siblings(".input-group-addon").css("visibility", "hidden")
    }

} //end of function

function isInArray(value, array) {
    //checks if a value is in array
    return array.indexOf(value) > -1;
}

function get_data_list_panel(itemData, link) {
    if (!itemData) {
        return "";
    }

    var containerFuild = $('<div/>', {
        class: "container-fluid",
    });

    var containerRow = $('<div/>', {
        class: "row",
        style: "padding:1px;"
    });

    var containerColumn = $('<div/>', {
        class: "col-sm-12 col-md-12 col-lg-12",
        style: "padding:1px;"
    });

    var mainMenuDiv = $('<div/>', {
        id: "mainMenu_" + link,
    });

    var listGroupPanel = $('<div/>', {
        class: "list-group panel",
        style: "margin-bottom: 0px; border: 0 solid transparent;"
    });

    var topLevelLink = $('<a></a>')
        .attr({
            "href": "#demo3",
            "class": "list-group-item",
            "data-toggle": "collapse",
            "data-parent": "#MainMenu",
            "style": "background: #ebf0fa;"
        });


    var topLevelDiv = $('<div/>', {
        class: "collapse"
    });


    var subMenuLink = $('<a/>', {
        href: "#",
        class: "list-group-item",
        click: function (event) {
            event.preventDefault();
            return false;
        }
    });


    if (Object.prototype.toString.call(itemData) === '[object Array]') {
        $.each(itemData, function (key, val) {
            if (Object.prototype.toString.call(val) === '[object String]') {
                var ctrlElem = subMenuLink.clone();
                ctrlElem.html(val);
                listGroupPanel.append(ctrlElem);
            } else if (Object.prototype.toString.call(val) === '[object Array]') {
                var ctrlElemLink = topLevelLink.clone();
                ctrlElemLink.attr("href", "#rec_" + link + "_" + key);
                ctrlElemLink.html('<span>Item ' + (key + 1) + '</span><i class="fa fa-caret-down pull-right"></i>');

                listGroupPanel.append(ctrlElemLink);

                var ctrlElemDiv = topLevelDiv.clone();
                ctrlElemDiv.attr("id", "rec_" + link + "_" + key);
                ctrlElemDiv.attr("class", "collapse");

                $.each(val, function (key2, val2) {
                    var spl = [];
                    var displayedValue = "";
                    var ctrlElemSubLink = subMenuLink.clone();
                    if (Object.prototype.toString.call(val2) === '[object String]') {
                        displayedValue = val2;
                    } else if (Object.prototype.toString.call(val2) === '[object Array]') {
                        $.each(val2, function (key22, val22) {
                            spl.push(val22);
                        });
                        displayedValue = spl.join("<br/>");

                        if (key2 == 0) {
                            ctrlElemLink.find("span").html(displayedValue);
                            displayedValue = "";
                        }
                    } else if (Object.prototype.toString.call(val2) === '[object Object]') {
                        Object.keys(val2).forEach(function (k2) {
                            spl.push(k2 + ": " + val2[k2]);
                        });

                        displayedValue = spl.join("<br/>");

                        if (key2 == 0) {
                            ctrlElemLink.find("span").html(displayedValue);
                            displayedValue = "";
                        }
                    }

                    if (displayedValue) {
                        ctrlElemSubLink.html(displayedValue);
                        ctrlElemDiv.append(ctrlElemSubLink);
                    }

                });


                listGroupPanel.append(ctrlElemDiv);

            } else if (Object.prototype.toString.call(val) === '[object Object]') {
            }
        });

    } else if (Object.prototype.toString.call(itemData) === '[object Object]') {
        //not an array-type object
        $.each(itemData, function (key, val) {
            var ctrlElem = subMenuLink.clone();
            ctrlElem.html(key + ": " + val);

            listGroupPanel.append(ctrlElem);
        });
    }


    containerColumn.append(mainMenuDiv.append(listGroupPanel));
    containerRow.append(containerColumn);
    containerFuild.append(containerRow);


    return $('<div/>').append(containerFuild).html();
}

function get_data_item_collapse(link, itemData, itemCount) {
    // create badge
    var badgeSpan = $('<span/>', {
        class: "badge",
        style: "background: #fff;  border-radius: 5px; margin-left: 2px; margin-bottom: 1px;",
        html: itemCount
    });

    //create button
    var itemsLanguage = "items";
    if (itemCount == 1) {
        itemsLanguage = "item";
    }
    var collapseBtn = $('<a></a>')
        .attr({
            "class": "btn btn-xs btn-info",
            "data-toggle": "collapse",
            "data-target": "#" + link,
            "style": "margin-left:1px; margin-bottom:0px; border-radius:0; background-image:none; border-color:transparent; ",
            "type": "button",
        })
        .html($('<div/>').append(badgeSpan).html() + '<span style="margin-left: 2px; margin-bottom:0px;"> ' + itemsLanguage + '</span>');

    var collapseDiv = $('<div>', {
        id: link,
        class: "collapse",
        html: itemData
    });

    var ctrlDiv = $('<div/>')
        .append(collapseBtn)
        .append(collapseDiv);


    return ctrlDiv.html();
}

function format_camel_case(xter) {
    var a = xter
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, function (str) {
            return str.toUpperCase();
        });


    var refinedXter = a.trim().split(/\s+/g);

    for (var i = 1; i < refinedXter.length; ++i) {
        var str = refinedXter[i];
        str = str.toLowerCase().replace(/\b[a-z]/g, function (letter) {
            return letter.toLowerCase();
        });

        refinedXter[i] = str;
    }

    return refinedXter.join(' ');

}

function build_description_display(data) {
    //this is a specialised counterpart to the function 'build_attributes_display()',
    // but handles datafile description metadata

    var resolvedTable = $('<table/>');

    for (var j = 0; j < data.description.columns.length; ++j) {
        var Ddata = data.description.columns[j];

        var iRow = $('<tr/>', {
            "class": "copo-webui-tabular"
        });

        var labelCol = $('<td/>').attr('colspan', 2).append(Ddata.title);
        iRow.append(labelCol);

        var dataCol = $('<td/>').attr('colspan', 2).append(data.description.data_set[Ddata.data]);
        iRow.append(dataCol);

        resolvedTable.append(iRow);
    }

    return resolvedTable;
}

function build_attributes_display(data) {
    var contentHtml = $('<table/>', {
        // cellpadding: "5",
        cellspacing: "0",
        border: "0",
        // style: "padding-left:50px;"
    });

    if (data.component_attributes.columns) {
        // expand row

        for (var i = 0; i < data.component_attributes.columns.length; ++i) {
            var colVal = data.component_attributes.columns[i];

            var colTR = $('<tr/>');
            contentHtml.append(colTR);

            colTR
                .append($('<td/>').append(colVal.title))
                .append($('<td/>').append(data.component_attributes.data_set[colVal.data]));

        }
    }

    return contentHtml;
}

function get_collapsible_panel(panelType) {
    if (!panelType) {
        panelType = 'default'
    }

    var panelGroup = $('<div/>', {
        class: "panel-group",
    });

    var panelClass = "panel panel-" + panelType;
    var panel = $('<div/>', {
        class: panelClass,
    });

    var panelHeading = $('<div/>', {
        class: "panel-heading",
    });

    var panelTitle = $('<div/>', {
        class: "panel-title"
    });

    var panelTitleAnchor = $('<a/>', {
        "data-toggle": "collapse"
    });

    panelTitle.append(panelTitleAnchor);
    panelHeading.append(panelTitle);

    panel.append(panelHeading);

    var panelCollapse = $('<div/>', {
        class: "panel-collapse collapse",
    });


    var panelBody = $('<div/>', {
        class: "panel-body"
    });

    panelCollapse.append(panelBody);

    panel.append(panelCollapse);

    panelGroup.append(panel);

    return $('<div/>').append(panelGroup).clone();
}

function get_panel(panelType) {
    if (!panelType) {
        panelType = 'default'
    }

    var panelClass = "panel panel-" + panelType;
    var panel = $('<div/>', {
        class: panelClass,
    });

    var panelHeading = $('<div/>', {
        class: "panel-heading",
        style: "background-image: none;"
    });

    panel.append(panelHeading);


    var panelBody = $('<div/>', {
        class: "panel-body"
    });

    panel.append(panelBody);

    var panelFooter = $('<div/>', {
        class: "panel-footer",
        style: "background-color: #fff;"
    });

    panel.append(panelFooter);

    return $('<div/>').append(panel).clone();
}

// Set COPO frontpage properties in this dictionary
function get_component_meta(component) {
    var componentMeta = null;
    var components = get_profile_components();

    components.forEach(function (comp) {
        if (comp.component == component) {
            componentMeta = comp;
            return false;
        }
    });

    return componentMeta
}

function get_profile_components() {
    var componentProperties = [
        {
            component: 'profile',
            title: 'Work Profiles',
            buttons: ["quick-tour-template", "new-component-template"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
            tableID: 'copo_profiles_table',
            secondaryTableID: 'copo_shared_profiles_table',
            visibleColumns: 3,
            recordActions: ["add_record_all", "edit_record_single"] //specifies action buttons for records manipulation
        },
        {
            component: 'sample',
            title: 'Samples',
            iconClass: "fa fa-filter",
            semanticIcon: "filter", //semantic UI equivalence of fontawesome icon
            countsKey: "num_sample",
            buttons: ["quick-tour-template", "new-samples-template", "new-samples-spreadsheet-template", "barcoding_manifest", "accept_reject_samples"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
            colorClass: "samples_color",
            color: "olive",
            profile_component: true,
            tableID: 'sample_table',
            recordActions: ["show_sample_source", "describe_record_all", "edit_record_single"],
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
        },/*
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
    ];

    return componentProperties
}


//builds component-page navbar
function do_page_controls(componentName) {
    var component = null;
    var components = get_profile_components();

    components.forEach(function (comp) {
        if (comp.component == componentName) {
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
    var pageHeaders = $(".copo-page-headers"); //page header/icons
    var pageIcons = $(".copo-page-icons"); //profile component icons
    var sideBar = $(".copo-sidebar"); //sidebar panels

    //add profile title
    if ($("#profile_title").length) {
        var profileTitle = $('<div/>', {
            class: "page-title-custom",
            style: "margin-right:10px;",
            html: "<span title='Profile title' style='color: #8c8c8c; font-size: 18px;'>Profile: " + $("#profile_title").val() + "</span>"
        });

        pageHeaders.append(profileTitle);
    }

    //add page title
    var PageTitle = $('<span/>', {
        class: "page-title-custom",
        style: "margin-right:10px;",
        html: component.title
    });

    pageHeaders.append(PageTitle);


    //create panels
    if (component.sidebarPanels) {
        var sidebarPanels = $(".copo-sidebar-templates").clone();
        var sidebarPanels2 = sidebarPanels.clone();
        sidebarPanels.find(".nav-tabs").html('');
        sidebarPanels.find(".tab-content").html('');
        $(".copo-sidebar-templates").remove();


        component.sidebarPanels.forEach(function (item) {
            sidebarPanels.find(".nav-tabs").append(sidebarPanels2.find(".nav-tabs").find("." + item));
            sidebarPanels.find(".tab-content").append(sidebarPanels2.find(".tab-content").find("." + item));
        });

        sideBar
            .append(sidebarPanels.find(".nav-tabs"))
            .append(sidebarPanels.find(".tab-content"));


    }

    //create buttons
    var buttonsSpan = $('<span/>', {style: "white-space:nowrap;"});
    pageHeaders.append(buttonsSpan);
    component.buttons.forEach(function (item) {
        if (component.buttons) {
            component.buttons.forEach(function (item) {
                buttonsSpan.append($("." + item)).append("<span style='display: inline;'>&nbsp;</span>");
            });
        }
    });

    //...and profile component buttons
    if (component.hasOwnProperty("profile_component") && component.profile_component.toString() == "true") {
        var pcomponentHTML = $(".pcomponents-icons-templates").clone().removeClass("pcomponents-icons-templates");
        var pcomponentAnchor = pcomponentHTML.find(".pcomponents-anchor").clone().removeClass("pcomponents-anchor");
        pcomponentHTML.find(".pcomponents-anchor").remove();

        pageIcons.append(pcomponentHTML);

        var components = get_profile_components();

        for (var i = 1; i < components.length; ++i) {
            var comp = components[i];
            if (comp.hasOwnProperty("profile_component") && comp.profile_component.toString() == "true") {

                if ((comp.component == component.component)) {
                    continue;
                }

                var newAnchor = pcomponentAnchor.clone();
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
    refresh_tool_tips();
}

function refresh_webpop(elem, title, content, exrta_meta) {
    var config = {
        title: title,
        content: '<div class="webpop-content-div">' + content + '</div>',
        closeable: true,
        cache: false,
        width: 300,
        trigger: 'hover',
        arrow: false,
        animation: 'fade',
        placement: 'right',
        dismissible: false,
        onHide: function ($element) {
            WebuiPopovers.updateContent(elem, '<div class="webpop-content-div">' + content + '</div>');
            elem.removeClass("copo-form-control-focus");
        },
        onShow: function ($element) {
            elem.addClass("copo-form-control-focus");
        }
    };

    //refresh config with extra configurations
    $.each(exrta_meta, function (key, val) {
        config[key] = val;
    });

    elem.webuiPopover(config);
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
    var loaderObject = $('<div>', {
        style: 'text-align: center',
        html: "<span class='fa fa-spinner fa-pulse fa-3x'></span>"
    });

    return loaderObject.clone();
}

function sanitise_help_list(contextHelpList) {
    var dataSet = [];

    if (contextHelpList.properties) {
        var dtd = contextHelpList.properties;

        for (var i = 0; i < dtd.length; ++i) {
            var option = {};
            option["id"] = i + 1;
            option["title"] = dtd[i].title;
            option["content"] = dtd[i].content;
            option["context"] = dtd[i].context;
            var helpID = Math.random() + Math.random() + Math.random();
            helpID = helpID.toString();
            option["help_id"] = "context_help_" + i + "_" + helpID.replace(".", "_");
            dataSet.push(option);
        }
    }

    return dataSet;
}

function do_context_help(data) {
    //does current page request context help?
    var tableID = 'page-context-help';
    var helpComponent = $("#" + tableID);

    //if true then page requests context help control to be added
    if (!helpComponent.length) {
        return false;
    }


    var dtd = sanitise_help_list(data);

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

function get_timestamp() {
    var date = new Date();

    var monthNames = [
        "Jan", "Feb", "Mar",
        "Apr", "May", "Jun", "Jul",
        "Aug", "Sep", "Oct",
        "Nov", "Dec"
    ];

    var day = date.getDate();
    var monthIndex = date.getMonth();
    var year = date.getFullYear();
    var hour = date.getHours();
    var minute = date.getMinutes();
    var second = date.getSeconds();

    return day + '_' + monthNames[monthIndex] + '_' + year + "_" + hour + "_" + minute + "_" + second;
}

function do_context_help_event() {
    //handles collapsing of help topics

    $(document).on('click', '.side-help-trigger', function (e) {
        var dataTargetID = $(this).attr('data-target');

        if ($(this).parent().hasClass("shown")) {
            $(this).parent().removeClass("shown");
            $("#" + dataTargetID).collapse("hide");
        } else {
            $(this).parent().addClass("shown");
            $("#" + dataTargetID).collapse("show");
        }
    });
}

function set_inputs_help() {
    $(document).on("focus", ".copo-form-group", function (event) {
        var elem = $(this);

        if (elem.attr("data-helptip") == "no") { //help turned off
            return false;
        }

        if (!(elem.find(".form-input-help").length)) {
            return false;
        }

        var title = elem.find("label").html();
        if (elem.find("label").find(".constraint-label").length) {
            title = elem.find("label").clone();
            title.find(".constraint-label").remove();
            title = title.html();
        }

        var content = elem.find(".form-input-help").html();

        if (elem.closest(".rendered-control").length) {
            elem.closest(".rendered-control").find(".message-segment")
                .html('')
                .append($('<div style="margin-top: 15px;" class="webpop-content-div message-segment-help ui ignored info message">' + content + '</div>'));
        } else {
            elem.webuiPopover('destroy');

            elem.webuiPopover({
                title: title,
                content: '<div class="webpop-content-div">' + content + '</div>',
                trigger: 'sticky',
                width: 300,
                arrow: true,
                closeable: true,
                animation: 'fade',
                placement: 'right',
            });
        }
    });

    $(document).on("blur", ".copo-form-group", function (event) {
        if ($(this).closest(".rendered-control").length) {
            $(this).closest(".rendered-control").find(".message-segment-help").remove();
        } else {
            $(this).webuiPopover('destroy');
        }
    });
}


function dialog_display(dialog, dTitle, dMessage, dType) {
    var dTypeObject = {
        "warning": '<div class="circular ui large basic red icon button"><i class="large icon remove"></i></div>',
        "danger": '<div class=" ui  basic red icon button"><i class=" icon remove"></i></div>',
        "info": "fa fa-exclamation-circle copo-icon-info"
    };

    var dTypeClass = "fa fa-exclamation-circle copo-icon-default";

    if (dTypeObject.hasOwnProperty(dType)) {
        dTypeClass = dTypeObject[dType];
    }

    var iconElement = $(dTypeClass);


    var messageDiv = $('<div/>', {
        html: dMessage
    });


    var $dialogContent = $('<div></div>');
    $dialogContent.append($('<div/>').append(iconElement));
    $dialogContent.append('<div class="copo-custom-modal-message">' + messageDiv.html() + '</div>');
    dialog.realize();
    dialog.setClosable(false);
    dialog.setSize(BootstrapDialog.SIZE_SMALL);
    dialog.getModalHeader().hide();
    dialog.setTitle(dTitle);
    dialog.setMessage($dialogContent);
    dialog.getModalBody().prepend('<div class="copo-custom-modal-title">' + dialog.getTitle() + '</div>');
    dialog.getModalBody().addClass('copo-custom-modal-body');
    //dialog.getModalContent().css('border', '4px solid rgba(255, 255, 255, 0.3)');
    dialog.open();
}

function update_quick_tour_flag() {
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
        var dismissTour = '<a class="dismisstouralert pull-right" href="#" role="button" ' +
            'style="text-decoration: none; color:  #c93c00;" aria-haspopup="true" aria-expanded="false">' +
            '<i class="fa fa-times-circle " aria-hidden="true">' +
            '</i>&nbsp; Dismiss Tour</a>';

        var takeTour = '<a class="takeatouryes" href="#" role="button" ' +
            'style="text-decoration: none;" aria-haspopup="true" aria-expanded="false">' +
            '<i class="fa fa-lightbulb-o " style="color: #35637e;" aria-hidden="true">' +
            '</i>&nbsp; Take Tour</a>';


        var messageContent = 'Do you want to take a quick tour of the page? <br/><br/><span style="color: #35637e;">Please note that your screen will be dimmed, and regular page elements inaccessible in the quick tour mode.</span>' + '<hr/>' + takeTour + dismissTour;

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

    var item = quickTourArray[0];
    var itemMessage = quickTourMessages[item.attr("data-copo-tour-id")];

    var endTour = '<a class="endcopotour pull-right" href="#" role="button" ' +
        'style="text-decoration: none; color:  #c93c00;" aria-haspopup="true" aria-expanded="false">' +
        '<i class="fa fa-times-circle " aria-hidden="true">' +
        '</i>&nbsp; End Tour</a>';

    var nextTip = endTour;


    if (quickTourArray.length > 1) {
        nextTip = '<a class="quicktournext" href="#" role="button" ' +
            'style="text-decoration: none;" aria-haspopup="true" aria-expanded="false">' +
            '<i class="fa fa-lightbulb-o " style="color: #35637e;" aria-hidden="true">' +
            '</i>&nbsp; Next Tip</a>';

        nextTip += endTour;
    }

    var messageContent = itemMessage.content + '<hr/>' + nextTip;

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

    for (var i = 0; i < quickTourArray.length; i++) {
        if (quickTourArray[i].attr("data-copo-tour-id") === item.attr("data-copo-tour-id")) {
            quickTourArray.splice(i, 1);
            break;
        }
    }
} //end of func

function quick_tour_messages() {
    var qt = {
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
    }

    return qt.properties;
}


function get_menu_control() {
    let menu_control = $('<div class="copo-actions-dropdown ui dropdown">' +
        '<div class="ui active buttons">' +
        '<div class="ui big blue button menu-action-label"></div>' +
        '<div class="ui big basic blue floating dropdown icon button">' +
        '<i class="dropdown icon"></i>' +
        '</div>' +
        '</div>' +
        '<div class="text" style="color: #35637e; padding-left: 5px;"></div>' +
        '<i data-html="Please note that some items in the menu may be unavailable depending on the status"' +
        'class="info circle grey icon copo-tooltip"></i>' +
        '<div class="menu component-menu">' +
        '</div>' +
        '</div>');

    return menu_control.clone();
}

function get_description_bundle_panel() {
    let panel = $('<div class="description-bundle-template">\n' +
        '        <div class="panel panel-dtables3">\n' +
        '            <div class="panel-heading" style="background-image: none; border: none;">\n' +
        '                <div class="bundle-header bundlename" style="font-weight: bold; font-size: 15px;"></div>\n' +
        '                <div class="attr-placeholder" style="font-weight: normal; font-size: 12px; color: #ecf2f9;"> <span class="attr-placeholder-key"> </span> <span class="attr-placeholder-value"></span></div>\n' +
        '                <div style="font-weight: normal; font-size: 12px; color: #ecf2f9;">Last modified: <span class="bundle-modified-date"></span></div>\n' +
        '            </div>\n' +
        '            <div class="panel-body">\n' +
        '                <div class="row" style="margin-bottom: 20px;">\n' +
        '                    <div class="col-sm-10 col-md-10 col-lg-10">\n' +
        '                        <div class="copo-actions-dropdown ui dropdown">\n' +
        '                            <div class="ui active buttons">\n' +
        '                                <div class="ui blue button bundle-action-label">Tasks Menu</div>\n' +
        '                                <div class="ui basic blue floating dropdown icon button">\n' +
        '                                    <i class="dropdown icon"></i>\n' +
        '                                </div>\n' +
        '                            </div>\n' +
        '                            <div class="text" style="color: #35637e;"></div>\n' +
        '                            <i data-html="Please note that some items in the menu may be unavailable depending on the status."\n' +
        '                               class="info circle grey icon copo-tooltip"></i>\n' +
        '                            <div class="menu component-menu">\n' +
        '                                <div data-task="add_datafiles" class="item bundlemenu">Add datafiles</div>\n' +
        '                                <div data-task="view_datafiles" class="item bundlemenu">Show datafiles</div>\n' +
        '                                <div class="divider"></div>\n' +
        '                                <div data-task="add_metadata" class="item bundlemenu">Add/Edit metadata</div>\n' +
        '                                <div data-task="view_metadata" class="item bundlemenu">Show metadata</div>\n' +
        '                                <div class="divider"></div>\n' +
        '                                <div data-task="edit_bundle" class="item bundlemenu">Rename bundle</div>\n' +
        '                                <div data-task="clone_bundle" class="item bundlemenu">Clone bundle</div>\n' +
        '                                <div data-task="delete_bundle" class="item bundlemenu">Delete bundle</div>\n' +
        '                                <div class="divider"></div>\n' +
        // '                                <div data-task="submit_bundle" class="item bundlemenu">Submit bundle</div>\n' +
        '                                <div data-task="view_accessions" class="item bundlemenu">View accessions</div>\n' +
        '                                <div data-task="view_issues" class="item bundlemenu">View issues</div>\n' +
        '                            </div>\n' +
        '                        </div>\n' +
        '                    </div>\n' +
        '                    <div class="col-sm-2 col-md-2 col-lg-2">\n' +
        '                        <div class="pull-right">\n' +
        '                            <i title="" class="big icon copo-tooltip bundle-status"></i>\n' +
        '                        </div>\n' +
        '                    </div>\n' +
        '                </div>\n' +
        '                <div class="row">\n' +
        '                    <div class="col-sm-12 col-md-12 col-lg-12">\n' +
        '                        <div class="pbody"></div>\n' +
        '                    </div>\n' +
        '                </div>\n' +
        '            </div>\n' +
        '        </div>\n' +
        '    </div>');

    return panel.clone();
}


function get_card_panel() {
    let panel = $('<div class="component-type-panel">\n' +
        '        <div class="panel panel-dtables3">\n' +
        '            <div class="panel-heading" style="background-image: none; border: none;">\n' +
        '                <div class="panel-header-1" style="font-weight: bold; font-size: 15px;"></div>\n' +
        '                <div class="attr-placeholder" style="font-weight: normal; font-size: 12px; color: #ecf2f9; display: none;"><span class="attr-key copo-right-spacer"></span> <span class="attr-value"></span></div>\n' +
        '            </div>\n' +
        '            <div class="panel-body">\n' +
        '                <div class="row" style="margin-bottom: 20px;">\n' +
        '                    <div class="col-sm-10 col-md-10 col-lg-10">\n' +
        '                        <div class="copo-actions-dropdown ui dropdown">\n' +
        '                            <div class="ui active buttons">\n' +
        '                                <div class="ui blue button menu-label">Tasks Menu</div>\n' +
        '                                <div class="ui basic blue floating dropdown icon button menu-label-icon">\n' +
        '                                    <i class="dropdown icon"></i>\n' +
        '                                </div>\n' +
        '                            </div>\n' +
        '                            <div class="text" style="color: #35637e;"></div>\n' +
        '                            <i data-html="Please note that some items in the menu may be unavailable depending on the status."\n' +
        '                               class="info circle grey icon copo-tooltip"></i>\n' +
        '                            <div class="menu component-menu"> </div>\n' +
        '                        </div>\n' +
        '                    </div>\n' +
        '                    <div class="col-sm-2 col-md-2 col-lg-2">\n' +
        '                        <div class="pull-right">\n' +
        '                            <i title="" class="big icon copo-tooltip bundle-status"></i>\n' +
        '                        </div>\n' +
        '                    </div>\n' +
        '                </div>\n' +
        '                <div class="row">\n' +
        '                    <div class="col-sm-12 col-md-12 col-lg-12">\n' +
        '                        <div class="pbody"></div>\n' +
        '                    </div>\n' +
        '                </div>\n' +
        '            </div>\n' +
        '        </div>\n' +
        '    </div>');

    return panel.clone();
}

function get_alert_control() {
    let alert = $('<div class="alert alert-success alert-dismissable fade in copo-alert-message" style="background-image: none; border: none;">\n' +
        '            <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>\n' +
        '            <span class="webpop-content-div alert-message"></span>\n' +
        '        </div>');

    return alert.clone();
}

function get_alert_control_no_close() {
    let alert = $('<div class="alert alert-success alert-dismissable fade in copo-alert-message" style="background-image: none; border: none;">\n' +
        '            <span class="webpop-content-div alert-message"></span>\n' +
        '        </div>');

    return alert.clone();
}

function get_ajax_loader() {
    let loader = $('<span class="input-group">\n' +
        '                    <img style="height: 24px; margin-left:5px;" src="/static/copo/img/loading.gif"></span>');

    return loader.clone();
}

function get_collapsible_panel() {
    let panel = $('<div class="panel-group" style="margin-top: 15px;">\n' +
        '        <div class="panel panel-dtables">\n' +
        '            <div class="panel-heading" style="background-image: none; border: none;">\n' +
        '                <h4 class="panel-title">\n' +
        '                    <div class="row">\n' +
        '                        <div class="col-sm-8 col-md-8 col-lg-8 copo-details-header"></div>\n' +
        '                        <div class="col-sm-2 col-md-2 col-lg-2 pull-right">\n' +
        '                            <div class="pull-right">\n' +
        '                                <i data-toggle="collapse" href="" class="fa fa-plus text-primary copo-details-icon"\n' +
        '                                   style="cursor: pointer; display: block;"\n' +
        '                                   aria-hidden="true"></i>\n' +
        '                            </div>\n' +
        '                        </div>\n' +
        '                    </div>\n' +
        '                </h4>\n' +
        '            </div>\n' +
        '            <div id="" class="panel-collapse collapse copo-details-coll">\n' +
        '                <div class="panel-body pbody"></div>\n' +
        '            </div>\n' +
        '        </div>\n' +
        '    </div>');

    return panel.clone();
}