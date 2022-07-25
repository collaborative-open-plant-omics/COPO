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
        // Preload with default manifest type
        // $("#manifestType").children()[2].click();
        $('#manifestType').combobox('selectByIndex', '0');
        const manifest_type = $('#manifestType').combobox('selectedItem').value;
        console.log(manifest_type + ' loaded on modal launch');
    });

    $(document).on("shown.bs.modal", "#manifest-wizard", get_field_handler);

    $(document).on("change", "#manifestType", get_field_handler);

    wizard_handler();


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


        // showStep(1);
        // console.log(info["step"]);
        // $(document).on("click", "#prevBtn", function () {
        // });
        // $(document).on("click", "#prevBtn", function () {
        // });

        // $('#manifest-wizard > .step' + step).show();
        // $('#modal-form').find('input[type="number"]').val(1);
        // $('#modal-form').find('select[id="commonfields"]').val('---------');
        //          {#modal-content#}
        //          {#$(this).find('form').trigger('reset');#}
    });

    // $("#commonfields").combobox({
    //     selected: function (event, ui) {
    //         alert('Handler for combox .change() called.');
    //         // insert_table_row();
    //     }
    // });
});

//
function showStep(step) {
    $('#manifest-wizard').data('wizard-steps', step);
    $('#manifest-wizard > .wizard-steps').hide();
    $('#manifest-wizard > .wizard-steps .active[data-target=#modal-step' + step + ']').show();
}

function wizard_handler() {
    $("#manifest-wizard").on('change.fu.wizard', function (e, data) {
        console.log('change');
        toggleNextIconVisibility(data);
        // console.log(data.step);
        // var item = $('#manifest-wizard').wizard('selectedItem');
        // console.log(item.step);
        // if (data.step === 3 && data.direction === 'next') {
        //     // return e.preventDefault();
        // }
        // $("#commonfields").combobox({
        //     selected: function (event, ui) {
        //         alert('Handler for combox .change() called.');
        //         insert_table_row();
        //     }
        // });
    }).on('changed.fu.wizard', function (e, data) {
        // alert('hi 2')
        console.log('changed');
        toggleNextIconVisibility(data);
        // if (data.step === 2 && data.step - 1 === 1) {
        //     console.log($('#manifestType').combobox('selectedItem').value);
        //     alert('yay');
        // }


    }).on('finished.fu.wizard', function (e, data) {
        console.log('finished');
        $("#modal-placeholder").modal("hide");
        $(this).find('#manifest-wizard .modal-content').html('reset');

    }).on('stepclick.fu.wizard', function (e, data) {
        toggleNextIconVisibility(data)

        console.log('step' + data.step + ' clicked');
    }).on('actionclicked.fu.wizard', function (evt, data) {
        toggleNextIconVisibility(data);
    });
}

function get_field_handler() {
    // Get fields from manifest schema based on the manifest type
    const manifest_type = $('#manifestType').combobox('selectedItem').value;
    console.log(manifest_type);
    alert('inside field handler');

    $.ajax({
        type: "GET",
        url: "get_manifest_fields/",
        dataType: "json",
        data: {
            "manifest_type": manifest_type
        }
    }).done(function (data) {
        console.log(data);
        let option = [];
        // Add a default value to the dropdown menu
        $("#commonfields .dropdown-menu").empty();
        for (let i = 0; i < data.length; i++) {
            option = data[i];
            $('#commonfields .dropdown-menu').append('<li data-value="' + option + '">' +
                '<a href="#">' + option + '</a> </li>')
        }

    }).fail(function (error) {
            console.log(error);
        }
    ).always(function () {
        //do  something whether request is ok or fail
    });

}

function toggleNextIconVisibility(data) {
    if (data.step === 3 && data.direction !== 'next') {
        // Hide the "next" icon from the last step of the wizard
        document.getElementById('rightIcon').style.visibility = 'hidden';
    }
}

function removeOptionFromCommonFieldDropdownList(commonField) {
    const select = document.getElementById("commonfields");
    const options = document.getElementById("commonfields").options;
    console.log(options)
    for (let i = 0; i < options.length; i++) {
        if (options[i].value === commonField) {
            options.remove(i);
            i--; // Decrease options by 1 since options now have one less element
            select.selectedIndex = 0; // Reverts to default option after selected option has been
                                      // removed from the dropdown list


        }
    }
}

function deleteRow(row) {
    // Find the cell value of common field name 
    let common_field = $(row).closest('tr').find('.cfID').text();
    // Append the common field name to the dropdown list now that before the is removed
    $('#commonfields').append('<option value="' + common_field + '">' + common_field + '</option>');
    $(row).closest('tr').remove(); // Remove row
}

function insert_table_row() {
    const tableID = document.getElementById("table");
    const table = document.createElement('table');
    // Set class and style to the table tag
    table.style.width = '80%';
    // table.setAttribute('border', '1');
    table.setAttribute('margin-left', 'auto');
    table.setAttribute('margin-right', 'auto');

    const tr = document.createElement('tr');
    $('#commonfields').combobox({
        selected: function (event, ui) {
            alert('Handler for .change() called.');
            // $(document).on("change", "#commonfields", function () {
            const common_field = document.querySelector('#commonfields').value;
            // Insert a row into a table
            const row = table.insertRow();
            // Common field cell
            let common_field_cell = row.insertCell();
            common_field_cell.innerHTML = common_field;
            common_field_cell.setAttribute('class', 'cfID');

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
            deleteIcon.setAttribute('onclick', 'deleteRow(this)');
            deleteIcon.setAttribute('class', "fa fa-minus-circle");
            deleteIcon.setAttribute('title', "Remove from manifest");
            $(delete_icon_cell).css({'color': 'red'});
            delete_icon_cell.appendChild(deleteIcon);

            // Remove selected common field from the dropdown menu
            removeOptionFromCommonFieldDropdownList(common_field);
        }
    });

    table.appendChild(tr);
    tableID.appendChild(table)

}