$(document).ready(function () {
    $.fn.datepicker.noConflict(); // Does not conflict with other scripts that also have datepicker defined

    // Trigger manifest wizard modal
    $(document).on("click", "#show_manifest_wzd_button", function () {
        let manifest_wizard = $('#manifest-wizard')
        $("#modal-placeholder").modal("show");
        manifest_wizard.wizard();
        $('#rightIcon').show(); // Show "right icon" after it was removed from last step
        // Automatically go to step 1 when the modal is launched
        manifest_wizard.wizard('selectedItem', {step: 1});

        document.getElementById('numberOfSamples').value = 1; // Preload with default number of samples
        $("#formID .form-group").remove(); // Remove/clear all existing divs from the form

        document.getElementById('manifestType').selectedIndex = 0; // Preload with default manifest type

        get_common_fields_handler(); // Preload with the common fields dropdown list
    });

    $(document).on("click", "#downloadBtn", generateManifestTemplate)

    // Show info popup dialog when info icon is clicked
    $(document).on("click", "#info", function () {
        bootbox.dialog({
            size: 'small',
            message: "To add another common value, select another field name from the dropdown list",
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
        // console.log('change');
    }).on('changed.fu.wizard', function () {
        let currentStep = $('#manifest-wizard').wizard('selectedItem').step;
        let rightIcon = $('#rightIcon')
        // Reveal/show the next icon from the final step of the wizard
        currentStep === 3 ? rightIcon.hide() : rightIcon.show();
    }).on('finished.fu.wizard', function (e) {
        // console.log('finished');
        $("#modal-placeholder").modal("hide");
        generateManifestTemplate(e);
    }).on('stepclick.fu.wizard', function (e, data) {
        //  console.log('Step' + data.step + ' clicked');
    }).on('actionclicked.fu.wizard', function (e, data) {
        validateCommonValue(e, data);
    });
}

function get_common_fields_handler() {
    // Get fields from the manifest schema based on the manifest type
    const manifest_type = document.querySelector('#manifestType').value;

    $.ajax({
        type: "GET",
        url: "get_manifest_fields/",
        dataType: "json",
        data: {
            "manifest_type": manifest_type
        }
    }).done(function (data) {
        let commonfieldsList = $("#commonfields")
        let option = [];
        // Add a default value to the dropdown list
        commonfieldsList.empty();
        commonfieldsList.append('<option selected disabled hidden value=""' + '>' + 'Choose a common field' + '</option>')
        for (let i = 0; i < data.length; i++) {
            option = data[i];
            commonfieldsList.append('<option value="' + option + '">' + option + '</option>')
        }

    }).fail(function (error) {
        console.log('Error:', error.message);

    });

}

function get_common_value_dropdown_list_handler(common_field, commonValueDiv) {
    // Get dropdown list fields from manifest schema based on the common field and/manifest type
    const manifest_type = document.querySelector('#manifestType').value;

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
            const value_input = document.createElement('select');
            value_input.setAttribute('id', "commonvalueID");
            value_input.setAttribute('class', 'form-control');
            value_input.setAttribute('aria-describedby', "commonValueStatus");
            value_input.setAttribute('required', '')
            value_input.style.width = '200px';// Set width of the select tag field

            let option = [];
            $(value_input).empty();
            $(value_input).append('<option selected disabled hidden value=""' + '>' + 'Choose common value' + '</option>')
            for (let i = 0; i < data.length; i++) {
                option = data[i];
                $(value_input).append('<option value="' + option + '">' + option + '</option>');
            }
            commonValueDiv.appendChild(value_input);
        } else {
            let date_fields = ["DATE_OF_COLLECTION", "DATE_OF_PRESERVATION", "ORIGINAL_COLLECTION_DATE"];
            // Create input tag
            const value_input = document.createElement('input');
            value_input.setAttribute('class', 'form-control');
            value_input.setAttribute('required', '');
            value_input.setAttribute('aria-describedby', "commonValueStatus");

            if (date_fields.includes(common_field)) {
                let datepicker = $(".datepicker")
                value_input.setAttribute('type', 'text');
                // Get date picker for common field that requires a date as its value
                // Date selected has to be before the current date i.e. a past date
                value_input.setAttribute('placeholder', "Select date");
                // Date is based on class instead of ID due to jQuery and FuelUX conflicts
                $(value_input).addClass('datepicker');


                // The datepicker function reverts to the "datepicker" defined by the jQueryUI
                // and does not use the one defined by FuelUX
                datepicker.datepicker({dateFormat: "yy-mm-dd", maxDate: 0});
                commonValueDiv.appendChild(value_input);
                // The "hasDatepicker" class triggers the datepicker function so it's removed
                // from a previous date field so that it can be displayed on following date fields
                datepicker.filter('.datepicker').removeClass('hasDatepicker').datepicker({
                    dateFormat: "yy-mm-dd",
                    maxDate: 0
                });
            } else if (common_field === "TIME_OF_COLLECTION") {
                value_input.setAttribute('id', "commonvalueID");
                value_input.setAttribute('type', 'time');
                value_input.setAttribute('min', "0:00")
                value_input.setAttribute('max', "24:00")
                value_input.setAttribute('placeholder', "Choose time");

                commonValueDiv.appendChild(value_input);
            } else {
                value_input.setAttribute('id', "commonvalueID");
                value_input.setAttribute('type', 'text');
                value_input.setAttribute('placeholder', "Enter common value");
                value_input.setAttribute('value', "");

                commonValueDiv.appendChild(value_input);
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

function insertFormDiv(common_field) {
    const formDiv = document.getElementById("formDiv");
    // $(formDiv).addClass('centerFormDiv');

    // Create a form tag
    const form = document.getElementById("formID");
    $(form).addClass('form-horizontal'); // form-horizontal form-inline


    // Create common field div
    const commonFieldDiv = document.createElement('div');
    commonFieldDiv.setAttribute('class', 'form-group has-feedback');
    commonFieldDiv.setAttribute('id', `${common_field.value}_div`);

    // Error message field cell
    const error_message_field = document.createElement('textarea');
    error_message_field.setAttribute('id', "errorMessageID");

    error_message_field.setAttribute('readonly', "");
    error_message_field.setAttribute('class', 'form-control');
    error_message_field.setAttribute('rows', '1');
    error_message_field.setAttribute('wrap', 'soft');
    error_message_field.innerHTML = "";
    error_message_field.style.overflowY = 'scroll';
    // error_message_field.style.height = '48px';
    error_message_field.style.width = '211px';
    // error_message_field.style.maxWidth = '270px';
    error_message_field.style.marginLeft = '243px';
    error_message_field.style.marginBottom = '10px';
    error_message_field.style.resize = 'none';
    error_message_field.style.display = 'none' // Hide textarea tag
    commonFieldDiv.appendChild(error_message_field);

    // Common field; Create common field label
    const commonFieldLabel = document.createElement('label');
    commonFieldLabel.innerHTML = common_field.value;
    commonFieldLabel.setAttribute('class', 'cfID control-label col-sm-6');
    commonFieldLabel.setAttribute('for', "commonValueID")
    commonFieldLabel.style.paddingRight = '20px'; // Add space between the value field and field name
    commonFieldLabel.style.marginLeft = '10px';

    // Truncate long field names
    commonFieldLabel.style.whiteSpace = 'nowrap';
    commonFieldLabel.style.textOverflow = 'ellipsis';
    commonFieldLabel.style.overflow = 'hidden';
    commonFieldLabel.style.maxWidth = '220px';
    commonFieldDiv.appendChild(commonFieldLabel);

    // Create common value div
    const commonValueDiv = document.createElement('div');
    commonValueDiv.setAttribute('class', 'col-sm-5 commonValueDiv');
    commonFieldDiv.appendChild(commonValueDiv);

    // Value field
    get_common_value_dropdown_list_handler(common_field.value, commonValueDiv)


    // Delete icon tag
    const deleteIcon = document.createElement('i');
    deleteIcon.setAttribute('type', 'button');
    deleteIcon.setAttribute('onclick', 'removeFormDiv(this)');
    deleteIcon.setAttribute('class', "fa fa-trash-o");
    deleteIcon.setAttribute('title', "Remove from manifest");
    deleteIcon.style.marginTop = "7px"; // Center icon
    $(deleteIcon).css({'color': 'red'});
    commonFieldDiv.appendChild(deleteIcon);

    // Append the form to the div
    $(form).append(commonFieldDiv);
    formDiv.appendChild(form);

    // Remove selected common field from the dropdown list
    removeOptionFromCommonFieldDropdownList(common_field.value);

    // Make the form scrollable once it contains at least 6 divs
    let divs_in_form = document.querySelectorAll('#formID .form-group');

    if (divs_in_form.length >= 6) {
        $(formDiv).css({'overflow': 'scroll'});
        $(formDiv).css({'height': '200px'});
        // Set distance between the delete icon and scroll once form div becomes scrollable
        $(formDiv).css({'margin-right': "20px"});
    }
}

function sortOptionsList(selectTagIDName) {
    let selectTagID = $(selectTagIDName);
    let selectedValue = selectTagID.val(); // Cache selected value, before sorting the list
    let options_list = selectTagID.find('option');
    options_list.sort(function (a, b) {
        return $(a).val() > $(b).val() ? 1 : -1;
    });
    selectTagID.html('').append(options_list);
    selectTagID.val(selectedValue); // Set cached selected value
}

// noinspection JSUnusedGlobalSymbols
function removeFormDiv(div) {
    const formDiv = document.getElementById("formDiv");
    let divs_in_form = document.querySelectorAll('#formID .form-group');

    // Get the common field name from the div within the form
    let common_field = $(div).closest('div .form-group').find('.cfID').text();

    // Append the common field name to the dropdown list now that it has be removed from the form
    $('#commonfields').append('<option value="' + common_field + '">' + common_field + '</option>');
    $(div).closest('div').remove(); // Remove div

    // Sort the options within the common fields' dropdownlist/select tag
    sortOptionsList('#commonfields');

    // Once the form is less than 6 rows, retain the initial height of the form/modal
    // by removing the css that were added to make the form tag div scrollable
    // when more than or equal to 6 rows were present in the form
    if (divs_in_form.length < 6) {
        $(formDiv).css({'overflow': ''});
        $(formDiv).css({'height': ''});
        $(formDiv).css({'margin-right': ""});
    }
}

function validateCommonValue(e, data) {
    function validateFormDivData() {
        $("#formID .form-group").each(function () {
                let element = $(this)
                let common_field = element.find('.cfID').text()
                let error_message_tag = element.find('#errorMessageID')

                // Common value is either a text enclosed within an input tag or a date enclosed within a select tag
                // let common_value = element.find('.commonValueDiv input') !== null ? element.find('.commonValueDiv input').val() : element.find('.commonValueDiv select').val();
                let common_value = element.find('.commonValueDiv input').val() ?? element.find('.commonValueDiv select').val();

                // Display an error message if the common value is undefined, null or empty
                if (common_value == null || common_value === "") {
                    error_message_tag.css({'display': ''}) // Reveal hidden textarea tag to show the error message
                    element.addClass('has-error')
                    error_message_tag.val('Field cannot be empty!')
                    console.log(`Common field: ${common_field}`);
                    console.log('Common value (null or empty): ', common_value)
                    console.log('Common value (null or empty) error message: ', element.find('#errorMessageID').val())

                } else {
                    console.log(`Common field: ${common_field}`);
                    console.log('Common value (has a value): ', common_value)
                    console.log('Common value (has a value) error message: ', element.find('#errorMessageID').val())

                    // Remove error information if it is shown
                    if (element.hasClass('has-error')) {
                        element.removeClass('has-error')
                        error_message_tag.val('')
                        error_message_tag.css({'display': 'none'})
                    }
                    // Use an ajax handler to validate the common value with regex expression
                    // now that the common value is neither undefined, null or empty i.e. it has a value
                    $.ajax({
                        type: "GET",
                        url: "validate_common_value/",
                        dataType: "json",
                        data: {
                            "common_field": common_field,
                            "common_value": common_value
                        }
                    }).done(function (data) {
                        console.log('Inside Ajax.....ajax data: ', data)
                        if (data['response']) {
                            console.log('Success ', data['response'])

                            // Check if any of the common value has invalid data in any of the div within the form
                            // If errors exist, then, do nothing, remain on step 2 of the manifest wizard
                            // else, navigate to the next step which is step 3 of the manifest wizard
                            let divs_in_form_with_error_class = document.querySelectorAll('#formID .has-error')
                            let number_of_errors_in_form = divs_in_form_with_error_class.length
                            number_of_errors_in_form === 0 ? $('#manifest-wizard').wizard('selectedItem', {step: 3}) : e.preventDefault();
                            console.log('Number of divs with errors: ', number_of_errors_in_form)
                        } else {
                            let validation_error_message = `Invalid value! Field must be ${data['error']}!`;
                            console.log('Invalid: ', data['error'])
                            error_message_tag.css({'display': ''}) // Reveal hidden textarea tag to show the error message
                            element.addClass('has-error')
                            error_message_tag.css({'height': '41px'})
                            // Increase the height of the error message textarea field if the
                            // error message is more than or equal to 50 characters
                            validation_error_message.length >= 50 ? error_message_tag.css({'height': '60px'}) : error_message_tag.css({'height': '0px'})
                            error_message_tag.val(validation_error_message)
                            error_message_tag.attr('title', validation_error_message)
                            e.preventDefault();
                        }

                    }).fail(function (error) {
                        console.log('Error:', error.message);

                    });


                }

            }
        );
    }

    if (data.step === 2 && data.direction === 'next') {
        console.log('Manifest wizard Step 2')
        e.preventDefault(); // Prevent navigating to the next step of the manifest wizard
        let divs_in_form = document.querySelectorAll('#formID .form-group');
        let commonFieldErrorMessageID = document.getElementById("commonFieldErrorMessageID");
        let commonfieldsDropdownlistDivID = document.querySelector("#commonfieldsDropdownlistDiv");
        let commonfieldsID = document.getElementById("commonfields");

        // Check if the value of the default/disabled common field is an empty string and
        // check if the number of divs within the form is non-existent i.e equal to zero
        if (commonfieldsID.value === "" && divs_in_form.length === 0) {
            commonfieldsDropdownlistDivID.classList.add('has-error');
            commonFieldErrorMessageID.innerHTML = "Choose a common field then, enter or select its value before proceeding!"
            commonFieldErrorMessageID.style.display = ''; // Reveal span tag with error message
        } else {
            // Remove error information if it is shown
            if (commonfieldsDropdownlistDivID.classList.contains('has-error')) {
                commonfieldsDropdownlistDivID.classList.remove('has-error')
                commonFieldErrorMessageID.innerHTML = ""
                commonFieldErrorMessageID.style.display = 'none';
            }
            // else {
            // Each common field and inputted/selected common value is located within a div
            //  and the div is located within a form
            validateFormDivData()

            // }
        }
    }
}

function generateManifestTemplate(event) {
    // User needs to be loggedin so that the CSRF cookie is set,
    // "{% csrf_token %}" has to be included within a form tag in the manifests.html webpage
    // so that X-CSRFToken is set and HTTPS 403 Forbidden does not occur
    // XMLHttpRequest() has to be used instead of Ajax when downloading files with JavaScript
    event.preventDefault()
    const xhr = new XMLHttpRequest();
    const manifest_type = document.querySelector('#manifestType').value;
    const number_of_samples = document.getElementById("numberOfSamples").value;

    let csrftoken = $('[name="csrfmiddlewaretoken"]').val(); //.attr('value');
    let common_fields_list = []
    let common_values_list = []


    $("#formID .form-group").each(function () {
        let element = $(this)
        let common_field = element.find('.cfID').text();

        // Get value from input tag or select tag
        let common_value = element.find('.commonValueDiv input') !== null ? element.find('.commonValueDiv input').val() : element.find('.commonValueDiv select').val();

        //.append() cannot be used to add an item to a list/array in JavaScript so .push() is used instead
        common_fields_list.push(common_field);
        common_values_list.push(common_value);

    });

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

function showWizardBasedOnManifestType(manifest_type) {
    let manifest_wizard = $('#manifest-wizard')
    let manifestTypeID = document.getElementById('manifestType')
    $("#modal-placeholder").modal("show");
    manifest_wizard.wizard();
    // Automatically navigate to step 2 when the modal is launched
    // since step 1 is about selecting the manifest which has been done indirectly
    manifest_wizard.wizard('selectedItem', {step: 2});
    $("#formID .form-group").remove(); // Remove/clear all existing divs from the form
    document.getElementById('numberOfSamples').value = 1; // Preload with default number of samples
    $('.btn-prev').hide(); // Hide previous button

    switch (manifest_type) {
        case "asg":
            manifestTypeID.selectedIndex = 0; // Preload with "ASG" manifest type
            break;
        case "dtol":
            manifestTypeID.selectedIndex = 1; // Preload with "DTOL" manifest type
            break;
        case "erga":
            manifestTypeID.selectedIndex = 2; // Preload with "ERGA" manifest type
            break;
        case "env":
            manifestTypeID.selectedIndex = 3; // Preload with "ENV" manifest type
            break;

        default:
            manifestTypeID.selectedIndex = 0;// Preload with "ASG" manifest type as default
            break;
    }

    get_common_fields_handler();// Preload with the common fields dropdown list
}