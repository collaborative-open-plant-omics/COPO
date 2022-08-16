$(document).ready(function () {
    $('#rightIcon').show();
    $('#loading').hide();
    // Trigger manifest wizard modal
    $(document).on("click", "#show_manifest_wzd_button", function (e) {
        $("#modal-placeholder").modal("show");
        $('#manifest-wizard').wizard();
        $('#rightIcon').show(); // Show "right icon" after it was removed from last step
        // Automatically go to step 1 when the modal is launched
        $('#manifest-wizard').wizard('selectedItem', {step: 1});

        document.getElementById('numberOfSamples').value = '1'; // Preload with default number of samples
        $("#tableID tbody tr").remove(); // Remove all existing rows from the table
        $('#manifestType').combobox('selectByIndex', '0') // Preload with default manifest type

        get_common_fields_handler();// Preload with the common fields dropdown menu
    });

    $(document).on("click", "#downloadBtn", generateManifestTemplate)

    // Show info popup dialog when info icon is clicked
    $(document).on("click", "#info", function () {
        bootbox.dialog({
            message: "To add another common value, select another field name from the dropdown menu",
            buttons: {
                "success": {
                    "label": "OK",
                    "className": "btn-sm btn-primary okbtn"
                }
            }
        });
    });

    // Show popup dialog when close icon is clicked
    $(document).on("click", "#closeModalIcon", function () {
        bootbox.confirm({
            message: "Are you sure that you would like to close the dialog? All inputted values will be lost.",
            buttons: {
                confirm: {
                    label: '<i class="fa fa-check"></i> Yes, close dialog'
                },
                cancel: {
                    label: '<i class="fa fa-times"></i> Cancel'
                }
            },
            callback: function (result) {
                if (result)
                    $("#modal-placeholder").modal("hide");
            }
        });
    });

    $(document).on("hidden.bs.modal", "#manifest-wizard", function (e, info) {
    });

    $(document).on("change", "#manifestType", get_common_fields_handler);

    wizard_handler();
});


function wizard_handler() {
    $("#manifest-wizard").on('change.fu.wizard', function () {
        console.log('change');
    }).on('changed.fu.wizard', function () {
        let currentStep = $('#manifest-wizard').wizard('selectedItem').step;
        if (currentStep === 3) {
            $('#rightIcon').hide();
        } else {
            $('#rightIcon').show();
        }
    }).on('finished.fu.wizard', function (e) {
        console.log('finished');
        $("#modal-placeholder").modal("hide");
        generateManifestTemplate(e);
    }).on('stepclick.fu.wizard', function (e, data) {
        console.log('Step' + data.step + ' clicked');
    }).on('actionclicked.fu.wizard', function (e) {
        // e.preventDefault();
    });
    // // Navigate wizard
    // $('.btn-prev').on('click', function () {
    //     $('#manifest-wizard').wizard('previous');
    // });
    //
    // $('.btn-next').on('click', function () {
    //     $('#manifest-wizard').wizard('next');
    // });
}

function get_common_fields_handler() {
    // Get fields from manifest schema based on the manifest type
    const manifest_type = $('#manifestType').combobox('selectedItem').value;

    $.ajax({
        type: "GET",
        url: "get_manifest_fields/",
        dataType: "json",
        data: {
            "manifest_type": manifest_type
        }
    }).done(function (data) {
        let option = [];
        // Add a default value to the dropdown menu
        $("#commonfields").empty();
        $('#commonfields').append('<option selected disabled hidden value=""' + '>' + 'Choose a common field' + '</option>')
        for (let i = 0; i < data.length; i++) {
            option = data[i];
            $('#commonfields').append('<option value="' + option + '">' + option + '</option>')
        }

    }).fail(function (error) {
        console.log('Error:', error.message);

    });

}

function get_common_value_dropdown_list_handler(common_field_cell, common_field, value_input_cell) {
    // Get dropdown list fields from manifest schema based on the common field and/ manifest type
    const manifest_type = $('#manifestType').combobox('selectedItem').value;

    $.ajax({
        type: "GET",
        url: "get_common_value_dropdown_list/",
        dataType: "json",
        data: {
            "manifest_type": manifest_type,
            "common_field": common_field
        }
    }).done(function (data) {
        if (data !== [] && data.length !== 0) {
            common_field_cell.style.width = '150px'; // Add space between the value and field
            const value_input = document.createElement('select');
            value_input.setAttribute('id', "commonvalueID");
            value_input.setAttribute('class', 'form-control');
            let option = [];
            $(value_input).empty();
            $(value_input).append('<option selected disabled hidden value=""' + '>' + 'Choose common value' + '</option>')
            for (let i = 0; i < data.length; i++) {
                option = data[i];
                $(value_input).append('<option value="' + option + '">' + option + '</option>');
            }
            value_input_cell.appendChild(value_input);
        } else {
            common_field_cell.style.width = '250px'; // Add space between the value and field
            let date_fields = ["DATE_OF_COLLECTION", "DATE_OF_PRESERVATION", "ORIGINAL_COLLECTION_DATE"];
            //Get Input value
            const value_input = document.createElement('input');
            value_input.setAttribute('id', "commonvalueID");

            if (date_fields.includes(common_field)) {
                value_input.setAttribute('type', 'text');
                // Get date picker for for common field that requires a date as its value
                // Date selected has to be before the current date i.e. a past date
                value_input.setAttribute('placeholder', "Select date");
                // The datepicker function reverts to the "datepicker" defined by the jQueryUI
                // and does not use the one defined by fuelux
                $.fn.datepicker.noConflict();
                $(value_input).datepicker({dateFormat: "yy-mm-dd", maxDate: 0});
                value_input_cell.appendChild(value_input);
            } else if (common_field === "TIME_OF_COLLECTION") {
                value_input.setAttribute('type', 'time');
                value_input.setAttribute('min', "0:00")
                value_input.setAttribute('max', "24:00")
                value_input_cell.appendChild(value_input);
            } else {
                value_input.setAttribute('type', 'text');
                value_input.setAttribute('placeholder', "Enter common value");
                value_input_cell.appendChild(value_input);
            }
        }

    }).fail(function (error) {
        console.log('Error:', error.message);

    });


}

function removeOptionFromCommonFieldDropdownList(commonField) {
    const select = document.getElementById("commonfields");
    const options = document.getElementById("commonfields").options;
    for (let i = 0; i < options.length; i++) {
        if (options[i].value === commonField) {
            options.remove(i);
            i--; // Decrease options by 1 since options now have one less element
            select.selectedIndex = 0; // Reverts to default option after selected option has been
                                      // removed from the dropdown list


        }
    }
}

function insertTableRow(common_field) {
    const tableDiv = document.getElementById("tableDiv");
    const table = document.getElementById("tableID");

    table.style.margin = "auto"; // Centre the table
    $(table).addClass('hoverTable');

    // Insert a row into a table
    const row = table.insertRow();
    // Common field cell
    let common_field_cell = row.insertCell();
    common_field_cell.innerHTML = common_field.value;
    common_field_cell.setAttribute('class', 'cfID');
    // common_field_cell.style.width = '250px'; // Add space between the value and field

    // Input value cell
    let value_input_cell = row.insertCell();

    get_common_value_dropdown_list_handler(common_field_cell, common_field.value, value_input_cell)

    // Delete icon cell
    let delete_icon_cell = row.insertCell();
    const deleteIcon = document.createElement('i');
    deleteIcon.setAttribute('type', 'button');
    deleteIcon.setAttribute('onclick', 'removeTableRow(this)');
    deleteIcon.setAttribute('class', "fa fa-trash-o");
    deleteIcon.setAttribute('title', "Remove from manifest");
    deleteIcon.style.marginLeft = "10px"; // Create space between the icon and the input value cell
    $(delete_icon_cell).css({'color': 'red'});
    delete_icon_cell.appendChild(deleteIcon);

    // Remove selected common field from the dropdown menu
    removeOptionFromCommonFieldDropdownList(common_field.value);

    let number_of_rows = table.rows.length

    // Add a scroll to the <div></div> tag containing the table so that the table can be scrollable
    // once it has at least 10 rows within it
    if (number_of_rows >= 10) {
        $(tableDiv).css({'overflow': 'scroll'});
        $(tableDiv).css({'height': '100px'});
    }
}

function removeTableRow(row) {
    // Find the cell value of common field name
    let common_field = $(row).closest('tr').find('.cfID').text();
    // Append the common field name to the dropdown list now that before the is removed
    $('#commonfields').append('<option value="' + common_field + '">' + common_field + '</option>');
    $(row).closest('tr').remove(); // Remove row
}

function generateManifestTemplate(event) {
    // XMLHttpRequest() has to be used instead of Ajax when downloading files with JavaScript
    event.preventDefault()
    const xhr = new XMLHttpRequest();
    const manifest_type = $('#manifestType').combobox('selectedItem').value;
    const table = document.getElementById("tableID");
    const number_of_samples = document.getElementById("numberOfSamples").value;
    const number_of_common_fields = table.rows.length;

    let csrftoken = $('[name="csrfmiddlewaretoken"]').attr('value');
    let common_fields_list = []
    let common_values_list = []

    for (let i = 0; i < number_of_common_fields; i++) {
        let common_field = table.rows[i].cells[0].innerHTML;

        // Get value from input tag or select tag
        let common_value = table.rows[i].cells[1].innerHTML.includes('input') ? table.rows[i].cells[1].querySelector('input').value : table.rows[i].cells[1].querySelector('select').value;

        //.append() cannot be used to add an item to a list/array in JavaScript so .push() is used instead
        common_fields_list.push(common_field);
        common_values_list.push(common_value);
    }

    xhr.open('POST', 'generate_manifest_template/');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            let link = document.createElement('a');
            let blob = new Blob([this.response], {});
            link.download = "manifest_template.xlsx"
            link.href = URL.createObjectURL(blob);
            link.click();
            window.URL.revokeObjectURL(link.href);
        } else if (xhr.status !== 200) {
            console.log(`Error ${xhr.status}: ${xhr.statusText}`);
        }
    }
    xhr.setRequestHeader('X-CSRFToken', csrftoken)
    xhr.responseType = 'blob';
    xhr.send(JSON.stringify({
        "row_count": number_of_samples,
        "manifest_type": manifest_type,
        "common_fields_list": common_fields_list,
        "common_values_list": common_values_list
    }));
}

function showWizard(manifest_type) {
    $("#modal-placeholder").modal("show");
    $('#manifest-wizard').wizard();
    // Automatically navigate to step 2 when the modal is launched
    // since step 1 is about selecting the manifest which has been done indirectly
    $('#manifest-wizard').wizard('selectedItem', {step: 2});
    $("#tableID tbody tr").remove(); // Remove all existing rows from the table
    document.getElementById('numberOfSamples').value = '1'; // Preload with default number of samples
    $('.btn-prev').hide();
    switch (manifest_type) {
        case "asg":
            $('#manifestType').combobox('selectByIndex', '0'); // Preload with "ASG" manifest type
            break;
        case "dtol":
            $('#manifestType').combobox('selectByIndex', '1'); // Preload with "DTOL" manifest type
            break;
        case "erga":
            $('#manifestType').combobox('selectByIndex', '2'); // Preload with "ERGA" manifest type
            break;
        case "env":
            $('#manifestType').combobox('selectByIndex', '3'); // Preload with "ENV" manifest type
            break;

        default:
            $('#manifestType').combobox('selectByIndex', '0'); // Preload with "ASG" manifest type as default

            break;
    }

    get_common_fields_handler();// Preload with the common fields dropdown menu
}