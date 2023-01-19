/** Created by AProvidence on 16012023
 * Functions defined are called from 'copo_tol_inspect' web page
 */

const fadeSpeed = 'fast';
const dt_options = {
    "scrollY": 400,
    "scrollX": true,
    "bSortClasses": false,
    "lengthMenu": [10, 25, 50, 75, 100, 500, 1000, 2000],
    select: {
        style: 'os',
        selector: 'td:first-child'
    },
};

$(document).ready(function () {
    const copoGALInspectionURL = "/copo/tol_inspect/gal";
    const project = $("#sample_filter").find(".active").find("a").attr("href");

    // add field names here which you don't want to appear in the supervisors table
    excluded_fields = ["profile_id", "biosample_id"]
    // add field names here which you want to appear in the 'tol_inspect' samples' table
    included_fields = ["SPECIMEN_ID", "SCIENTIFIC_NAME", "public_name"]


    // Get active manifest type tab on tab change
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        let project = $(e.target).attr("href")
        update_pending_samples_table_for_tol_inspection(project)
    });

    $(document).data("areAllSampleModalFieldsShown", false)
    $(document).data("showAllTableFieldsCheckbox", false);
    $(document).data("isSampleModalSearchQueryChecked", true);
    $(document).data("navBarItems", [])
    $(document).data("navBarItemsTableBodyView", {})
    $(document).data("searchQuery", {})

    $(document).on("click", ".tol_inspect_gal", function () {
        document.location = copoGALInspectionURL;
    })

    $(document).on("click", ".sample_table_row", function (el) {
        let sample_id = el.currentTarget.id
        const errorMsg = "Couldn't build Sample Details' form!";
        csrftoken = $.cookie('csrftoken');

        $(el.currentTarget).parent().siblings().addBack().each(function (idx, el) {
            $(el).toggleClass("selected_row")
        })

        $.ajax({
            url: "/copo/get_sample_details/",
            method: "POST",
            headers: {'X-CSRFToken': csrftoken},
            dataType: "json",
            data: {
                'sample_id': sample_id,
            },
            success: function (data) {
                json2HtmlForm_SampleDetails(data)
            },
            error: function () {
                alert(errorMsg);
            }
        });
    })

    $(document).on("click", ".fieldID", function (e) {
        let preNavItem = $("#tolInspectNavBar li.active")
        let breadcrumb = $(".breadcrumb")
        let navBarItems = $(document).data("navBarItems")

        //  Ensure that duplicate fields are not included in the top navigation menu
        if (!navBarItems.includes(this.innerHTML)) {
            // Clone "tol_inspect" web page table body so that it can be referenced when the
            // different nav items are clicked
            let isSampleModalSearchQueryChecked = $(document).data("isSampleModalSearchQueryChecked");
            let navItem = preNavItem.text()
            let navItemView = $("#sample_panel").clone()
            let navItemViewDict = $(document).data("navBarItemsTableBodyView")
            let searchQueryDict = $(document).data("searchQuery")
            let field_value = $(this).next('.field_valueDiv').find('#field_valueID').val()

            if (isSampleModalSearchQueryChecked) {
                // Get samples by field, field value and project
                navItemViewDict[navItem] = navItemView;
                console.log('Nav menu items: ', navItemViewDict)


            } else {
                // Get samples by field and field value
                searchQueryDict["field"] = this.innerHTML;
                searchQueryDict["field_value"] = field_value;

                row_select_on_tol_inspect_web_page(this)
            }

            preNavItem.removeClass("active")
            // new/current nav item
            const listItem = $("<li/>", {});
            listItem.addClass("active")
            listItem.text(this.innerHTML)
            breadcrumb.append(listItem)

            $("#tolInspectNavBar li.active").prev('li').html('<a href="">' + preNavItem.text() + '</a>')
            navBarItems.push(this.innerHTML)


            $('.modal').modal('hide'); // Close the Bootstrap dialog
        } else {
            BootstrapDialog.alert('Please choose another field. The field, ' + '<b>' + this.innerHTML + '</b>' + ',  is already included in the navigation menu!')

            // Displays the Bootstrap dialog over the sample details modal
            $('.modal bootstrap-dialog').css({"z-index": "9999"})
        }
    })

    $(document).on("click", "tr.sample_table_row", function (e) {
        let cb;
        cb = $($(e.target).siblings(".tickbox").find("input"));
        cb.click()

    })

    $(document).on("click", ".selectable_row, .hot_tab", row_select_on_tol_inspect_web_page)

    update_pending_samples_table_for_tol_inspection(project)
});


function build_form_body_sample_Details(data, form) {
    //data = $(document).data("sample_data")
    //console.log("Data: ", data)
    const formDiv = document.getElementsByClassName("formDiv");

    // Iterate through dictionary
    Object.entries(data).forEach(([field, value]) => {
        // Create field div
        const fieldDiv = document.createElement('div');
        fieldDiv.setAttribute('class', 'form-group fieldDiv');
        fieldDiv.setAttribute('id', `${field}_div`);

        // Field; Create field label
        const fieldLabel = document.createElement('label');
        fieldLabel.innerHTML = field;
        fieldLabel.setAttribute('class', 'fieldID control-label col-sm-6');
        fieldLabel.style.paddingRight = '20px'; // Add space between the value field and field name
        fieldLabel.style.marginLeft = '15px';
        fieldLabel.style.textAlign = "left"

        // Truncate long field names
        fieldLabel.style.whiteSpace = 'nowrap';
        fieldLabel.style.textOverflow = 'ellipsis';
        fieldLabel.style.overflow = 'hidden';
        fieldLabel.style.maxWidth = '220px';
        fieldLabel.setAttribute('title', 'Query similar samples by the field, ' + field)
        fieldDiv.appendChild(fieldLabel);

        // Field value div
        const fieldValueDiv = document.createElement('div');
        fieldValueDiv.setAttribute('class', 'col-sm-6 field_valueDiv');
        // Hide field and field value if field value is null or empty
        if (value.toString() === "") {
            fieldDiv.classList.add('divhidden')
            fieldDiv.setAttribute('hidden', 'hidden')
        }
        fieldDiv.appendChild(fieldValueDiv);

        // Field value
        const field_value = document.createElement('input');
        field_value.setAttribute('id', "field_valueID");
        field_value.setAttribute('readonly', "");
        field_value.setAttribute('type', 'text');
        field_value.setAttribute('class', 'form-control');
        field_value.setAttribute('value', value.toString());

        fieldValueDiv.appendChild(field_value);
        form.appendChild(fieldDiv)
        $(formDiv).append(form)


    })


}

function get_form_message(data) {
    var messageRowDiv = $('<div/>',
        {
            class: "row"
        });

    var messageColDiv = $('<div/>',
        {
            class: "col-sm-12 col-md-12 col-lg-12 formMessageDiv"
        });

    messageRowDiv.append(messageColDiv);

    var message_text = null;
    var message_type = null;


    try {
        message_text = data.form.form_message.text;
        message_type = data.form.form_message.type;

    } catch (err) {
    }

    if (message_text && message_type) {
        let feedback = get_alert_control();
        let alertClass = "alert-" + message_type;

        feedback
            .removeClass("alert-success")
            .addClass(alertClass);

        feedback.find(".alert-message").html(message_text);
        messageColDiv.html(feedback);
    }

    return messageRowDiv;
}

function get_profile_samples_table_first_element_block_of_code(el, td, row, th_row, td_row) {
    // Change "public_name" table header name to "tolid" table header name
    // because tolid" is recognised/known by users
    el === "public_name" ? el = "tolid" : el
    // make header
    const th = $("<th/>", {
        html: el
    });
    $(th).css({"text-align": "center"})
    $(th).css({"width": "360px"})
    $(th_row).append(
        th
    )
    // and row
    td = $("<td/>", {
        html: row[el]
    })
    $(td).css({"text-align": "center"})
    $(td).css({"width": "360px"})
    if (row[el] === 'NA') {
        $(td).addClass("na_color")
    } else if (row[el] === "") {
        $(td).addClass("empty_color")
    }
    $(td_row).append(
        td
    )
}

function get_profile_samples_table_not_first_element_block_of_code(el, row, td_row) {
    let td = document.createElement("td")
    td.innerHTML = row[el]
    if (row[el] === 'NA') {
        td.className = "na_color"
    } else if (row[el] === "") {
        td.className = "empty_color"
    }
    td_row.appendChild(td)
}

function set_up_form_show_all_fields_checkbox_div(data) {
    const project = $("#sample_filter").find(".active").find("a").attr("href");

    const rowDiv = $('<div/>',
        {
            class: "row helpDivRow",
            style: "margin-bottom:20px;"
        });

    const showAllFieldsCheckBoxLabel = $('<label/>',
        {
            class: "pull-right showFieldsLabel",
            style: "padding-right:60px;"
        });

    const querySamplesCheckBoxLabel = $('<label/>',
        {
            class: "pull-left showSamplesQueryLabel",
            style: "padding-left:25px;"
        });

    const showAllFieldsCheckBox = $('<input/>',
        {
            id: "sampleModalFieldsID",
            type: "checkbox",
            style: "margin-left:10px;",

        });

    const showQuerySamplesCheckBox = $('<input/>',
        {
            id: "sampleModalQueryTypeID",
            type: "checkbox",
            style: "margin-left:10px;",

        });

    showQuerySamplesCheckBox.attr('checked', 'checked')
    querySamplesCheckBoxLabel.text('Query within ' + project + ' project samples: ')
    querySamplesCheckBoxLabel.append(showQuerySamplesCheckBox)

    showAllFieldsCheckBoxLabel.text('Show all fields: ')
    showAllFieldsCheckBoxLabel.append(showAllFieldsCheckBox)
    return rowDiv.append(querySamplesCheckBoxLabel).append(showAllFieldsCheckBoxLabel);
}

function set_up_form_body_div_sample_details(data, form) {
    const formBodyDiv = $('<div/>',
        {
            class: "row formDivRow"
        }).append($('<div/>',
        {
            class: "formDiv col-sm-12 col-md-12 col-lg-12",
            css: {'overflow': 'scroll', 'height': '530px', 'margin-right': "20px"},
        }).append(form));

    //build main form
    build_form_body_sample_Details(data, form);

    return formBodyDiv;
}


function json2HtmlForm_SampleDetails(data) {
    const form = document.createElement('form');
    form.setAttribute('class', 'form-horizontal');

    // let data = $(document).data("areAllSampleModalFieldsShown") ? data_with_blanks : data_with_no_blanks
    // let data = $(document).data("sample_data")

    const dialog = new BootstrapDialog({
        description: "The following information relates to the selected sample.",
        message: "The following information relates to the selected sample.",
        type: BootstrapDialog.TYPE_PRIMARY,
        size: BootstrapDialog.SIZE_WIDE,
        title: function () {
            return $('<span>' + 'Sample Details for ' + data["SPECIMEN_ID"] + '</span>').css("text-align", "center");
        },
        closable: true,
        closeIcon: '&#215;',
        animate: true,
        draggable: true,
        onhide: function (dialogRef) {
            refresh_tool_tips();
        },
        onshown: function (dialogRef) {

            //prevent enter keypress from submitting form automatically
            $("form").keypress(function (e) {
                //Enter key
                if (e.which === 13) {
                    return false;
                }
            });

            const event = jQuery.Event("postformload"); //individual compnents can trap and handle this event as they so wish
            $('body').trigger(event);

            document.querySelector("#sampleModalFieldsID").onchange = (e) => {
                let fieldDiv1 = document.getElementsByClassName('divhidden');
                let fieldDiv = $('.fieldDiv.divhidden')
                let checked = e.target.checked;

                if (checked) {
                    fieldDiv.removeAttr("hidden")
                    $(fieldDiv1).css({"display": ""})
                } else {
                    fieldDiv.attr("hidden")
                    $(fieldDiv1).css({"display": "None"})

                }
            }

            document.querySelector("#sampleModalQueryTypeID").onchange = (e) => {
                let checked = e.target.checked;
                $(document).data("isSampleModalSearchQueryChecked", checked)
            }
        },
    });

    const $dialogContent = $('<div/>');
    const form_help_div = set_up_form_show_all_fields_checkbox_div(data);
    const form_message_div = get_form_message(data);
    const form_body_div = set_up_form_body_div_sample_details(data, form);

    $dialogContent.append(form_help_div).append(form_message_div).append(form_body_div);
    dialog.realize();
    dialog.setMessage($dialogContent);
    dialog.open();
} //end of json2HTMLForm


function row_select_on_tol_inspect_web_page(ev) {
    // Get samples for the profile clicked in the left-hand panel and
    // populate the table in the right-hand panel
    jQuery.support.cors = true;
    let isSampleModalSearchQueryChecked = $(document).data("isSampleModalSearchQueryChecked");
    let searchQueryDict = $(document).data("searchQuery")
    let row;

    if ($(ev.currentTarget).is("td") || $(ev.currentTarget).is("tr")) {
        // we have clicked a profile on the left hand list
        $(document).data("selected_row", $(ev.currentTarget))
        row = $(document).data("selected_row")
        $(".selected").removeClass("selected")
        $(row).addClass("selected")
    } else {
        row = $(document).data("selected_row")
    }
    const project = $("#sample_filter").find(".active").find("a").attr("href");

    const d = {"profile_id": $(row).find("td").data("profile_id"), "project": project};

    const get_samples_by_project_s = {
        url: "/copo/get_project_samples_for_tol_inspection",
        data: d,
        method: "GET",
        dataType: "json"
    }
// JSON.parse(JSON.stringify(searchQueryDict)).field
    const get_samples_by_field_and_value_s = {
        url: `sample/sample_field/${searchQueryDict.field}/${searchQueryDict.field_value}`,
        data: {},
        method: "GET",
        headers: {'Access-Control-Allow-Origin': '*'},
        dataType: 'jsonp',
    }
    let s = $.isEmptyObject(searchQueryDict) && isSampleModalSearchQueryChecked ? get_samples_by_project_s : get_samples_by_field_and_value_s

    $("#profile_id").val(d.profile_id)
    $("#spinner").show()

    console.log("Ajax 's': ", s)
    console.log("Is search query dictionary empty: ", $.isEmptyObject(searchQueryDict))
    console.log("Search query: ", searchQueryDict)
    console.log(`Field: ${searchQueryDict.field}, Value:${searchQueryDict.field}`)

    console.log("In row select on tol inspect web page..is sample modal search query checked: ", isSampleModalSearchQueryChecked)

    $.ajax(s).error(function (data) {
        console.error("ERROR: " + data)
    }).done(function (data) {
            let sample_panel = $("#sample_panel")
            if ($.fn.DataTable.isDataTable('#profile_samples')) {
                $("#profile_samples").DataTable().clear().destroy();

            }
            sample_panel.find("thead").empty()
            sample_panel.find("tbody").empty()

            if (data.length) {
                const header = $("<h4/>", {
                    html: "Samples"
                });
                sample_panel.find(".labelling").empty().append(header)

                // Create page top navigation
                const navMenu = $("<li/>", {
                    class: "active"
                });

                navMenu.text("SAMPLES")

                // Add 'SAMPLES' to the global navBarItems list
                $(document).data("navBarItems", [])
                $(document).data("navBarItems").push('SAMPLES')

                $("#tolInspectNavBar").find(".breadcrumb").empty().append(navMenu)

                const rows = [];

                // Get the value of the showAllTableFields checkbox
                let areAllTableFieldsShown = $(document).data("showAllTableFieldsCheckbox");

                $(data).each(function (idx, row) {
                    let td;
                    const th_row = document.createElement("tr");
                    const td_row = document.createElement("tr");
                    td_row.className = "sample_table_row"

                    if (idx === 0) {
                        // do header and row
                        const empty_th = document.createElement("th");
                        th_row.appendChild(empty_th)
                        td = document.createElement("td");
                        td.className = "tickbox"
                        td.style.textAlign = "center"
                        td.innerHTML = idx + 1 // Increment by 1 because default numbering system starts at 0
                        td_row.appendChild(td)

                        for (let el in row) {
                            if (el === "_id") {
                                td_row.setAttribute("id", row._id.$oid)
                                $(td_row).attr("sample_id", row._id.$oid)
                            } else if (!areAllTableFieldsShown && included_fields.includes(el)) {
                                get_profile_samples_table_first_element_block_of_code(el, td, row, th_row, td_row)
                            } else if (areAllTableFieldsShown && !excluded_fields.includes(el)) {
                                get_profile_samples_table_first_element_block_of_code(el, td, row, th_row, td_row)
                            }
                        }
                        document.getElementById("profile_samples").getElementsByTagName("thead")[0].appendChild(th_row)
                        document.getElementById("profile_samples").getElementsByTagName("tbody")[0].appendChild(td_row)

                    } else {
                        // if not first element
                        td = document.createElement("td")
                        td.className = "tickbox"
                        td.style.textAlign = "center"
                        td.innerHTML = idx + 1  // Increment by 1 because default numbering system starts at 0
                        td_row.appendChild(td)

                        for (let el in row) {
                            if (el === "_id") {
                                td_row.setAttribute("id", row._id.$oid)
                                td_row.setAttribute("sample_id", row._id.$oid)
                            } else if (!areAllTableFieldsShown && included_fields.includes(el)) {
                                get_profile_samples_table_not_first_element_block_of_code(el, row, td_row)
                            } else if (areAllTableFieldsShown && !excluded_fields.includes(el)) {
                                get_profile_samples_table_not_first_element_block_of_code(el, row, td_row)
                            }
                        }
                        $(td_row).css({"text-align": "center"})
                        $(td_row).css({"width": "360px"})
                        rows.push(td_row)
                    }

                })

                fastdom.mutate(() => {
                    //$("#profile_samples tbody").append(rows)
                    const tbody = document.getElementById("profile_samples").getElementsByTagName('tbody')[0];
                    rows.forEach(el => {
                        tbody.appendChild(el)
                    })
                    $("#profile_samples").DataTable(dt_options);

                    // Add checkbox to show all fields within the table beside the search box
                    // within the profile samples data table
                    $("#profile_samples_filter").prepend('<label style="padding-right: 40px"> Show all fields: <input id="showFieldsID" style="padding-right:20px" type="checkbox" onclick="row_select_on_tol_inspect_web_page(this)"></label>');

                    $("#showFieldsID").prop('checked', $(document).data("showAllTableFieldsCheckbox"));

                    document.querySelector("#showFieldsID").onchange = (e) => {
                        let checked = e.target.checked;
                        $(document).data("showAllTableFieldsCheckbox", checked);
                    }
                    $("#showFieldsID").prop('checked', $(document).data("showAllTableFieldsCheckbox"));
                })
            } else {
                let content
                if (data.hasOwnProperty("locked")) {
                    content = $("<h4/>", {
                        html: "View is locked by another User. Try again later."
                    })
                } else {
                    content = $("<h4/>", {
                        html: "No Samples Found"
                    })
                }
                $("#sample_panel").find(".labelling").empty().html(
                    content
                )
                $("#tolInspectNavBar").find(".breadcrumb").empty().html("")
                $(document).data("navBarItems", [])
            }
            $("#spinner").fadeOut("fast")
        }
    )
}

function update_pending_samples_table_for_tol_inspection(project) {
    // get profiles with samples needing looked at and populate left hand column
    $.ajax({
        url: "/copo/update_pending_samples_table_for_tol_inspection",
        method: "GET",
        dataType: "json",
        data: {
            "project": project
        }
    }).error(function (e) {
        console.error(e)
    }).done(function (data) {
        // Clear existing data in the profile titles' table
        if ($.fn.DataTable.isDataTable('#profile_titles')) {
            $("#profile_titles").DataTable().clear().destroy();
        }
        $(data['profiles']).each(function (d) {
            let date = new Date(data['profiles'][d].date_created.$date).toLocaleDateString('en-GB', {timeZone: 'UTC'})
            $("#profile_titles").find("tbody").append("<tr class='selectable_row'><td style='max-width: 10px' data-profile_id='" + data['profiles'][d]._id.$oid + "'>" + data['profiles'][d].title + "</td><td style='text-align: center'>" + date + "</td><td style='text-align: center'>" + data['profile_samples_count'] + "</td></tr>")

        })
        $($("#profile_titles tr")[1]).click()


        $.fn.dataTable.moment('DD/MM/YYYY');
        $("#profile_titles").DataTable({
            responsive: true,
            paging: false,
            dom: '<"top"f>rt<"bottom"lp><"clear">',
            "order": [[1, "desc"]],

        })

    })
}
