$(document).ready(function () {
    // Trigger manifest wizard modal
    $(document).on("click", "#show_manifest_wzd_button", function (e) {
        $("#modal-placeholder").modal("show");
        $('#manifest-wizard').wizard();
        // Automatically goes to step 1 especially when the modal is relaunched
        // after the "finished" button is pressed
        $('#manifest-wizard').wizard('selectedItem', {step: 1});
        // Show "right icon" after it is removed from last step
        document.getElementById('rightIcon').style.visibility = 'visibility';


        $('#manifestType').combobox('selectByIndex', '0'); // Preload with default manifest type
        get_common_fields_handler();// Preload with the common fields dropdown menu
    });


    $(document).on("change", "#manifestType", get_common_fields_handler);
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


    $(document).on("hidden.bs.modal", "#manifest-wizard", function (e, info) {
        // {#$('#manifest-wizard').removeData('bs.modal');#}
        // $(this).remove();
        // $(this).html('');
        // alert('Modal has been reset');
        // $(this).find('#modal-form').trigger('reset');
        // $(this).find("#manifestType").html("")
        // $('#modal-form').find('#numberOfSamples').val(1);

        $(this).find('#manifest-wizard .modal-content').trigger('reset');
    });

    wizard_handler();
});

function wizard_handler() {
    $("#manifest-wizard").on('change.fu.wizard', function (e, data) {
        console.log('change');
        toggleNextIconVisibility();
    }).on('changed.fu.wizard', function (e, data) {
        console.log('changed');
        toggleNextIconVisibility();

    }).on('finished.fu.wizard', function (e, data) {
        console.log('finished');
        $("#modal-placeholder").modal("hide");
        $(this).find('#manifest-wizard .modal-content').html('reset');

    }).on('stepclick.fu.wizard', function (e, data) {
        toggleNextIconVisibility()

        console.log('step' + data.step + ' clicked');
    }).on('actionclicked.fu.wizard', function (evt, data) {
        toggleNextIconVisibility();

    });
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
        // $('#commonfields').append('<option selected disabled hidden value=""' + '>' + '----------' + '</option>')
        for (let i = 0; i < data.length; i++) {
            option = data[i];
            $('#commonfields').append('<option value="' + option + '">' + option + '</option>')
        }

    }).fail(function (error) {
            console.log(error);
        }
    ).always(function () {
        //do  something whether request is ok or fail
    });

}

function toggleNextIconVisibility(step) {
    let currentStep = $('#manifest-wizard').wizard('selectedItem').step;
    try {
        if (currentStep === 3) {
            // Hide the "next" icon from the last step of the wizard
            document.getElementById('rightIcon').style.visibility = 'hidden';
        }
    } catch (error) {
        console.log(error.message)
    }
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

function removeTableRow(row) {
    // Find the cell value of common field name 
    let common_field = $(row).closest('tr').find('.cfID').text();
    // Append the common field name to the dropdown list now that before the is removed
    $('#commonfields').append('<option value="' + common_field + '">' + common_field + '</option>');
    $(row).closest('tr').remove(); // Remove row
}

function insertTableRow(common_field) {
    const tableID = document.getElementById("table");
    const table = document.createElement('table');
    table.style.margin = "auto"; // Centre the table

    const tr = document.createElement('tr');

    // $(tableID).css({'height': '100px'});
    $('#tableID').addClass(' tr:nth-child(even)');

    // Insert a row into a table
    const row = table.insertRow();
    // Common field cell
    let common_field_cell = row.insertCell();
    common_field_cell.innerHTML = common_field.value;
    common_field_cell.setAttribute('class', 'cfID');
    common_field_cell.style.width = '250px'; // Add space between the value and field

    // Input value cell
    let value_input_cell = row.insertCell();
    const value_input = document.createElement('input');
    value_input.setAttribute('type', 'text');
    value_input.setAttribute('placeholder', "Enter common value");
    value_input.setAttribute('id', "commonvalueID");
    value_input_cell.appendChild(value_input);

    // Delete icon cell
    let delete_icon_cell = row.insertCell();
    const deleteIcon = document.createElement('i');
    deleteIcon.setAttribute('type', 'button');
    deleteIcon.setAttribute('onclick', 'removeTableRow(this)');
    deleteIcon.setAttribute('class', "fa fa-minus-circle");
    deleteIcon.setAttribute('title', "Remove from manifest");
    deleteIcon.style.marginLeft = "10px"; // Create space between the icon and the input cell
    $(delete_icon_cell).css({'color': 'red'});
    delete_icon_cell.appendChild(deleteIcon);

    // Remove selected common field from the dropdown menu
    removeOptionFromCommonFieldDropdownList(common_field.value);

    table.appendChild(tr);
    tableID.appendChild(table);

    // Number of rows is equivalent to the total number of open and closed tags divided by 2
    // since one of this "<tr></tr>" is equivalent to one row
    let number_of_rows = $("#table").find('tr').length / 2; //$("#table tr").length / 2;

    console.log('Number of rows in the table: ' + number_of_rows);
    // Add a scroll to the table once it has at least 5 rows in it
    if (number_of_rows >= 5) {
        console.log('Number of rows is more than or equal to 5');
        $(tableID).css({'overflow': 'scroll'});
        $(tableID).css({'height': '100px'});
    }


}