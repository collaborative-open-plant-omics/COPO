/** Created by AProvidence on 16012023
 * Functions defined are called from 'copo_tol_inspect' web page
 */
const profile_samples_dt_options = {
    "scrollY": 400,
    "scrollX": true,
    "bSortClasses": false,
    "bDestroy": true,
    "bPaginate": true,
    "bFilter": true,
    "bInfo": true,
    "lengthMenu": [10, 25, 50, 75, 100, 500, 1000, 2000],
    "bLengthChange": true,
    select: {
        style: 'os',
        selector: 'td:first-child'
    },
};

$(document).ready(function () {
    const copoGALInspectionURL = "/copo/tol_inspect/gal";
    const copoTolDashboardURL = "/copo/dashboard/";

    $(document).data("areAllSampleModalFieldsShown", false)
    $(document).data("showAllTableFieldsCheckBox", false);
    $(document).data("queryUserProfileRecordsCheckBox", true);
    $(document).data("searchByFaceting", false);
    $(document).data("selectedProfileID", "");
    $(document).data("navBarItems", [])
    $(document).data("searchQueryInUserProfile", {})
    $(document).data("searchQuery", {})

    $(document).on("click", ".tol_inspect_gal", function () {
        document.location = copoGALInspectionURL;
    })

    $(document).on("click", ".copo_dashboard", function () {
        document.location = copoTolDashboardURL
    })

    $(document).on("click", ".sample_table_row", function (el) {
        let sample_id = el.currentTarget.id
        const errorMsg = "Couldn't build Sample Details' form!";
        csrftoken = $.cookie('csrftoken');

        // Highlight clicked row
        $(this).addClass('selected_row').siblings().removeClass('selected_row');

        highlight_empty_cells_in_selected_row()

        $.ajax({
            url: "/copo/get_sample_details/",
            method: "POST",
            headers: {'X-CSRFToken': csrftoken},
            dataType: "json",
            data: {
                'sample_id': sample_id,
            },
            success: function (data) {
                if (!window.location.href.includes('dashboard')) json2HtmlForm_SampleDetails(data)
            },
            error: function () {
                alert(errorMsg);
            }
        });
    })

    $(document).on("click", ".fieldID", function () {
        let preNavItem = $("#tolInspectNavBar li.active")
        let breadcrumb = $(".breadcrumb")
        let navBarItems = $(document).data("navBarItems")
        let searchQueryDict = $(document).data("searchQuery")

        //  Ensure that duplicate fields are not included in the top navigation menu
        if (!navBarItems.includes(this.innerHTML)) {
            searchQueryDict[this.innerHTML] = $(this).next('.field_valueDiv').find('#field_valueID').val()

            // Remove 'tol_project' field/key from searchQueryDict so
            // that the aggregation is not inlude querying by project
            // if (Object.keys(searchQueryDict).includes("tol_project")) {
            //     delete searchQueryDict["tol_project"]
            // }

            preNavItem.removeClass("active")
            // new/current nav item
            const listItem = $("<li/>", {});
            listItem.addClass("active")
            listItem.text(this.innerHTML)
            listItem.attr("title", `Query for: ${$(this).next('.field_valueDiv').find('#field_valueID').val()}`)
            breadcrumb.append(listItem)

            $("#tolInspectNavBar li.active").prev('li').html('<a href="#">' + preNavItem.text() + '</a>')
            navBarItems.push(this.innerHTML)

            $(document).data("searchByFaceting", true);

            get_profile_titles(searchQueryDict)

            $('.modal').modal('hide'); // Close the Bootstrap dialog
        } else {
            BootstrapDialog.alert('Please choose another field. The field, ' + '<b>' + this.innerHTML + '</b>' + ',  is already included in the navigation menu!')

            // Displays the Bootstrap dialog over the sample details modal
            $('.modal .bootstrap-dialog').css({"z-index": "9999"})
        }
    })

    $(document).on("click", ".profile_title_selectable_row, .hot_tab", populate_samples_table_based_on_profile_title)

    $(document).on("click", ".breadcrumb li a", function (e) {
        let clicked_nav_menu_item = $(this).text()
        let searchQueryDict = $(document).data("searchQuery")
        let current_profileID = $('td').data("profile_id")
        let breadcrumb_liTag = $('.breadcrumb li')
        let profile_titlesID = $("#profile_titles")

        const project = $("#profile_types_filter").find(".active").find("a").attr("href");
        const profile_titles_row = $("#profile_titles tr")

        $(document).data("selectedProfileID", current_profileID);
        $(document).data("clicked_nav_menu_item", clicked_nav_menu_item);


        //Remove active navbar menu item
        $('#tolInspectNavBar li.active').removeClass('active').remove()

        // Set clicked navbar menu item as active
        $(this).closest('li').addClass('active').text(clicked_nav_menu_item)
        $(this).closest('a').remove() // Remove the anchor tag

        // If "SAMPLES" is clicked in the navbar menu then, revert to the initial view of web page
        // when a profile that has samples was clicked
        if (clicked_nav_menu_item === "SAMPLES") {
            $(document).data("selectedProfileID", current_profileID)
            // get_profile_titles(project) // Get all profile titles
            // $(document).data("searchByFaceting", false);
            get_profile_titles_nav_tabs() // Get profile types
            highlight_empty_cells_in_selected_row()
            const profile_titles_row = $("#profile_titles tr")
            const profile_titles_row_count = profile_titles_row.length - 1

            // Select profile title based on the index of the selected profile ID
            let profile_title_row_index = $(document).data("selectedProfileID") && $(document).data("searchByFaceting")
                ? $('td[data-profile_id*=' + $(document).data("selectedProfileID") + ']').index($(this).closest('tr'))
                : 1

            // '-1' is not recognised as the last index in the profile_titles_row array
            // so set the last index to be the length of the array
            profile_title_row_index = profile_title_row_index === -1 ? profile_titles_row_count : profile_title_row_index

            profile_titlesID.find(".selected").removeClass("selected")

            $(profile_titles_row[profile_title_row_index]).addClass("selected") // Add the selected class to the first profile displayed

            $(profile_titles_row[profile_title_row_index]).click() // Click on the selected profile title

        } else {
            // Get samples based on the selected nav menu item
            // Clear/empty the 'profile_samples' table is any samples are displayed
            if ($.fn.DataTable.isDataTable('#profile_samples')) {
                $("#profile_samples").DataTable().clear().destroy();

            }
            get_samples(profile_titles_row[1], project)
        }
    });

    // Get active manifest type tab on tab change
    $('#profile_types_filter').bind('click', function (e) {
        $(document).data("selectedProfileID", "") //  Reset the selected profile ID
        let project = $(e.target).attr("href")
        get_profile_titles(project)
    });
    get_profile_titles_nav_tabs() // Get profile types
    highlight_empty_cells_in_selected_row()
});

function get_profile_titles_nav_tabs() {
    // check profiles
    let queryUserProfileRecordsCheckBox = $(document).data("queryUserProfileRecordsCheckBox") ?? true
    let profile_titles_nav_bar = $("#profile_types_filter")
    let profile_titles_liTag = $('#profile_types_filter li')
    let profile_titlesID = $("#profile_titles")
    let profile_titles_row = $("#profile_titles tr")


    $.ajax({
        url: "/copo/get_profile_titles_nav_tabs",
        method: "GET",
        dataType: "json",
        data: {
            'queryUserProfileRecords': queryUserProfileRecordsCheckBox
        }
    }).error(function (e) {
        console.log(`Error: ${e.message}`);
    }).done(function (data) {
        // Populate the nav bar/tab of the profile titles table on the left of the web page
        // with profile titles
        data.forEach(function (profile_type, index) {
            const li = $("<li/>", {
                class: "hot_tab in"
            });

            const a = $("<a/>", {});


            if ($(document).data("selectedProfileID")) {
                //  Set the profile type of the selected profile to be the first tab to be displayed
                const project = $("#profile_types_filter").find(".active").find("a").attr("href");

                if (profile_type === project) {
                    // If data exists within the 'profile_types_filter' ul tag, remove it
                    if (profile_titles_liTag.length > 0) $('#profile_types_filter li').remove();
                    $(li).addClass("active")
                    get_profile_titles(project) // Get the profile titles for the first profile type

                    let profile_titles_row_count = $("#profile_titles tr").length - 1
                    // Highlight the selected profile title
                    $(document).data("searchByFaceting", false)
                    let profile_title_row_index = $(document).data("selectedProfileID")
                        ? $('td[data-profile_id*=' + $(document).data("selectedProfileID") + ']').index($(this).closest('tr'))
                        : 1
                    profile_titlesID.find(".selected").removeClass("selected")

                    // '-1' is not recognised as the last index in the profile_titles_row array
                    // so set the last index to be the length of the array
                    profile_title_row_index = profile_title_row_index === -1 ? profile_titles_row_count : profile_title_row_index

                    $(profile_titles_row[profile_title_row_index]).addClass("selected") // Add the selected class to the first profile displayed

                }
            } else {
                //  Set the first profile type (in alphabetical order) to be the first tab to be displayed
                if (index === 0) {
                    $(li).addClass("active")
                    get_profile_titles(profile_type) // Get the profile titles for the first profile type
                }
            }

            a.attr("data-toggle", "tab");
            a.attr("data-type", "tab");
            a.attr("href", profile_type);
            a.text(profile_type);

            li.append(a);

            profile_titles_nav_bar.append(li);
        });
    })

}

function build_form_body_sample_Details(data, form) {
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
    const messageRowDiv = $('<div/>',
        {
            class: "row"
        });

    const messageColDiv = $('<div/>',
        {
            class: "col-sm-12 col-md-12 col-lg-12 formMessageDiv"
        });

    messageRowDiv.append(messageColDiv);

    let message_text = null;
    let message_type = null;


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
    } else if (row[el] === "" || row[el] === " ") {
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
    } else if (row[el] === "" || row[el] === " ") {
        td.className = "empty_color"
    }
    td_row.appendChild(td)
}

function set_up_form_show_all_fields_checkbox_div() {
    const project = $("#profile_types_filter").find(".active").find("a").attr("href");

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
            id: "queryUserProfileRecordsCheckBoxID",
            type: "checkbox",
            style: "margin-left:10px;",

        });


    if ($("#queryCOPORecordsCheckBoxID").is(":checked")) {
        $(document).data("queryUserProfileRecordsCheckBoxID", false)
        showQuerySamplesCheckBox.prop("disabled", true);
        showQuerySamplesCheckBox.attr("title", "Search query within COPO records is enabled. Uncheck to query in user profile records")


    } else {
        showQuerySamplesCheckBox.attr('checked', 'checked')
        showQuerySamplesCheckBox.attr('title', 'Once unchecked and a field name listed below is selected, samples within COPO record that matches the selected field name and its corresponding field value are displayed')

    }

    querySamplesCheckBoxLabel.text('Query profile for ' + project + ' samples: ')
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
        onhide: function () {
            // Unhighlight the selected/clicked sample table row
            $('#profile_samples').find('.selected_row').removeClass('selected_row');

            // Highlight first profile title displayed in the profile titles table row....
            // this becomes unhighlighted for some strange reason so highlight it again
            $("#profile_titles").find(".selected").removeClass("selected")
            $($("#profile_titles tr")[1]).addClass("selected")
        },
        onshown: function () {

            //prevent enter keypress from submitting form automatically
            $("form").keypress(function (e) {
                //Enter key
                if (e.which === 13) {
                    return false;
                }
            });

            const event = jQuery.Event("postformload"); // Individual components can trap and handle this event as they so wish
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

            document.querySelector("#queryUserProfileRecordsCheckBoxID").onchange = (e) => {
                let queryCOPORecordsCheckBoxID = $("#queryCOPORecordsCheckBoxID")
                let checked = e.target.checked;
                if (checked) {
                    $(document).data("queryCOPORecordsCheckBox", false)

                    if (queryCOPORecordsCheckBoxID.is(":checked")) {

                        queryCOPORecordsCheckBoxID.prop('checked', $(document).data("queryCOPORecordsCheckBox"));
                        queryCOPORecordsCheckBoxID.prop("disabled", true);
                        queryCOPORecordsCheckBoxID.attr("title", "Search query within user profile records is enabled. Uncheck query in COPO profile records in prder tp query in user profile records")

                    } else {
                        queryCOPORecordsCheckBoxID.prop("disabled", true);
                        queryCOPORecordsCheckBoxID.attr("title", "Search query within user profile records is enabled. Uncheck query in COPO profile records in prder tp query in user profile records")
                    }


                }
                $(document).data("queryUserProfileRecordsCheckBox", checked)
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

function get_profile_titles_on_queryCOPORecordsCheckBoxID() {
    if ($("#queryCOPORecordsCheckBoxID").is(":checked")) {
        $(document).data("queryCOPORecordsCheckBox", true)
        $(document).data("queryUserProfileRecordsCheckBox", false)
        const project = $("#profile_types_filter").find(".active").find("a").attr("href");
        get_profile_titles(project)

        // Remove the 'selected' class from any previously selected profile listed
        $("#profile_titles").find(".selected").removeClass("selected")
        const profile_titles_row = $("#profile_titles tr")
        $(profile_titles_row[1]).addClass("selected") // Add the selected class to the first profile displayed

        // Clear/empty the 'profile_samples' table is any samples are displayed
        if ($.fn.DataTable.isDataTable('#profile_samples')) {
            $("#profile_samples").DataTable().clear().destroy();

        }
        get_samples(profile_titles_row[1], project) // Populate samples table with samples from the first profile displayed
    } else {
        $(document).data("queryCOPORecordsCheckBox", false)
        $(document).data("queryUserProfileRecordsCheckBox", true)
    }
}

function get_samples(row, project) {
    let profile_id = $(row).find("td").data("profile_id")
    let s;
    let searchByFaceting = $(document).data("searchByFaceting")
    s = determine_sample_request_data(row, profile_id, project)

    $("#profile_id").val(profile_id)
    $("#spinner").show()

    $.ajax(s).done(function (data) {
            let sample_panel_tol_inspect = $("#sample_panel_tol_inspect")

            if ($.fn.DataTable.isDataTable('#profile_samples')) {
                $("#profile_samples").DataTable().clear().destroy();

            }
            sample_panel_tol_inspect.find("thead").empty()
            sample_panel_tol_inspect.find("tbody").empty()

            // Show only 13 rows when copo_dashboard web page is displayed
            // Correlates with height of data table scroll bar
            data = window.location.href.includes('dashboard') ? data.slice(0, 12) : data

            if (data.length) {
                // If the search is not by faceting then, display the 'Samples' header as the active header
                if (!searchByFaceting) {
                    const header = $("<h4/>", {
                        html: "Samples"
                    });

                    sample_panel_tol_inspect.find(".labelling").empty().append(header)

                    // Create page top navigation
                    const navMenu = $("<li/>", {
                        class: "active"
                    });

                    navMenu.text("SAMPLES")

                    // Add 'SAMPLES' to the global navBarItems list
                    $(document).data("navBarItems", [])
                    $(document).data("navBarItems").push('SAMPLES')

                    $("#tolInspectNavBar").find(".breadcrumb").empty().append(navMenu)
                }

                // Show the breadcrumb/ navigation bar is samples exist on tol_inspect web page
                if (!window.location.href.includes('dashboard')) $("#tolInspectNavBar").find(".breadcrumb").show()

                const rows = [];

                // Get the value of the showAllTableFields checkbox
                let areAllTableFieldsShown = $(document).data("showAllTableFieldsCheckBox");

                $(data).each(function (idx, row) {
                    let td;
                    let sample_id;
                    let excluded_fields_tol_inspect;
                    let included_fields_tol_inspect;

                    const th_row = document.createElement("tr");
                    const td_row = document.createElement("tr");

                    // add field names here which you don't want to appear in the supervisors table
                    excluded_fields_tol_inspect = ["profile_id", "biosample_id"]
                    // add field names here which you want to appear in the 'tol_inspect' samples' table
                    included_fields_tol_inspect = ["SPECIMEN_ID", "SCIENTIFIC_NAME", "public_name"]

                    td_row.className = "sample_table_row"

                    if (idx === 0) {
                        // do header and row
                        const empty_th = document.createElement("th");
                        th_row.appendChild(empty_th)
                        td = document.createElement("td");
                        td.className = "index"
                        td.style.textAlign = "center"
                        td.innerHTML = idx + 1 // Increment by 1 because default numbering system starts at 0
                        td_row.appendChild(td)

                        for (let el in row) {
                            if (el === "_id") {
                                sample_id = row._id.$oid ?? row._id
                                td_row.setAttribute("id", sample_id)
                                $(td_row).attr("sample_id", sample_id)
                            } else if (!areAllTableFieldsShown && included_fields_tol_inspect.includes(el)) {
                                get_profile_samples_table_first_element_block_of_code(el, td, row, th_row, td_row)
                            } else if (areAllTableFieldsShown && !excluded_fields_tol_inspect.includes(el)) {
                                get_profile_samples_table_first_element_block_of_code(el, td, row, th_row, td_row)
                            }
                        }
                        document.getElementById("profile_samples").getElementsByTagName("thead")[0].appendChild(th_row)
                        document.getElementById("profile_samples").getElementsByTagName("tbody")[0].appendChild(td_row)

                    } else {
                        // if not first element
                        td = document.createElement("td")
                        td.className = "index"
                        td.style.textAlign = "center"
                        td.innerHTML = idx + 1  // Increment by 1 because default numbering system starts at 0
                        td_row.appendChild(td)

                        for (let el in row) {
                            if (el === "_id") {
                                sample_id = row._id.$oid ?? row._id
                                td_row.setAttribute("id", sample_id)
                                td_row.setAttribute("sample_id", sample_id)
                            } else if (!areAllTableFieldsShown && included_fields_tol_inspect.includes(el)) {
                                get_profile_samples_table_not_first_element_block_of_code(el, row, td_row)
                            } else if (areAllTableFieldsShown && !excluded_fields_tol_inspect.includes(el)) {
                                get_profile_samples_table_not_first_element_block_of_code(el, row, td_row)
                            }
                        }
                        $(td_row).css({"text-align": "center"})
                        $(td_row).css({"width": "360px"})
                        rows.push(td_row)
                    }

                })

                fastdom.mutate(() => {
                    let profile_samples = $("#profile_samples");
                    let showAllTableFieldsCheckBoxID = $("#showAllTableFieldsCheckBoxID")
                    let queryCOPORecordsCheckBoxID = $("#queryCOPORecordsCheckBoxID")
                    let queryUserProfileRecordsCheckBoxID = $("#queryUserProfileRecordsCheckBoxID")
                    const tbody = document.getElementById("profile_samples").getElementsByTagName('tbody')[0];

                    rows.forEach(el => {
                        tbody.appendChild(el)
                    })
                    profile_samples.DataTable(profile_samples_dt_options);

                    // Re-configure 'profile_samples' table options if 'copo_dashboard' is displayed
                    if (window.location.href.includes('dashboard')) {
                        profile_samples_dt_options.lengthMenu = [15]
                        profile_samples_dt_options.bLengthChange = false //  Remove the 'show entries' droppdown menu option
                        profile_samples_dt_options.scrollY = 450 // Correlates with number of table rows
                        profile_samples_dt_options.autoWidth = true
                        profile_samples_dt_options.bPaginate = false // Removes table pagination
                        profile_samples_dt_options.bFilter = false // Removes table search box
                        profile_samples_dt_options.bInfo = false
                        profile_samples_dt_options.scrollX = false // Turns off maximum column width
                        profile_samples_dt_options.sScrollX = 525 // Sets column headers' width

                        profile_samples.DataTable().destroy()
                        profile_samples.DataTable(profile_samples_dt_options);
                    }

                    // Add checkbox to show all fields within the table beside the search box
                    // within the profile samples data table
                    let showAllTableFieldsCheckbox_html = '<label style="padding-right: 40px"> Show all fields: <input id="showAllTableFieldsCheckBoxID" style="padding-right:20px" type="checkbox" onclick="populate_samples_table_based_on_profile_title(this)"></label>'
                    let filterByCOPODatabaseIDCheckbox_html = '<label style="padding-right: 30px"> Query in<span class="font-weight-bold ms-1"> COPO </span>record:<input id="queryCOPORecordsCheckBoxID" onclick="get_profile_titles_on_queryCOPORecordsCheckBoxID(this)" style="padding-right:20px; margin-right:8px" type="checkbox"">' +
                        '                                     </label>'

                    // Create a div that has checkboxes on the same row
                    let profileSamplesTable_checkBoxesDiv = $('<div id="profileSamplesTable_checkBoxesDiv" style="display: inline;"> </div>')
                    profileSamplesTable_checkBoxesDiv.append(showAllTableFieldsCheckbox_html)
                    profileSamplesTable_checkBoxesDiv.append(filterByCOPODatabaseIDCheckbox_html)


                    $("#profile_samples_filter").prepend(profileSamplesTable_checkBoxesDiv)

                    showAllTableFieldsCheckBoxID.prop('checked', $(document).data("showAllTableFieldsCheckBox"));
                    queryCOPORecordsCheckBoxID.prop('checked', $(document).data("queryCOPORecordsCheckBox"));

                    //Only show the checkboxes on tol_inspect web page
                    if (!window.location.href.includes('dashboard')) {
                        document.querySelector("#showAllTableFieldsCheckBoxID").onchange = (e) => {
                            let checked = e.target.checked;
                            $(document).data("showAllTableFieldsCheckBox", checked);
                        }


                        document.querySelector("#queryCOPORecordsCheckBoxID").onchange = (e) => {
                            let checked = e.target.checked;
                            if (checked) {
                                $(document).data("queryUserProfileRecordsCheckBox", false)
                                if (queryUserProfileRecordsCheckBoxID.is(":checked")) {

                                    queryUserProfileRecordsCheckBoxID.prop('checked', $(document).data("queryUserProfileRecordsID"));
                                    queryUserProfileRecordsCheckBoxID.prop("disabled", true);
                                    queryUserProfileRecordsCheckBoxID.attr("title", "Search query within user profile records is enabled. Uncheck query in COPO profile records in prder tp query in user profile records")
                                } else {
                                    queryUserProfileRecordsCheckBoxID.prop("disabled", true);
                                    queryUserProfileRecordsCheckBoxID.attr("title", "Search query within user profile records is enabled. Uncheck query in COPO profile records in prder tp query in user profile records")
                                }
                            }
                            $(document).data("queryCOPORecordsCheckBox", checked);
                        }
                    }

                    showAllTableFieldsCheckBoxID.prop('checked', $(document).data("showAllTableFieldsCheckBox"));
                    queryCOPORecordsCheckBoxID.prop('checked', $(document).data("queryCOPORecordsCheckBox"));

                    // Hide 'profileSamplesTable_checkBoxesDiv' div and disable its child checkboxes
                    // 'Show all fields' checkbox and 'Query in COPO record' checkbox
                    // when on dashboard web page
                    if (window.location.href.includes('dashboard')) {
                        showAllTableFieldsCheckBoxID.prop("disabled", true);
                        queryCOPORecordsCheckBoxID.prop("disabled", true);
                        $("#profileSamplesTable_checkBoxesDiv").hide()
                    }

                })
                highlight_empty_cells_in_selected_row()
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
                sample_panel_tol_inspect.find(".labelling").empty().html(
                    content
                )
                // Increase padding of the 'tol inspect" card if 'No Samples Found' message
                // is shown on dashboard web page
                if (window.location.href.includes('dashboard')) {
                    sample_panel_tol_inspect.find(".h4").css("padding-top", "200px").css("text-align", "center");
                    $(".tol_inspect_card").addClass("tol_inspect_card_padding")
                    $(".tol_inspect_card > div").addClass("mb-3")

                }

                // Hide navbar menu if no sample records exist in a profile
                $("#tolInspectNavBar").find(".breadcrumb").empty().html("").hide()
                $(document).data("navBarItems", [])
            }


            $("#spinner").fadeOut("fast")
        }
    ).error(function (error) {
        console.error(`Error: ${error.message}`)
    })
}

function populate_samples_table_based_on_profile_title(ev) {
    // Get samples for the profile clicked in the left-hand panel and
    // populate the table in the right-hand panel
    jQuery.support.cors = true;
    let row;

    if ($(ev.currentTarget).is("td") || $(ev.currentTarget).is("tr")) {
        // we have clicked a profile on the left hand list
        $(document).data("selected_profile_title_row", $(ev.currentTarget))
        row = $(document).data("selected_profile_title_row") ?? $(ev.currentTarget)
        $("#profile_titles").find(".selected").removeClass("selected")
        $(row).addClass("selected")
    } else {
        row = $(document).data("selected_profile_title_row")
    }

    const project = $("#profile_types_filter").find(".active").find("a").attr("href");

    get_samples(row, project)
}

function get_profile_titles(data) {
    // get profiles with samples needing looked at and populate left hand column
    let searchQueryDict = $(document).data("searchQuery")
    let match_items = JSON.stringify(data)
    let queryUserProfileRecordsCheckBox = $(document).data("queryUserProfileRecordsCheckBox")
    let queryCOPORecordsCheckBox = $(document).data("queryCOPORecordsCheckBox") ?? false
    let getProjectTitlesForUserOnly = !!($.isEmptyObject(searchQueryDict) && queryUserProfileRecordsCheckBox && !queryCOPORecordsCheckBox)
    let searchByFaceting = typeof (data) !== 'string'
    let profile_titles_nav_bar = $("#profile_types_filter")

    $(document).data("searchByFaceting", searchByFaceting);

    // If data is of type 'string' i.e. the value of data is 'project type', search by faceting is not required
    // else if data is of type 'object' (dictionary) i.e. the value of data is 'match_items' data,
    // search by faceting is required
    data = searchByFaceting ? match_items : data

    $.ajax({
        url: "/copo/get_profiles_for_tol_inspection/",
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        method: "POST",
        dataType: "json",
        data: {
            "data": data,
            "searchByFaceting": searchByFaceting,
            "getProjectTitlesForUserOnly": getProjectTitlesForUserOnly
        }
    }).error(function (e) {
        console.error(e)
    }).done(function (data) {
        let profile_titlesID = $("#profile_titles")
        let profile_titles_liTag = $('#profile_types_filter li')

        // Clear existing data in the profile titles' table
        if ($.fn.DataTable.isDataTable('#profile_titles')) {
            profile_titlesID.DataTable().clear().destroy();
        }

        // Populate the nav bar/tab of the profile titles table
        // on the left of the web page with profile titles
        if (Object.hasOwn(data, "projects")) {
            // Get get_profile_titles_nav_tabs
            // If data exists within the ul tag, remove it
            if (profile_titles_liTag.length > 0) $('#profile_types_filter li').remove();
            data["projects"].forEach(function (profile_type, index) {
                // Set Profile titles nav tab
                const li = $("<li/>", {
                    class: "hot_tab in"
                });

                const a = $("<a/>", {});

                //  Set the first profile type (in alphabetical order) to be the first tab to be displayed
                if (index === 0) {
                    $(li).addClass("active")
                }

                a.attr("data-toggle", "tab");
                a.attr("data-type", "tab");
                a.attr("href", profile_type);
                a.text(profile_type);

                li.append(a);

                profile_titles_nav_bar.append(li);
            })
        }

        // Set profile titles
        $(data['profiles']).each(function (d) {
            let date = new Date(data['profiles'][d].date_created.$date).toLocaleDateString('en-GB', {timeZone: 'UTC'})
            let profile_id = searchByFaceting ? data['profiles'][d]._id : data['profiles'][d]._id.$oid

            profile_titlesID.find("tbody").append("<tr class='profile_title_selectable_row'><td style='max-width: 10px' data-profile_id='" + profile_id + "'>" + data['profiles'][d].title + "</td><td style='text-align: center'>" + date + "</td><td style='text-align: center'>" + data['profile_samples_count'][d] + "</td></tr>")

        })

        const profile_titles_row = $("#profile_titles tr")
        const profile_titles_row_count = profile_titles_row.length - 1

        console.log("selectedProfileID:", $(document).data("selectedProfileID"))

        let profile_title_row_index = $(document).data("selectedProfileID")
            ? $('td[data-profile_id*=' + $(document).data("selectedProfileID") + ']').index($(this).closest('tr'))
            : 1

        // '-1' is not recognised as the last index in the profile_titles_row array
        // so set the last index to be the length of the array
        profile_title_row_index = profile_title_row_index === -1 ? profile_titles_row_count : profile_title_row_index

        if (searchByFaceting) {
            profile_titlesID.find(".selected").removeClass("selected")


            $(profile_titles_row[profile_title_row_index]).addClass("selected") // Add the selected class to the first profile displayed

            // Clear/empty the 'profile_samples' table if any samples are displayed
            if ($.fn.DataTable.isDataTable('#profile_samples')) {
                $("#profile_samples").DataTable().clear().destroy();
            }

            // Get active project/profile type
            const project = $("#profile_types_filter").find(".active").find("a").attr("href");

            // Get samples for active profile type
            get_samples(profile_titles_row[profile_title_row_index], project) // Populate samples table with samples from the first profile displayed
        } else {
            $(profile_titles_row[profile_title_row_index]).click()
        }


        $.fn.dataTable.moment('DD/MM/YYYY');
        profile_titlesID.DataTable({
            responsive: true,
            paging: false,
            destroy: true,
            dom: '<"top"f>rt<"bottom"lp><"clear">',
            "order": [[1, "desc"]],

        })

    })
}

function highlight_empty_cells_in_selected_row() {
    // Highlight all cells in a row when the row is clicked even cells that are empty
    let table_rows = document.querySelectorAll(".sample_table_row");

    table_rows.forEach(row => {
        if (row.classList.contains('selected_row')) {
            // Highlight empty cells by removing "empty_color" class from them
            row.childNodes.forEach(td => {
                if (td.classList.contains("empty_color") && td.innerHTML.trim() === "") {
                    td.classList.remove("empty_color");
                }
            })
        } else {
            // Add "empty_color" class to cells that have no text i.e cells that are empty
            row.childNodes.forEach(td => {
                if (!td.classList.contains("empty_color") && td.innerHTML.trim() === "") {
                    td.classList.add("empty_color");
                }

            })

        }
    })
}


function determine_sample_request_data(row, profile_id, project) {
    let match_items;
    let searchQueryDict_with_profileID;
    let project_field_name = "tol_project"
    let searchQueryDict = $(document).data("searchQuery") ?? {}
    let clicked_nav_menu_item = $(document).data("clicked_nav_menu_item") ?? null
    let navBarItems = $(document).data("navBarItems")

    searchQueryDict[project_field_name] = project

    // If nav menu item is clicked, get samples based on the nav menu item clicked
    // i.e. get match_items based on the nav menu item clicked
    // Else, get active nav menu item and get samples based on the active nav menu item
    if (clicked_nav_menu_item) {
        // Get match_items based on the nav menu item clicked
        let all_object_keys = Object.keys(searchQueryDict)
        let clicked_nav_menu_item_index = all_object_keys.indexOf(clicked_nav_menu_item)

        let searchQueryDict_based_on_clickedNavItem = all_object_keys.slice(0, clicked_nav_menu_item_index + 1).reduce((result, key) => {
            result[key] = searchQueryDict[key];
            return result;
        }, {});

        // Set navBarItems according to the clicked nav menu item
        navBarItems = navBarItems.slice(0, clicked_nav_menu_item_index + 1)
        $(document).data("navBarItems", navBarItems)

        // Set searchQueryDict according to the clicked nav menu item
        searchQueryDict = $(document).data("searchQuery", searchQueryDict_based_on_clickedNavItem)

        // Include the active profile ID to perform the MongoDB match aggregation query
        searchQueryDict_with_profileID = {...{"profile_id": profile_id}, ...searchQueryDict_based_on_clickedNavItem}
    } else {
        // Include the active profile ID to perform the MongoDB match aggregation query
        searchQueryDict_with_profileID = {...{"profile_id": profile_id}, ...searchQueryDict}
    }

    match_items = JSON.stringify(searchQueryDict_with_profileID)

    return {
        url: "/copo/get_samples_by_search_faceting/",
        data: {"match_items": match_items},
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        method: "POST",
        dataType: "json"
    };
}