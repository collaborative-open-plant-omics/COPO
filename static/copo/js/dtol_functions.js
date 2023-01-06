$(document).ready(function () {
    // functions defined here are called from copo_sample_accept_reject, copo_samples and copo_tol_inspect, all provide DTOL
    // functionality
    let currentURL = window.location.href
    const project = $("#sample_filter").find(".active").find("a").attr("href");

    // add field names here which you don't want to appear in the supervisors table
    excluded_fields = ["profile_id", "biosample_id"]
    // add field names here which you want to appear in the 'tol_inspect' samples' table
    included_fields = ["SPECIMEN_ID", "SCIENTIFIC_NAME", "public_name"]

    $(document).data("accepted_warning", false)
    $(document).data("isDtolSamplePage", true)
    $(document).data("areAllSampleModalFieldsShown", false)
    $(document).data("showAllTableFieldsCheckbox", false);
    $(document).data("isSampleModalSearchQueryChecked", true);
    $(document).data("navBarItems", [])
    $(document).data("navBarItemsTableBodyView", {})
    $(document).data("searchQuery", {})


    $(document).on("click", ".select-all", function () {
        $(".form-check-input:not(:checked)").each(function (idx, element) {
            $(element).click()
        })
    })

    $(document).on("click", ".select-none", function () {
        $(".form-check-input:checked").each(function (idx, element) {
            $(element).click()
        })
    })

    $(document).on("click", "tr.sample_table_row", function (e) {
        let cb;
        if (currentURL.includes("tol_inspect")) {
            cb = $($(e.target).siblings(".tickbox").find("input"));
            cb.click()
        } else {
            cb = $($(e.target).siblings(".tickbox").find("input"));
            cb.click()
        }
    })

    $(document).on("click", ".delete-selected", function (e) {

        var saved_text = $("#dtol_sample_info").text()
        BootstrapDialog.show({
            title: "Delete Samples",
            message: "Are you sure you want to delete?",
            buttons: [{
                label: 'Close',
                action: function (dialogItself) {
                    dialogItself.close();
                }
            },
                {
                    label: 'Delete',
                    action: function (dialog) {


                        $("#dtol_sample_info").text("Deleting")

                        var csrftoken = $.cookie('csrftoken');
                        var checked = $(".form-check-input:checked").closest("tr")
                        var sample_ids = []
                        $(checked).each(function (it) {
                            sample_ids.push($(checked[it]).data("id"))
                        })
                        console.log(sample_ids)
                        $.ajax({
                            headers: {'X-CSRFToken': csrftoken},
                            url: "/copo/delete_dtol_samples/",
                            method: "POST",
                            data: {
                                sample_ids: JSON.stringify(sample_ids)
                            }
                        }).done(function (e) {
                            $("#profile_titles").find(".selected").click()
                            dialog.close()
                        }).error(function (e) {
                            console.error(e)
                        })
                    }
                }
            ]
        })


    })

    $(document).on("click", ".form-check-input", function (el) {

        if ($(".form-check-input:checked").length) {
            $("#accept_reject_button").find("button").prop("disabled", false)
        } else {
            $("#accept_reject_button").find("button").prop("disabled", true)
        }
        $(el.currentTarget).parent().siblings().addBack().each(function (idx, el) {
            $(el).toggleClass("selected_row")
        })
    })

    $(document).on("click", "#accept_reject_button button", handle_accept_reject)

    $(document).on("change", "#dtol_type_select", function (e) {
        $.ajax({
            url: "/copo/get_subsample_stages",
            method: "GET",
            data: {
                "stage": $(e.currentTarget).val()
            },
            dataType: "json"
        }).done(function (data) {
            $("#accordion").fadeOut(function () {
                $("[id^='section']").find(".collapse").collapse("hide")
                $("[id^='section']").hide()
                $(data).each(function (idx, el) {
                    el = el.replace(" ", "_")
                    el = "section_" + el
                    $("#" + el).show()
                })
                $("#accordion").fadeIn(function () {
                    $(document).find("[id^='section']:visible:first").find(".collapse").collapse('show')
                })
            })
        })
    })

    $(document).on("keyup", "#taxonid", delay(function (e) {
            $("#taxonid").addClass("loading-spinner")
            var taxonid = $("#taxonid").val()
            if (taxonid == "") {
                $("#species, #genus, #family, #order, #commonName").val("")
                $("#species, #genus, #family, #order, #commonName").prop("disabled", false)
                return false
            }
            $.ajax(
                {
                    url: "/copo/resolve_taxon_id",
                    method: "GET",
                    data: {"taxonid": taxonid},
                    dataType: "json"
                }
            ).done(function (data) {
                $("#species, #genus, #family, #order, #commonName").val("")
                $("#species, #genus, #family, #order, #commonName").prop("disabled", false)
                for (var el in data) {
                    var element = data[el]
                    $("#" + el).prop("disabled", true)
                    $("#" + el).val(element)
                }
                $(".loading-spinner").removeClass("loading-spinner")
            }).error(function (error) {
                BootstrapDialog.alert(error.responseText);
            })
        })
    )

    $(document).on("keyup", "#species_search", delay(function (e) {
            var s = $("#species_search").val()
            $.ajax(
                {
                    url: "/copo/search_species",
                    method: "GET",
                    data: {"s": s},
                    dataType: "json"
                }
            ).done(function (data) {
                var ul = $("ul", {
                    class: "species_results"
                })
                $(data).each(function (d) {
                    $(ul).append("<li>", {
                        html: d
                    })
                })
                $("#resultsPanel").append(ul)
            })
        })
    )

    $(document).on("click", "#species", function (e) {
        var disabled = $(e.currentTarget).attr('disabled');

        if (typeof disabled == typeof undefined && disabled !== true) {
            BootstrapDialog.show({
                title: "Search",
                message: $('<div></div>').load("/static/copo/snippets/ncbitaxon_species_search.html")
            })
        }
    })

    // re: tol_inspect web page
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

    // re: accept/reject web page
    $("#accept_reject_button").find("button").prop("disabled", true)

    // re: tol_inspect web page

    // Get active manifest type tab on tab change
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        let project = $(e.target).attr("href")
        update_pending_samples_table_for_tol_inspection(project)
    });

    currentURL.includes("tol_inspect") ? update_pending_samples_table_for_tol_inspection(project) : update_pending_samples_table()

    // re: tol_inspect web page & accept/reject web page
    // handle clicks on both profiles (.selectable_row), and filter (.hot_tab)
    currentURL.includes("tol_inspect") ? $(document).on("click", ".selectable_row, .hot_tab", row_select_on_tol_inspect_web_page)
        : $(document).on("click", ".selectable_row, .hot_tab", row_select)

})

var fadeSpeed = 'fast'
var dt_options = {
    "scrollY": 400,
    "scrollX": true,
    "bSortClasses": false,
    "lengthMenu": [10, 25, 50, 75, 100, 500, 1000, 2000],
    select: {
        style: 'os',
        selector: 'td:first-child'
    },
}

function row_select(ev) {
    $("#accept_reject_button").find("button").prop("disabled", true)
    // get samples for profile clicked in the left hand panel and populate table on the right
    var row;
    if ($(ev.currentTarget).is("td") || $(ev.currentTarget).is("tr")) {
        // we have clicked a profile on the left hand list
        $(document).data("selected_row", $(ev.currentTarget))
        row = $(document).data("selected_row")
        $(".selected").removeClass("selected")
        $(row).addClass("selected")
    } else {
        row = $(document).data("selected_row")
    }

    var filter = $("#sample_filter").find(".active").find("a").attr("href")

    var d = {"profile_id": $(row).find("td").data("profile_id"), "filter": filter}
    $("#profile_id").val(d.profile_id)


    $("#spinner").show()

    $.ajax({
        url: "/copo/get_samples_for_profile",
        data: d,
        method: "GET",
        dataType: "json"
    }).error(function (data) {
        console.error("ERROR: " + data)
    }).done(function (data) {
            if ($.fn.DataTable.isDataTable('#profile_samples')) {
                $("#profile_samples").DataTable().clear().destroy();

            }
            $("#sample_panel").find("thead").empty()
            $("#sample_panel").find("tbody").empty()

            if (data.length) {
                var header = $("<h4/>", {
                    html: "Samples"
                })
                $("#sample_panel").find(".labelling").empty().append(header)

                var rows = []
                $(data).each(function (idx, row) {
                    var th_row = document.createElement("tr")
                    var td_row = document.createElement("tr")
                    td_row.className = "sample_table_row"

                    if (idx == 0) {
                        // do header and row
                        if (filter === "pending" || filter === "rejected") {

                            var empty_th = document.createElement("th")
                            th_row.appendChild(empty_th)
                            var td = document.createElement("td")
                            td.className = "tickbox"

                            var tickbox = $("<input/>",
                                {
                                    "type": "checkbox",
                                    class: "form-check-input"
                                })

                            var tickbox = document.createElement("input")
                            tickbox.type = "checkbox"
                            tickbox.className = "form-check-input"
                            td.appendChild(tickbox)
                            td_row.appendChild(td)

                        }
                        for (el in row) {
                            if (el == "_id") {
                                //$(td_row).data("id", row._id.$oid)
                                td_row.setAttribute("id", row._id.$oid)
                                $(td_row).attr("sample_id", row._id.$oid)
                            } else if (!excluded_fields.includes(el)) {
                                // make header
                                var th = $("<th/>", {
                                    html: el
                                })
                                $(th_row).append(
                                    th
                                )
                                // and row
                                td = $("<td/>", {
                                    html: row[el]
                                })
                                if (row[el] == 'NA') {
                                    $(td).addClass("na_color")
                                } else if (row[el] == "") {
                                    $(td).addClass("empty_color")
                                }
                                $(td_row).append(
                                    td
                                )
                            }
                        }
                        document.getElementById("profile_samples").getElementsByTagName("thead")[0].appendChild(th_row)
                        document.getElementById("profile_samples").getElementsByTagName("tbody")[0].appendChild(td_row)

                    } else { // if not first element
                        if (filter === "pending" || filter === "rejected") {

                            var td = document.createElement("td")
                            td.className = "tickbox"
                            var tickbox = document.createElement("input")
                            tickbox.type = "checkbox"
                            tickbox.className = "form-check-input checkbox"
                            td.appendChild(tickbox)
                            td_row.appendChild(td)
                        }
                        for (el in row) {
                            if (el == "_id") {
                                td_row.setAttribute("id", row._id.$oid)
                                td_row.setAttribute("sample_id", row._id.$oid)
                            } else if (!excluded_fields.includes(el)) {
                                // just do row
                                td = $("<td/>", {
                                    html: row[el]
                                })
                                var td = document.createElement("td")
                                td.innerHTML = row[el]
                                if (row[el] == 'NA') {
                                    td.className = "na_color"
                                } else if (row[el] == "") {
                                    td.className = "empty_color"
                                }
                                td_row.appendChild(td)

                            }

                        }
                        rows.push(td_row)
                    }
                })
                fastdom.mutate(() => {
                    //$("#profile_samples tbody").append(rows)
                    var tbody = document.getElementById("profile_samples").getElementsByTagName('tbody')[0]
                    rows.forEach(el => {
                        tbody.appendChild(el)
                    })
                    $("#profile_samples").DataTable(dt_options);
                })
            } else {
                var content
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
                $("#accept_reject_button").find("button").prop("disabled", true)

            }

            $("#spinner").fadeOut("fast")

        }
    )
}

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

function delay(fn, ms) {
    let timer = 0
    return function (...args) {
        clearTimeout(timer)
        timer = setTimeout(fn.bind(this, ...args), ms || 1000)
    }
}

function update_pending_samples_table() {
    // get profiles with samples needing looked at and populate left hand column
    $.ajax({
        url: "/copo/update_pending_samples_table",
        method: "GET",
        dataType: "json"
    }).error(function (e) {
        console.error(e)
    }).done(function (data) {
        $(data).each(function (d) {
            let date = new Date(data[d].date_created.$date).toLocaleDateString('en-GB', {timeZone: 'UTC'})
            $("#profile_titles").find("tbody").append("<tr class='selectable_row'><td style='max-width: 10px' data-profile_id='" + data[d]._id.$oid + "'>" + data[d].title + "</td><td>" + date + "</td></tr>")
        })
        $($("#profile_titles tr")[1]).click()


        if ($.fn.DataTable.isDataTable('#profile_titles')) {
            $("#profile_titles").DataTable().clear().destroy();

        }
        $.fn.dataTable.moment('DD/MM/YYYY');
        $("#profile_titles").DataTable({
            responsive: true,
            paging: false,
            dom: '<"top"f>rt<"bottom"lp><"clear">',
            "order": [[1, "desc"]],

        })

    })
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

function handle_accept_reject(el) {
    $("#spinner").fadeIn(fadeSpeed)


    var checked = $(".form-check-input:checked").closest("tr")

    var button = $(el.currentTarget)
    var action
    if (button.hasClass("positive")) {
        action = "accept"
    } else {
        action = "reject"
    }
    var sample_ids = []
    $(checked).each(function (it) {
        sample_ids.push($(checked[it]).attr("id"))
    })

    $(checked).each(function (idx, row) {
        $(row).fadeOut(fadeSpeed)
        $(row).remove()

    })

    if (action == "reject") {
        // mark sample object as rejected
        $.ajax({
            url: "/copo/mark_sample_rejected",
            method: "GET",
            data: {"sample_ids": JSON.stringify(sample_ids)}
        }).done(function () {

            $("#profile_titles").find(".selected").click()
            $("#spinner").fadeOut(fadeSpeed)

        })
    } else if (action == "accept") {
        if ($(document).data("accepted_warning")) {
            // create or update dtol submission record
            var profile_id = $("#profile_id").val()
            $("#sub_spinner").fadeIn(fadeSpeed)
            $.ajax({
                url: "/copo/add_sample_to_dtol_submission/",
                method: "GET",
                data: {"sample_ids": JSON.stringify(sample_ids), "profile_id": profile_id},
            }).done(function () {
                $("#profile_titles").find(".selected").click()
                $("#spinner").fadeOut(fadeSpeed)
            })
        } else {
            BootstrapDialog.show({

                title: "ENA Submission",
                message: "By accepting the samples, these will immediately be submitted to ENA. This action is" +
                    " irreversible.",
                cssClass: "copo-modal1",
                closable: true,
                animate: true,
                type: BootstrapDialog.TYPE_INFO,
                buttons: [
                    {
                        label: "Cancel",
                        cssClass: "tiny ui basic" +
                            " button",
                        id: "code_cancel",
                        action: function (dialogRef) {
                            dialogRef.close();
                        }
                    },
                    {
                        label: "Ok",
                        cssClass: "tiny ui basic button",
                        action: function (dialogRef) {
                            dialogRef.close();
                            $(document).data("accepted_warning", true)
                            // create or update dtol submission record
                            var profile_id = $("#profile_id").val()
                            $("#sub_spinner").fadeIn(fadeSpeed)
                            $.ajax({
                                url: "/copo/add_sample_to_dtol_submission/",
                                method: "GET",
                                data: {"sample_ids": JSON.stringify(sample_ids), "profile_id": profile_id},
                            }).done(function () {
                                $("#profile_titles").find(".selected").click()
                                $("#spinner").fadeOut(fadeSpeed)
                            })
                        }
                    }
                ]

            })

        }
    }

}
