$(document).ready(function () {
    // functions defined here are called from both copo_sample_accept_reject and copo_samples, all provide DTOL
    // functionality

    // add field names here which you don't want to appear in the supervisors table
    excluded_fields = ["_id", "profile_id", "biosample_id"]
    // populate profiles panel on left
    update_pending_samples_table()

    $(document).on("click", ".selectable_row", row_select)

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

function row_select(ev) {
    // get samples for profile clicked in the left hand panel and populate table on the right
    var row = $(ev.currentTarget)
    $(".selected").removeClass("selected")
    $(row).addClass("selected")
    var d = {"profile_id": $(row).find("td").data("sample_id")}
    $.ajax({
        url: "/copo/get_samples_for_profile",
        data: d,
        method: "GET",
        dataType: "json"
    }).error(function (data) {
        console.error("ERROR: " + data)
    }).done(function (data) {
        $("#sample_panel").find("thead").empty()
        $("#sample_panel").find("tbody").empty()
        if (data.length) {
            var header = $("<h4/>", {
                html: "Samples"
            })
            $("#sample_panel").find(".labelling").empty().append(header)



            $(data).each(function (idx, row) {
                var th_row = $("<tr/>")
                var td_row = $("<tr/>")
                if (idx == 0) {
                    // do header and row
                    var empty_th = $("<th/>")
                    $(th_row).append(empty_th)
                    var td = $("<td/>", {
                        class: "tickbox"
                    })
                    var tickbox = $("<input/>",
                        {
                            "type": "checkbox",
                            class: "form-check-input"
                        })
                    $(td).append(tickbox)
                    $(td_row).append(td)
                    for (el in row) {
                        if (!excluded_fields.includes(el)) {
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
                            $("#profile_samples").find("thead").append(th_row)
                            $("#profile_samples").find("tbody").append(td_row)
                        }
                    }
                } else {
                    var td = $("<td/>", {
                        class: "tickbox"
                    })
                    var tickbox = $("<input/>",
                        {
                            "type": "checkbox",
                            class: "form-check-input tickbox"
                        })
                    $(td).append(tickbox)
                    $(td_row).append(td)
                    for (el in row) {
                        if (!excluded_fields.includes(el)) {
                            // just do row
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
                    $("#profile_samples").find("tbody").append(td_row)
                }
            })
        } else {
            var no_data = $("<h4/>", {
                html: "No Samples Found"
            })
            $("#sample_panel").find(".labelling").empty().html(
                no_data
            )
        }
    })
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
            $("#profile_titles").find("tbody").append("<tr class='selectable_row'><td data-sample_id='" + data[d]._id.$oid + "'>" + data[d].title + "</td></tr>")
        })
    })
}


