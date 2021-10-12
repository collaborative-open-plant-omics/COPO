$(document).ready(function () {
    // functions defined here are called from both copo_sample_accept_reject and copo_samples, all provide DTOL
    // functionality
    $(document).data("isDtolSamplePage", true)
    $("#accept_reject_button").find("button").prop("disabled", true)
    // add field names here which you don't want to appear in the supervisors table
    excluded_fields = ["profile_id", "biosample_id"]
    // populate profiles panel on left
    update_pending_samples_table()

    $(document).on("click", ".select-all", function () {
        $(".form-check-input:not(:checked)").each(function (idx, element) {
            $(element).click()
        })
    })

    $(document).on("click", "#force_btn", handle_accept_reject)

    $(document).on("click", "#dd_reason", function (e) {
        var e = document.getElementById("dd_reason")
        var val = e.value;
        if (val === "other") {
            $("#txt_box_other_reason").prop("disabled", false)
        } else {
            $("#txt_box_other_reason").prop("disabled", true)
        }
    })

    $(document).on("click", ".select-none", function () {
        $(".form-check-input:checked").each(function (idx, element) {
            $(element).click()
        })
    })


    $(document).on("click", "tr.sample_table_row", function (e) {
        var cb = $($(e.target).siblings(".tickbox").find("input"))
        cb.click()
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
            $("#barcode_select").find("button").prop("disabled", false)
        } else {
            $("#accept_reject_button").find("button").prop("disabled", true)
            $("#barcode_select").find("button").prop("disabled", true)
        }
        //$(".background_violet").removeClass("background_violet")
        //$(".background_pink").removeClass("background_pink")
        $(el.currentTarget).parent().siblings().addBack().each(function (idx, el) {
            $(el).not(".manifest, .bold").toggleClass("selected_row")

        })
        $(el.currentTarget).parent().parent().find(".manifest").toggleClass("background_violet")
        $(el.currentTarget).parent().parent().find(".bold").toggleClass("background_pink")
    })

    $(document).on("click", "#accept_reject_button button", handle_accept_reject)
    $(document).on("click", "#force_submission", handle_force_submission)

    // handle clicks on both profiles (.selectable_row), and filter (.hot_tab)
    $(document).on("click", ".selectable_row, .hot_tab", row_select)

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

    if (filter == "conflicting_barcode") {
        $("#accept_reject_button").hide()
        $("#barcode_select").show()
        $("#edit_buttons").show()
        $("#sample_filter").removeClass("filter_margin")
        $("#force_submission").hide()
        $("#edit_buttons").hide()
    } else if (filter == "pending") {
        $("#accept_reject_button").show()
        $("#barcode_select").hide()
        $("#edit_buttons").show()
        $("#sample_filter").removeClass("filter_margin")
        $("#force_submission").hide()
    } else if (filter == "pending_barcode") {
        $("#accept_reject_button").hide()
        $("#barcode_select").hide()
        $("#edit_buttons").show()
        $("#force_submission").show()
        $("#sample_filter").removeClass("filter_margin")

    } else {
        $("#accept_reject_button").hide()
        $("#barcode_select").hide()
        $("#force_submission").hide()
        $("#edit_buttons").hide()
        $("#sample_filter").addClass("filter_margin")
    }


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

        if (filter == "conflicting_barcode") {
            if ($.fn.DataTable.isDataTable('#profile_samples')) {
                $("#profile_samples").DataTable().clear().destroy();
            }
            $("#sample_panel").find("thead").empty()
            $("#sample_panel").find("tbody").empty()
            var th = "<tr><th></th><th>Specimen ID</th><th>Manifest Species</th><th>Bold Species</th></tr>"
            var body = ""
            $(data).each(function (idx, el) {
                var manifest_tax = el.species_list
                var bold_tax = el.barcoding
                var td = $("<td/>", {
                    class: "tickbox"
                })
                var tickbox = $("<input/>",
                    {
                        "type": "checkbox",
                        class: "form-check-input"
                    })
                $(td).append(tickbox)

                body = body + "<tr data-id='" + el._id.$oid + "'><td>" + td.html() + "</td><td style='min-width: 200px;'>" + el.SPECIMEN_ID + "</td><td class='manifest' style='min-width: 200px;'>" + manifest_tax[0].SCIENTIFIC_NAME + "</td><td class='bold' style='min-width: 200px;'>" + bold_tax.taxonomy.species.taxon.name + "</td></tr>"
            })
            $("#sample_panel").find("thead").append(th)
            $("#sample_panel").find("tbody").append(body)
            $("#profile_samples").DataTable(dt_options);
        } else {
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
                        if (filter.startsWith("pending")) {

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
                        if (filter.startsWith("pending")) {

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
                $("#profile_samples").DataTable(dt_options);
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
            $("#profile_titles").find("tbody").append("<tr class='selectable_row'><td data-profile_id='" + data[d]._id.$oid + "'>" + data[d].title + "</td></tr>")
        })
        $($("#profile_titles tr")[1]).click()
    })
}


function handle_accept_reject(el) {
    $("#spinner").fadeIn(fadeSpeed)
    var checked = $(".form-check-input:checked").closest("tr")
    if (el.hasOwnProperty("currentTarget")) {
        var button = $(el.currentTarget)
    }

    var action
    var dd_reason
    var txt_box_other_reason
    if (button.hasClass("positive")) {
        action = "accept"
    } else if (button.hasClass("negative")) {
        action = "reject"
    } else if (button.hasClass("force")) {
        action = "accept"
        var dd_reason = $(document).data("dd_reason")
        var txt_box_other_reason = $(document).data("txt_box_other_reason")
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
        // create or update dtol submission record
        do_accept(sample_ids, dd_reason, txt_box_other_reason)
    }
}

function handle_force_submission() {


    BootstrapDialog.show({
        title: 'Reason for Forcing Submission',
        message: $("<div></div>").load('/copo/force_submission_dialog_content/'),
        buttons: [{
            id: 'force_btn',
            label: 'Accept',
            cssClass: 'ui green button force',
            action: function (dialog) {
                $(document).data("dd_reason", $('#dd_reason').find(":selected").val())
                $(document).data("txt_box_other_reason", $('#txt_box_other_reason').val())
                dialog.close()
            }
        }, {
            label: 'Close',
            cssClass: 'ui button',
            action: function (dialog) {
                dialog.close();
            }
        }],
    })
}

function do_accept(sample_ids, dd_reason, txt_box_other_reason) {
    var profile_id = $("#profile_id").val()
    $("#sub_spinner").fadeIn(fadeSpeed)
    $.ajax({
        url: "/copo/add_sample_to_dtol_submission/",
        method: "GET",
        data: {
            "sample_ids": JSON.stringify(sample_ids),
            "profile_id": profile_id,
            "dd_reason": dd_reason,
            "txt_box_other_reason": txt_box_other_reason
        },
    }).done(function () {
        $("#profile_titles").find(".selected").click()
        $("#spinner").fadeOut(fadeSpeed)
    })
}

}
