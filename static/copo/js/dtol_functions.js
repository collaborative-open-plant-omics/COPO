$(document).ready(function () {
    // functions defined here are called from both copo_sample_accept_reject and copo_samples, all provide DTOL
    // functionality
    $(document).data("accepted_warning", false)
    $(document).data("isDtolSamplePage", true)
    $("#accept_reject_button").find("button").prop("disabled", true)
    // add field names here which you don't want to appear in the supervisors table
    excluded_fields = ["profile_id", "biosample_id"]
    included_fields = ["SPECIMEN_ID", "SCIENTIFIC_NAME", "public_name"] // for "tol_inspect" web page
    // populate profiles panel on left
    let currentURL = window.location.href
    currentURL.includes("tol_inspect") ? tol_inspect_update_pending_samples_table() : update_pending_samples_table()

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

    $(document).on("click", ".sample_table_row", function (el) {
        let columns = []
        let row_values = []
        let sample_details_table_columns_count = document.getElementById("profile_samples").getElementsByTagName("thead")[0].rows[0].cells.length - 1
        console.log('Number of columns in the table: ', sample_details_table_columns_count)


        console.log("Current target: ", $(el.currentTarget))

        let specimen_ID = $(el.currentTarget).find("td").eq(1).html()
        console.log("Selected row SPECIMEN_ID: ", specimen_ID)

        // Retrieve the column names and row values from the sample details table starting from column 1
        let range = [...Array(sample_details_table_columns_count).keys()].map(i => i + 1);
        columns = range.map(i => $(el.currentTarget).parent().siblings().find("th>div").eq(i).html())
        console.log("Column values: ", columns)

        row_values = range.map(i => $(el.currentTarget).find("td").eq(i).html())
        console.log("Row values: ", row_values)

        let sample_id = el.currentTarget.id
        console.log("Sample ID: ", sample_id)


        $(el.currentTarget).parent().siblings().addBack().each(function (idx, el) {
            $(el).toggleClass("selected_row")
        })
        csrftoken = $.cookie('csrftoken');
        const component = "profile_sample_details" //"profile_sample_details";
        const copoFormsURL = "/copo/copo_forms/";
        const errorMsg = "Couldn't build Sample Details' form!";


        // console.log(document.getElementById("profile_samples").getElementsByTagName("th")[0].innerText)
        //
        //
        // console.log(document.getElementById("profile_samples").getElementsByTagName("td")[1].innerText)

        // json2HtmlForm_SampleDetails(specimen_ID, columns, row_values);
        $.ajax({
            url: "/copo/get_sample_details/",
            method: "POST",
            headers: {'X-CSRFToken': csrftoken},
            dataType: "json",
            data: {
                'sample_id': sample_id,
                'specimen_id': specimen_ID
            },
            success: function (data) {
                json2HtmlForm_SampleDetails(data);
            },
            error: function () {
                alert(errorMsg);
            }
        });
    })

    $(document).on("click", "#accept_reject_button button", handle_accept_reject)

    // handle clicks on both profiles (.selectable_row), and filter (.hot_tab)
    currentURL.includes("tol_inspect") ? $(document).on("click", ".selectable_row, .hot_tab", row_select_on_tol_inspect_web_page)
        : $(document).on("click", ".selectable_row, .hot_tab", row_select)

    // $(document).on("click", "#showFieldsID", row_select_on_tol_inspect_web_page)

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

function get_profile_samples_table_block_of_code(el, td, row, th_row, td_row) {

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
    // just do row
    // td = $("<td/>", {
    //     html: row[el]
    // })
    let td = document.createElement("td")
    td.innerHTML = row[el]
    if (row[el] === 'NA') {
        td.className = "na_color"
    } else if (row[el] === "") {
        td.className = "empty_color"
    }
    td_row.appendChild(td)
}

function row_select_on_tol_inspect_web_page(ev) {
    // Get samples for the profile clicked in the left-hand panel and
    // populate the table in the right-hand panel
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

    var project = $("#sample_filter").find(".active").find("a").attr("href")

    var d = {"profile_id": $(row).find("td").data("profile_id"), "project": project}
    $("#profile_id").val(d.profile_id)


    $("#spinner").show()

    $.ajax({
        url: "/copo/get_project_samples_for_tol_inspection",
        data: d,
        method: "GET",
        dataType: "json"
    }).error(function (data) {
        console.error("ERROR: " + data)
    }).done(function (data) {
            // Get value of the checkbox to show all fields in the profile samples table
            let checkBox = document.getElementById("showFieldsID");
            let areAllTableFieldsShown = checkBox == null ? false : checkBox.checked;  // set false as default value
            let areAllTableFieldsShown1 = localStorage.getItem("areAllTableFieldsShown") === 'true';
            console.log("areAllTableFieldsShown1", areAllTableFieldsShown1)
            console.log("areAllTableFieldsShown2", areAllTableFieldsShown)
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
                $("#sample_panel").find(".labelling").empty().append(header)

                const rows = [];
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
                                console.log("Are all fields shown: ", areAllTableFieldsShown)
                                get_profile_samples_table_block_of_code(el, td, row, th_row, td_row)
                                localStorage.setItem("areAllTableFieldsShown", "false");
                                $("#showFieldsID").prop('checked', false);
                            } else if (areAllTableFieldsShown && !excluded_fields.includes(el)) {
                                console.log("Are all fields shown: ", areAllTableFieldsShown)
                                get_profile_samples_table_block_of_code(el, td, row, th_row, td_row)
                                localStorage.setItem("areAllTableFieldsShown", "true");
                                $("#showFieldsID").prop('checked', true);
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
                                // Set/store show all table fields checkbox value in local storage
                                // because value is reset once page is reloaded
                                localStorage.setItem("areAllTableFieldsShown", "false");
                                $("#showFieldsID").prop('checked', false);
                            } else if (areAllTableFieldsShown && !excluded_fields.includes(el)) {
                                get_profile_samples_table_not_first_element_block_of_code(el, row, td_row)
                                // Set/store show all table fields checkbox value in local storage
                                // because value is reset once page is reloaded
                                localStorage.setItem("areAllTableFieldsShown", "true");
                                $("#showFieldsID").prop('checked', true);
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
            }

            $("#spinner").fadeOut("fast")

        }
    )
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


function tol_inspect_update_pending_samples_table() {
    // get profiles with samples needing looked at and populate left hand column
    const project = $("#sample_filter").find(".active").find("a").attr("href");

    $.ajax({
        url: "/copo/tol_inspect_update_pending_samples_table",
        method: "GET",
        dataType: "json",
        data: {
            "project": project
        }
    }).error(function (e) {
        console.error(e)
    }).done(function (data) {
        $(data['profiles']).each(function (d) {
            let date = new Date(data['profiles'][d].date_created.$date).toLocaleDateString('en-GB', {timeZone: 'UTC'})
            $("#profile_titles").find("tbody").append("<tr class='selectable_row'><td style='max-width: 10px' data-profile_id='" + data['profiles'][d]._id.$oid + "'>" + data['profiles'][d].title + "</td><td style='text-align: center'>" + date + "</td><td style='text-align: center'>" + data['profile_samples_count'] + "</td></tr>")

        })
        // $($("#profile_titles tr")[1]).css({})
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
