function handle_csv_button_click(table) {
    // produce content for column update modal
    $("#column_inspect_table thead").empty()
    $("#column_inspect_table tbody").empty()
    const headers = table.header()[0].innerHTML
    const body = table.body()[0].innerHTML
    $("#csv_update_modal").find("thead").append(headers)
    $("#csv_update_modal").find("tbody").append(body)
    $("#csv_update_modal").find("select").empty()
    $(headers).find("th").each(function (idx, el) {
        if (idx > 0 && el.innerHTML != "Source") {
            // don't add units as these will be automatically selected for spreadsheet compilation
            if (el.innerHTML != "Unit") {
                $("#csv_update_modal").find("select").append('<option data-order=" ' + idx + ' " value="' + el.innerHTML + '">' + el.innerHTML + '</option>')
            }
        }
    })
    $("#csv_update_modal .select-checkbox").remove()
    $("#column_inspect_table tr td:nth-child(1)").addClass("cell_highlight_in_column")
    $("#column_inspect_table tr th:nth-child(1)").addClass("cell_highlight_in_column")
    $("#csv_update_modal").modal()
}

$(document).on("change", "#column_dropdown", function (evt) {
    // highlight the selected column
    const selected_column_text = $(evt.currentTarget).find("option:selected").val()
    const column = $(evt.currentTarget).find("option:selected").data("order")
    $(".cell_highlight_in_column").removeClass("cell_highlight_in_column")
    if (selected_column_text.includes("Characteristics") || selected_column_text.includes("Factors")) {
        // if charateristics or factors column selected, also select the unit column to the right
        $("#column_inspect_table tr td:nth-child(" + column + ")").addClass("cell_highlight_in_column")
        $("#column_inspect_table tr td:nth-child(" + (parseInt(column) + 1) + ")").addClass("cell_highlight_in_column")
        $("#column_inspect_table tr th:nth-child(" + column + ")").addClass("cell_highlight_in_column")
        $("#column_inspect_table tr th:nth-child(" + (parseInt(column) + 1) + ")").addClass("cell_highlight_in_column")
    } else {
        $("#column_inspect_table tr td:nth-child(" + column + ")").addClass("cell_highlight_in_column")
        $("#column_inspect_table tr th:nth-child(" + column + ")").addClass("cell_highlight_in_column")
    }
})

$(document).on("click", "#ss_download_button", function (evt) {
    evt.preventDefault()
    const selected_column_text = $("#column_dropdown").find("option:selected").val()
    const rows = $("#column_inspect_table tbody tr")
    row_ids = []
    $(rows).each(function (idx, el) {
        const record_id = $(el).attr("id").split("_")[1]
        row_ids.push(record_id)
    })
    var csrftoken = $.cookie('csrftoken');
    $.ajax({
        url: '/copo/handle_csv_column_update_spreadsheet/',
        type: "POST",
        headers: {'X-CSRFToken': csrftoken},
        data: {
            'task': 'get',
            'records': JSON.stringify(row_ids),
            'column': selected_column_text
        }
    }).done(function (data) {
        let link = document.createElement('a');
        let blob = new Blob([data], {});
        blob = blob.slice(0, blob.size, "text/csv")
        link.download = selected_column_text + ".csv"
        link.href = URL.createObjectURL(blob);
        link.click();
        window.URL.revokeObjectURL(link.href);
    }).fail(function (error) {
        console.log(error)
    })
})

$(document).on("change", "#csv_upload_button", handle_csv_upload)
$(document).on("click", "#csv_reload", handle_csv_upload)

function handle_csv_upload(evt) {
    evt.preventDefault()
    var csrftoken = $.cookie('csrftoken');
    const files = document.getElementById("csv_upload_button").files[0];
    const column = $("#column_dropdown").val()
    const form = document.getElementById("csv_upload_form")
    const profile_id = $("#profile_id").val()
    const fd = new FormData(form)
    fd.append("file", files)
    fd.append("column", column)
    fd.append("update_type", "sample")
    fd.append("profile_id", profile_id)
    fd.append("task", "post")
    $.ajax({
        headers: {'X-CSRFToken': csrftoken},
        url: '/copo/handle_csv_column_update_spreadsheet/',
        type: 'POST',
        data: fd,
        processData: false,
        contentType: false,
        cache: false,
        dataType: "json"
    }).done(function (data) {
        for (idx in data) {
            const el = data[idx]
            // get row in question
            const row = $("#column_inspect_table [id$=" + el._id.$oid + "]")
            const selection = $(row).find(".cell_highlight_in_column")
            if (el["updated_field"] == "value") {

                $($(selection)[0]).html(el["updated_value"])
                $($(selection)[0]).addClass("cell_updated", 500)
            } else if (el["updated_field"] == "value_source") {
                $($(selection)[0]).addClass("cell_updated", 500)
            } else if (el["updated_field"] == "unit") {
                $($(selection)[1]).html(el["updated_value"])
                $($(selection)[1]).addClass("cell_updated", 500)

            } else if (el["updated_field"] == "unit_source") {
                $($(selection)[1]).addClass("cell_updated", 500)
            }
        }
        $("#csv_validate").removeClass("disabled")
    })
}

$(document).on("click", "#csv_validate", function (evt) {
    evt.preventDefault()
    $("#validate_loader").fadeIn()
    //get all cells marked as updated and send to backend for validation
    const updated_cells = $(".cell_updated")
    var send = []
    $(updated_cells).each(function (idx, cell) {
        //for each get the record id, header, cell value
        cell = $(cell)
        const cell_uid = "cell_" + idx
        // strore cell in document for later retrieval
        $(document).data(cell_uid, cell)
        var field = {}
        var header = cell.closest('table').find('th').eq(cell.index()).text()
        field.header = header
        field.uid = cell_uid
        field.value = $(cell).html()
        const tr = $(cell).parent()
        var id = $(tr).attr("id")
        id = id.split("_")[1]
        field.record_id = id
        field.column = $("#column_dropdown").find("option:selected").val()
        send.push(field)
    })
    var csrftoken = $.cookie('csrftoken');
    $.ajax({
        url: '/copo/handle_csv_column_validate_spreadsheet/',
        type: "POST",
        headers: {'X-CSRFToken': csrftoken},
        data: {
            'task': 'validate',
            'data': JSON.stringify(send)
        }
    }).done(function (data) {
        const d = JSON.parse(data)
        console.table(d)
        for (x in d) {
            const el = d[x]
            if (el.status == "accepted") {
                // this is probably a numeric change which should just be accepted
                const id = el.uid
                $(document).data(id).removeClass("cell_updated").addClass("cell_accepted")
            } else if (el.status == "tentative") {
                // this is probably an ontology change so user needs to double check
                const id = el.uid
                var cell = $($(document).data(id))
                cell.removeClass("cell_updated").addClass("cell_tentative")
                cell.html(el.label)
                cell.data("iri", el.iri)
                cell.data("ontology_prefix", el.ontology_prefix)
                cell.attr("title", el.description)
            } else if (el.status == "error") {
                const id = el.uid
                var cell = $($(document).data(id))
                cell.removeClass("cell_updated").addClass("error")
            }
        }
        $("#validate_loader").fadeOut()
        $("#csv_save").removeClass("disabled")
    })

    $(document).on("click", "#csv_save", function (evt) {
        evt.preventDefault()
        // collect cells needing to be updated
        const cells = $(".cell_accepted, .cell_tentative")
        send = []
        $(cells).each(function (idx, el) {
            field = {}
            var header = cell.closest('table').find('th').eq(cell.index()).text()
            field.value = $(cell).html()
            const tr = $(cell).parent()
            var id = $(tr).attr("id")
            id = id.split("_")[1]
            field.record_id = id
            field.column = $("#column_dropdown").find("option:selected").val()
            send.push(field)
        })
        $.ajax({
            url: '/copo/handle_csv_column_update_samples/',
            type: "POST",
            headers: {'X-CSRFToken': csrftoken},
            data: {
                'task': 'validate',
                'data': JSON.stringify(send)
            }
        })
    })

})
