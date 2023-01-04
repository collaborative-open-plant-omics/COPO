$(document).ready(function () {
    $('#spinner_div').hide(); // Hide "Manifest is generating" spinner
    $(".dropdown-toggle").dropdown(); // Facilitate the display of the manifest template dropdown menu options
    $.fn.datepicker.noConflict(); // Does not conflict with other scripts that also have datepicker defined

    $(document).data("manifest_type", "")

    $(document).on("click", "#downloadBtn", generateManifestTemplate)

    $(document).on("click", "#resetBtn", resetManifestWizard)

    // Show info popup dialog when info icon is clicked
    $(document).on("click", "#info", function () {
        let manifest_type = $(document).data("manifest_type")
        const asg_and_dtol_sop_link = "https://github.com/darwintreeoflife/metadata"
        const erga_sop_link = "https://github.com/ERGA-consortium/ERGA-sample-manifest"
        const dtolenv_sop_link = ""
        const sop_link = manifest_type === "asg" || manifest_type === "dtol" ? asg_and_dtol_sop_link :
            manifest_type === "erga" ? erga_sop_link : manifest_type === "dtolenv" ? dtolenv_sop_link : ""

        let info_message = "<ul  style = " + "'padding-top: 15px; padding-left: 10px;padding-right: 10px;" + "'> <li>To input a common value, select a field name from the dropdown list</li> <li style = " + "'margin-top: 10px;" + "'>Inputted values <b>must</b> conform to the <a href=" + sop_link + ">Standard Operating Procedure (SOP)</a></li></ul>";

        bootbox.dialog({
            size: 'small',
            message: info_message,
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
                if (result) {
                    resetManifestWizard(); // Reset values in the wizard
                    $("#modal-placeholder").modal("hide");
                }
            }
        });
    });

    //$(document).on("change", "#manifestType", get_common_fields_handler);

    wizard_handler();
});

function wizard_handler() {
    $("#manifest-wizard").on('change.fu.wizard', function () {
        // console.log('change');
    }).on('changed.fu.wizard', function () {
        let currentStep = $('#manifest-wizard').wizard('selectedItem').step;
        let prevButton = $('.btn-prev')
        let resetButton = $('.btn-reset')
        let rightIcon = $('#rightIcon')

        // Reveal/show the next icon/previous button/reset button
        // from the final step of the wizard
        currentStep === 2 ? prevButton.show() : prevButton.hide();
        currentStep === 2 ? resetButton.hide() : resetButton.show();
        currentStep === 2 ? rightIcon.hide() : rightIcon.show();
    }).on('finished.fu.wizard', function (e) {
        // console.log('finished');
        $("#modal-placeholder").modal("hide");
        $('#spinner_div').show();
        generateManifestTemplate(e);
    }).on('stepclick.fu.wizard', function (e, data) {
        //  console.log('Step' + data.step + ' clicked');
    }).on('actionclicked.fu.wizard', function (e, data) {
        validateCommonValue(e, data);
    });
}

function resetManifestWizard() {
    let commonfieldsDropdownlistDivID = document.querySelector("#commonfieldsDropdownlistDiv");
    let commonFieldErrorMessageID = document.getElementById("commonFieldErrorMessageID");
    document.getElementById('numberOfSamples').value = 1; // Preload with default number of samples

    $("#formID .form-group").remove(); // Remove/clear all existing divs from the form
    $('.btn-prev').hide(); // Hide previous button

    // Remove error information if it is shown
    if (commonfieldsDropdownlistDivID.classList.contains('has-error')) {
        commonfieldsDropdownlistDivID.classList.remove('has-error')
        commonFieldErrorMessageID.innerHTML = ""
        commonFieldErrorMessageID.style.display = 'none';
    }

    get_common_fields_handler(); // Preload with the common fields dropdown list
}

function get_common_fields_handler() {
    // Get fields from the manifest schema based on the manifest type
    // const manifest_type = document.querySelector('#manifestType').value;
    let manifest_type = $(document).data("manifest_type")

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
        let colour_lst = []

        // Add a default value to the dropdown list
        commonfieldsList.empty();
        commonfieldsList.append('<option selected disabled hidden value=""' + '>' + 'Choose a common field' + '</option>')


        for (let i = 0; i < data.length; i++) {
            let [order_num, excel_column_letter, current_colour, fieldname] = data[i]
            option = fieldname;


            let field_option = $('<option/>', {
                style: "background-color: " + current_colour + "  !important;padding: 10px 5px",
                value: option
            });


            // Add a divider/separator between the groups of colours
            let [prev_order_num, prev_excel_column_letter, prev_colour, prev_fieldname] = data[i - 1] || ""

            if (prev_colour != null && current_colour != null) {
                if (prev_colour !== "" && current_colour !== "") {
                    if (prev_colour !== current_colour) {
                        commonfieldsList.append('<option disabled>────────────────────────────────────</option>')
                    }
                }
                // Place a divider before the group of fields that have no assigned colour
                if (prev_colour !== "" && !current_colour.includes('#') && option !== "") {
                    commonfieldsList.append('<option disabled>────────────────────────────────────</option>')
                }


            }

            // Populate the dropdown menu
            field_option.text(excel_column_letter + "\xa0\xa0\xa0\xa0\xa0\xa0" + option)
            if (option === "RACK_OR_PLATE_ID" || option === "TUBE_OR_WELL_ID") {
                // Value for the fields - "RACK_OR_PLATE_ID" || option == "TUBE_OR_WELL_ID"
                // should be scanned in using their barcodes not manually entered
                field_option.attr("disabled", "disabled")
                field_option.attr("title", "Value should be scanned in not manually entered")

                commonfieldsList.append(field_option)
            } else {
                commonfieldsList.append(field_option)
            }


        }
    }).fail(function (error) {
        console.log('Error:', error.message);

    });

}

function get_common_value_dropdown_list_handler(common_field, commonValueDiv) {
    // Get dropdown list fields from manifest schema based on the common field and/manifest type
    // const manifest_type = document.querySelector('#manifestType').value;
    let manifest_type = $(document).data("manifest_type")

    $.ajax({
        type: "GET",
        url: "get_common_value_dropdown_list/",
        dataType: "json",
        data: {
            "manifest_type": manifest_type,
            "common_field": common_field
        }
    }).done(function (data) {
        if (data['dropdownlist'] !== [] && data['dropdownlist'].length !== 0) {
            const value_input = document.createElement('select');
            value_input.setAttribute('id', "commonValueID");
            value_input.setAttribute('class', 'form-control');
            value_input.setAttribute('aria-describedby', "commonValueStatus");
            value_input.setAttribute('required', '')
            value_input.style.width = '200px';// Set width of the select tag field

            let option = [];

            $(value_input).empty();
            $(value_input).append('<option selected disabled hidden value=""' + '>' + 'Choose common value' + '</option>')

            for (let i = 0; i < data['dropdownlist'].length; i++) {
                option = data['dropdownlist'][i];
                $(value_input).append('<option value="' + option + '">' + option + '</option>');
            }
            commonValueDiv.appendChild(value_input);
        } else {
            // Create input tag
            const value_input = document.createElement('input');
            value_input.setAttribute('class', 'form-control');
            value_input.setAttribute('required', '');
            value_input.setAttribute('aria-describedby', "commonValueStatus");

            // Create date field
            if (data['date_fields'].includes(common_field)) {
                // Get date picker for common field that requires a date as its value
                // Date selected has to be before the current date i.e. a past date
                value_input.setAttribute('type', 'text');
                value_input.setAttribute('placeholder', "Select date");
                // Date is based on class instead of ID due to jQuery and FuelUX conflicts
                // and multiple instances of the datepicker function cannot have the same ID
                $(value_input).addClass('datepicker');

                commonValueDiv.appendChild(value_input);

                // The "hasDatepicker" class triggers the datepicker function so it has to be present
                // in the input field that requires a date. The following line ensures
                // that the "hasDatepicker" class is present in each date field after the date
                // field is added to the commonValueDiv
                $('input').filter('.datepicker').datepicker({
                    dateFormat: "yy-mm-dd",
                    maxDate: 0
                });
            } else if (common_field === "TIME_OF_COLLECTION") {
                // Create time field
                value_input.setAttribute('id', "commonValueID");
                value_input.setAttribute('type', 'time');
                value_input.setAttribute('min', "0:00")
                value_input.setAttribute('max', "24:00")
                value_input.setAttribute('placeholder', "Choose time");

                commonValueDiv.appendChild(value_input);
            } else if (data['integer_fields'].includes(common_field)) {
                // Create integer field
                value_input.setAttribute('id', "commonValueID");
                value_input.setAttribute('type', 'number');
                value_input.setAttribute('placeholder', "Enter integer");
                value_input.setAttribute('onkeypress', "return event.keyCode === 8 || event.charCode > 48 && event.charCode <= 57")
                value_input.setAttribute('min', '1')
                value_input.setAttribute('max', "10000")

                commonValueDiv.appendChild(value_input);

            } else {
                value_input.setAttribute('id', "commonValueID");
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

function disableSelectedOption(commonField) {
    // Disable the selected option in dropdownlist
    $("#commonfields option:contains(" + commonField + ")").attr("disabled", "disabled");
    // Revert to the default option after selected option has been disabled in the dropdown list
    $("select").prop("selectedIndex", 0)
}

function insertFormDiv(common_field) {
    const formDiv = document.getElementById("formDiv");
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
    error_message_field.style.display = 'none' // Hide error message textarea tag
    commonFieldDiv.appendChild(error_message_field);

    // Common field; Create common field label
    const commonFieldLabel = document.createElement('label');
    commonFieldLabel.innerHTML = common_field.value;
    commonFieldLabel.setAttribute('class', 'cfID control-label col-sm-6');
    commonFieldLabel.setAttribute('for', "commonValueID")
    commonFieldLabel.style.paddingRight = '20px'; // Add space between the value field and field name
    commonFieldLabel.style.marginLeft = '10px';
    commonFieldLabel.style.textAlign = "left"

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

    // Disable selected common field in the dropdown list
    disableSelectedOption(common_field.value);

    // Make the form scrollable once it contains at least 6 divs
    let divs_in_form = document.querySelectorAll('#formID .form-group');

    if (divs_in_form.length >= 6) {
        $(formDiv).css({'overflow': 'scroll'});
        $(formDiv).css({'height': '200px'});
        // Set distance between the delete icon and scroll once form div becomes scrollable
        $(formDiv).css({'margin-right': "20px"});
    }
}

// noinspection JSUnusedGlobalSymbols
function removeFormDiv(div) {
    const formDiv = document.getElementById("formDiv");
    let divs_in_form = document.querySelectorAll('#formID .form-group');

    // Get the common field name from the div within the form
    let common_field = $(div).closest('div .form-group').find('.cfID').text();

    // Enable the common field name that is disabled in the dropdown list by removing the disable attribute
    $("#commonfields option:contains(" + common_field + ")").removeAttr("disabled");
    $(div).closest('div').remove(); // Remove the div from the form

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
                let common_value = element.find('.commonValueDiv input').val() ?? element.find('.commonValueDiv select').val();

                // Display an error message if the common value is undefined, null or empty
                if (common_value == null || common_value === "") {
                    error_message_tag.css({'display': ''}) // Reveal hidden textarea tag to show the error message
                    element.addClass('has-error')
                    error_message_tag.val('Field cannot be empty!')
                } else {
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
                            "common_value": common_value,
                        }
                    }).done(function (data) {
                        if (data['response']) {
                            // Check if any of the common value has invalid data in any of the div within the form
                            // If errors exist, then, do nothing, remain on step 2 of the manifest wizard
                            // else, navigate to the next step which is step 3 of the manifest wizard
                            let divs_in_form_with_error_class = document.querySelectorAll('#formID .has-error')
                            let number_of_errors_in_form = divs_in_form_with_error_class.length
                            number_of_errors_in_form === 0 ? $('#manifest-wizard').wizard('selectedItem', {step: 2}) : e.preventDefault();
                        } else {
                            let validation_error_message = `Invalid value! Field must be ${data['error']}!`;
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

    if (data.step === 1 && data.direction === 'next') {
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
            // Each common field and inputted/selected common value is located within a div
            // and the div is located within a form
            validateFormDivData()
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
    // const manifest_type = document.querySelector('#manifestType').value;
    let manifest_type = $(document).data("manifest_type")
    const number_of_samples = document.getElementById("numberOfSamples").value;

    let csrftoken = $('[name="csrfmiddlewaretoken"]').val(); //.attr('value');
    let common_fields_list = []
    let common_values_list = []


    $("#formID .form-group").each(function () {
        let common_value;
        let element = $(this)
        let common_field = element.find('.cfID').text();

        // Get value from input tag or select tag
        // If the input tag is "undefined" or "null" then, the value originates from a select tag and vice versa

        if (typeof element.find('.commonValueDiv input').val() === 'undefined' || element.find('.commonValueDiv input').val() === null) {
            common_value = element.find('.commonValueDiv select').val();
        } else {
            // typeof element.find('.commonValueDiv select').val() === 'undefined' || element.find('.commonValueDiv select').val() === null)
            common_value = element.find('.commonValueDiv input').val();
        }

        //.append() cannot be used to add an item to a list/array in JavaScript so .push() is used instead
        common_fields_list.push(common_field);
        common_values_list.push(common_value);

    });

    xhr.open('POST', 'generate_manifest_template/');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            let link = document.createElement('a');
            let blob = new Blob([this.response], {});
            link.download = `${manifest_type.toUpperCase()}_MANIFEST_TEMPLATE.xlsx`
            link.href = URL.createObjectURL(blob);
            link.click();
            window.URL.revokeObjectURL(link.href);
            $('#spinner_div').hide();
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

// Trigger manifest wizard modal with desired manifest type
function showWizardBasedOnManifestType(manifest_type) {
    $(document).data("manifest_type", manifest_type)
    let manifest_wizard = $('#manifest-wizard')
    // let manifestTypeID = document.getElementById('manifestType')
    $("#modal-placeholder").modal("show");
    manifest_wizard.wizard();
    // Automatically navigate to step 1 when the modal is launched
    // since step 0 is about selecting the manifest which has been done indirectly
    manifest_wizard.wizard('selectedItem', {step: 1});
    $("#formID .form-group").remove(); // Remove/clear all existing divs from the form
    document.getElementById('numberOfSamples').value = 1; // Preload with default number of samples
    // $('.btn-prev').hide(); // Hide previous button
    get_common_fields_handler();// Preload with the common fields dropdown list
}