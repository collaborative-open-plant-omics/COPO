$(document).ready(function () {
    // Trigger manifest wizard modal
    $(document).on("click", "#show_manifest_wzd_button", function (e) {
        $("#modal-wizard").modal("show");
        $("#manifestType").children()[1].click()
    });

    $(document).on("shown.bs.modal", "#modal-wizard", get_field_handler)

    $(document).on("change", "#manifestType", get_field_handler)

    // $(document).on("change", "#commonvalue", create_table)
    create_table()


})

function get_field_handler() {
    // Number of organisms/samples/rows step
    var select = "";
    for (let i = 1; i <= 100; i++) {
        select += "<option val=" + i + ">" + i + "</option>";
    }
    $("#numberOfSamples").html(select);

    // Hides the modal and clear the data within the modal
    // after the "ok" button is clicked in the popup dialog
    $(document).on("click", ".okbtn", function (e) {
        $('#manifestType').val([]);
        $('#numberOfSamples').val([1]);
        $('#commonfields').val([]);
        $("#modal-wizard").modal("hide");
    });

    // Get all DTOL fields from manifest schemas based on the manifest type
    const manifest_type = document.querySelector('#manifestType').value;

    $.ajax({
        type: "GET",
        url: "get_manifest_fields/",
        dataType: "json",
        data: {
            "manifest_type": manifest_type
        }
    }).done(function (data) {
        console.log(data)
        for (let i = 0; i <= data.length; i++) {
            const option = data[i];
            $('#commonfields').append('<option value="' + option + '">' + option + '</option>')
        }
    }).error(function (error) {
            console.log(error)
        }
    );

}

function create_table() {
    var tableID = document.getElementById("table");
    var table = document.createElement('table');
    table.style.width = '40%';
    table.setAttribute('border', '1');
    var tbdy = document.createElement('tbody');
    var tr = document.createElement('tr');
    tr.addClass("fa fa-minus-circle");
    // blStatus.innerHTML = '<i class="fa fa-minus-circle"></i>';
    // $('tr').css({'color':'blue'});

    $(document).on("change", "#commonfields", function (e) {
        const common_field = document.querySelector('#commonfields').value;
        // Add rows to a table
        const row = table.insertRow();
        let cell = row.insertCell();
        cell.innerHTML = common_field;
        cell = row.insertCell();
        var value_input = document.createElement('input');
        value_input.setAttribute('type', 'text');
        value_input.setAttribute('placeholder', "Enter common value")
        value_input.setAttribute('id', "commonvalueID")
        cell.appendChild(value_input);
    });


    table.appendChild(tr);
    tableID.appendChild(table)
}