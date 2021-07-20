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
    } else {
        $("#column_inspect_table tr td:nth-child(" + column + ")").addClass("cell_highlight_in_column")
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
