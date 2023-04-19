/**  * Contains functions for generating form html from JSON-based tags
 * for copo_profile_index web page
 */

let htmlForm = $('<div/>'); //global form div
let global_key_split = "___0___";

//map controls to rendering functions
const controlsMapping = {
    "text": "do_text_ctrl",
    "textarea": "do_textarea_ctrl",
    "select": "do_select_ctrl",
    "copo-multi-select2": "do_copo_multi_select2_ctrl"
};

let contactCOPODialogCount = 1;

//form controls
const dispatchFormControl = {
    do_text_ctrl: function (formElem, elemValue) {
        let txt;
        const ctrlsDiv = $('<div/>',
            {
                class: "ctrlDIV"
            });

        let metaDiv = $('<div/>');
        let readonly = false;

        if (formElem.readonly) {
            readonly = formElem.readonly;
        }

        if (formElem.control === 'email') {
            formElem.email = true;
        }

        if (formElem.disabled === "true") {
            txt = $('<input/>',
                {
                    type: "text",
                    class: "input-copo form-control copo-text-control",
                    id: formElem.id,
                    name: formElem.id,
                    readonly: readonly,
                    disabled: true
                });
        } else {
            txt = $('<input/>',
                {
                    type: "text",
                    class: "input-copo form-control copo-text-control",
                    id: formElem.id,
                    name: formElem.id,
                    readonly: readonly,
                });
        }


        //set validation markers
        const vM = set_validation_markers(formElem, txt);

        metaDiv.append(txt);


        // set control metadata
        if (formElem.hasOwnProperty("control_meta")) {
            const control_meta = formElem.control_meta;

            if (control_meta.hasOwnProperty("input_group_addon")) {
                //get addon label
                let input_group_addon_label = '';

                try {
                    input_group_addon_label = control_meta.input_group_addon_label;
                } catch (err) {

                }

                //redefine metaDiv
                metaDiv = $('<div/>',
                    {
                        class: "input-group"
                    });

                const inputGroupSpan = $('<span/>',
                    {
                        class: "input-group-addon",
                        html: input_group_addon_label
                    });

                if (control_meta.input_group_addon === "right") {
                    metaDiv.append(txt).append(inputGroupSpan);
                } else {
                    metaDiv.append(inputGroupSpan).append(txt);
                }
            }

        }

        ctrlsDiv.append(metaDiv);
        ctrlsDiv.append(vM.errorHelpDiv);

        const output = get_form_ctrl(ctrlsDiv.clone(), formElem, elemValue);
        return add_message_segment(output);
    },
    do_textarea_ctrl: function (formElem, elemValue) {

        const ctrlsDiv = $('<div/>',
            {
                class: "ctrlDIV"
            });

        const txt = $('<textarea/>',
            {
                class: "form-control copo-textarea-control",
                rows: 4,
                cols: 40,
                id: formElem.id,
                name: formElem.id
            });

        //set validation markers
        const vM = set_validation_markers(formElem, txt);

        ctrlsDiv.append(txt);
        ctrlsDiv.append(vM.errorHelpDiv);

        const output = get_form_ctrl(ctrlsDiv.clone(), formElem, elemValue);
        return add_message_segment(output);
    },
    do_select_ctrl: function (formElem, elemValue) {
        const ctrlsDiv = $('<div/>',
            {
                class: "ctrlDIV"
            });

        //build select
        const selectCtrl = $('<select/>',
            {
                class: "form-control input-copo copo-select-control",
                id: formElem.id,
                name: formElem.id
            });

        if (formElem.option_values) {
            for (let i = 0; i < formElem.option_values.length; ++i) {
                const option = formElem.option_values[i];
                let lbl = "";
                let vl = "";
                if (typeof option === "string") {
                    lbl = option;
                    vl = option;
                } else if (typeof option === "object") {
                    lbl = option.label;
                    vl = option.value;
                }
                if (vl === "required") {
                    $('<option disabled selected value>' + lbl + '</option>').appendTo(selectCtrl)
                } else {
                    $('<option value="' + vl + '">' + lbl + '</option>').appendTo(selectCtrl);
                }
            }
        }

        ctrlsDiv.append(selectCtrl);

        return get_form_ctrl(ctrlsDiv.clone(), formElem, elemValue);
    },
    do_copo_multi_select2_ctrl: function (formElem, elemValue) {
        formElem["type"] = "string"; //this, for the purposes of the UI, should be assigned a string temporarily, since multi_search takes care of the multiple values

        var ctrlsDiv = $('<div/>',
            {
                class: "ctrlDIV"
            });

        var placeholder = "Select " + formElem.label + "...";
        if (formElem.hasOwnProperty("placeholder")) {
            placeholder = formElem.placeholder;
        }

        //maximum selection
        var maximumSelectionLength = -1;
        if (formElem.data_maxItems) {
            maximumSelectionLength = formElem.data_maxItems;
        }

        //form options
        var optionsList = [];

        if (formElem.option_values && formElem.option_values.length) {
            optionsList = formElem.option_values.map(function (item) {
                if (typeof item === "string") {
                    var newItem = item;
                    item = {};
                    item.value = newItem;
                    item.label = newItem;
                }
                return {
                    id: item.accession || item.value,
                    text: item.label,
                    selected: true
                };
            });
        }

        //set current data
        var currentValue = [];

        if (elemValue) {
            if (typeof elemValue === "string") {
                currentValue = elemValue.split(",");
            } else if (typeof elemValue === "object") {
                currentValue = elemValue;
            }
        }

        //generate element controls
        var ctrl = $('<select/>',
            {
                class: "input-copo form-control copo-multi-select2",
                style: "width: 100%",
                "multiple": "multiple",
                id: formElem.id,
                name: formElem.id,
                "data-validate": true,
                "data-placeholder": placeholder,
                "data-maximumSelectionLength": maximumSelectionLength,
                "data-currentValue": JSON.stringify(currentValue),
                "data-optionsList": JSON.stringify(optionsList)
            });


        //set validation markers
        const vM = set_validation_markers(formElem, ctrl);

        ctrlsDiv.append(ctrl);
        ctrlsDiv.append(vM.errorHelpDiv);

        const returnDiv = get_form_ctrl(ctrlsDiv.clone(), formElem, elemValue);

        return add_message_segment(returnDiv);
    }
};

$(document).ready(function () {
    //handle event for form calls
    $(document).on("click", ".new-form-call", function (e) { //call to generate form
        e.preventDefault();

        let component = "";
        try {
            component = $(this).attr("data-component");
        } catch (err) {
            console.log(err);
        }

        if (component === 'annotation') {
            initiate_annotation_call();
        } else {
            initiate_profile_form_call(component);
        }
    });

    // Add an event listener/bind the close button of the 'COPO contact dialog'
    $('#contactCOPODialogBtnID').bind('click', function () {
        contactCOPODialogCount++;
    });

}); //end of document ready

function initiate_profile_form_call(component) {
    let copoFormsURL = "/copo/copo_profile_forms/";
    const csrftoken = $.cookie('csrftoken');
    const errorMsg = "Couldn't build " + component + " form!";
    let componentData = null;

    $.ajax({
        url: copoFormsURL,
        type: "POST",
        headers: {'X-CSRFToken': csrftoken},
        data: {
            'task': 'form',
            'component': component
        },
        success: function (data) {
            json2HtmlProfileForm(data);
            componentData = data;

        },
        error: function () {
            alert(errorMsg);
        }
    });
}

function contact_COPO_popup_dialog() {
    const message = "If you would like to make manifest submissions to an ASG, ERGA or DToL manifest group";
    let $content = '<div>';

    $content += '<div style="margin-bottom: 10px; padding-bottom: 15px; font-weight: bold">' + message + '</div>';
    $content += '<p style="margin-top:10px">Please contact <a style="text-decoration: underline;" href="mailto:EI.COPO@earlham.ac.uk">EI.COPO@earlham.ac.uk</a> in order to be added to the manifest group. We will grant you the permission to select the desired group, create a profile for the group and subsequently upload a manifest to the group.</p>';
    $content += '</div>';

    const dialog = new BootstrapDialog({
        type: BootstrapDialog.TYPE_WARNING,
        title: "Contact COPO via email",
        message: $content,
        closable: false,
        onshown: function (dialogRef) {
            contactCOPODialogCount++; // Increment the number of times the dialog is shown
        },
        onhide: function (dialogRef) {
        },
        buttons: [{
            id: 'contactCOPODialogBtnID',
            label: 'Okay',
            cssClass: 'btn-custom3',
            hotkey: 13,
            action: function (dialogRef) {
                dialogRef.close(); // Close the 'Contact COPO' dialog
            }
        }]
    });

    dialog.realize();
    dialog.getModalFooter().removeClass('modal-footer');
    dialog.getModalFooter().css({"padding": "15px", "text-align": "right"});

    // Show the 'Contact COPO dialog' once
    if (contactCOPODialogCount > 1) {
        contactCOPODialogCount++;
        return false;
    } else {
        dialog.open();
    }

} //end of contact_COPO_popup_dialog  **************

function remove_selectedProfileType_from_associatedProfileTypeList(profileTypeID) {
    document.getElementById(profileTypeID).addEventListener("change", function () {
        // Perform the following only if selected 'Profile Type' is not "Stand-alone"
        if (this.value !== "Stand-alone") {
            $('.row:nth-child(4) > .col-sm-12').show() // Show 'Associated Profile Type(s)' field
            // Retrieve the parentheses and the enclosed string from the selected profile type
            let selected_type;
            let multi_select_options = $('.copo-multi-select2')
            const pattern = /(([\s]+))/; // parentheses regex with string enclosed

            if (!pattern.test(this.value))
                selected_type = this.value // Get selected value if no parentheses exist
            else {
                let associated_type_abbreviation_without_parentheses;
                associated_type_abbreviation_without_parentheses = this.value.substring(this.value.indexOf('(') + 1, this.value.indexOf(')'));

                // Get abbreviated associated type enclosed in parentheses
                selected_type = `(${associated_type_abbreviation_without_parentheses})`
                // If empty parentheses are returned, set the acronym as
                // the full string excluding the empty parentheses
                selected_type = selected_type === '()' ? this.value.replace(/\(\s*\)/g, "") : selected_type
            }

            let associated_type_option = multi_select_options.find("option[value*='" + selected_type + "']")
            if (associated_type_option.length) {
                // Exclude the selected profile from the associated profile type dropdown menu options
                multi_select_options.select2({
                    templateResult: function (option) {

                        if (option.text.includes(selected_type)) {
                            return null;
                        }
                        return option.text;
                    }
                });
                // Reinitialise/update the multi-select options
                multi_select_options.trigger('change');

            }
        } else {
            $('.row:nth-child(4) > .col-sm-12').hide() // Hide 'Associated Profile Type(s)' field
        }
    });

}

function json2HtmlProfileForm(data) {

    //tidy up before closing the modal
    const doTidyClose = {
        closeIt: function (dialogRef) {
            refresh_profile_tool_tips();

            htmlForm.empty(); //clear form
            dialogRef.close();
        }
    };
    let dialog_title = get_profile_form_title(data)
    const dialog = new BootstrapDialog({
        type: BootstrapDialog.TYPE_PRIMARY,
        size: BootstrapDialog.SIZE_WIDE,
        title: function () {
            return $('<span>' + dialog_title + '</span>');
        },
        closable: false,
        animate: true,
        draggable: true,
        onhide: function (dialogRef) {
            refresh_profile_tool_tips();
        },
        onshown: function (dialogRef) {
            //prevent enter keypress from submitting form automatically
            $("form").keypress(function (e) {
                //Enter key
                if (e.which === 13) {
                    return false;
                }
            });

            // Add Profile form
            if (dialog_title.includes("Add Profile")) {
                // If a user is not added to a manifest group, display a message for the user to contact
                // COPO via email dialog in order to be added to the manifest group
                if (groups.length === 0) {
                    contact_COPO_popup_dialog();
                } else {
                    // In the 'Add Profile' dialog, remove selected profile type from 'associated_type' dropdown menu
                    // options if a user is added to a manifest group
                    remove_selectedProfileType_from_associatedProfileTypeList(data.form.form_schema[2].id)
                }
            }

            // Edit Profile form
            if (dialog_title.includes("Edit Profile")) {
                if (groups.length === 0) {
                    // If a user is not added to a manifest group,do nothing
                    // This is already handled by back-end functionality.
                } else {
                    // In the 'Edit Profile' dialog, remove selected profile profile from 'associated_type'
                    // dropdown menu options if a user is added to a manifest group
                    remove_selectedProfileType_from_associatedProfileTypeList(data.form.form_schema[2].id)
                }
            }

            //custom validators
            custom_validate(htmlForm.find("form"));

            refresh_form_aux_controls();

            //validate on submit event
            htmlForm.find("form").validator().on('submit', function (e) {
                if (e.isDefaultPrevented()) {
                    return false;
                } else {
                    e.preventDefault();
                    save_form(data.form, dialogRef);
                }
            });

            const event = jQuery.Event("postformload"); //individual compnents can trap and handle this event as they so wish
            $('body').trigger(event);

            if (!groups.includes("dtol_users")) {
                $('select option[value *= "(DTOL)"]').hide();
                $('select option[value *= "(ASG)"]').hide();
            }
            if (!groups.includes("erga_users")) {
                $('select option[value *= "(ERGA)"]').hide();
            }
            if (!groups.includes("dtolenv_users")) {
                $('select option[value *= "(DTOL_ENV)"]').hide();
            }
        },
        buttons: [
            {
                id: 'btnFormCancel',
                label: 'Cancel',
                cssClass: 'tiny ui basic button',
                action: function (dialogRef) {
                    doTidyClose["closeIt"](dialogRef);
                    // Close any other dialog that might have been opened
                    $.each(BootstrapDialog.dialogs, function (id, dialog) {
                        dialog.close();
                    });
                }
            },
            {
                id: 'btnFormSave',
                label: '<i class="copo-components-icons glyphicon glyphicon-save"></i> Save',
                cssClass: 'tiny ui basic primary button',
                action: function (dialogRef) {
                    validate_forms(htmlForm.find("form"));
                }
            }
        ]
    });

    const $dialogContent = $('<div/>');

    const form_help_div = set_up_form_help_div(data);
    const form_message_div = get_form_message(data);

    const form_body_div = set_up_form_body_div(data);

    $dialogContent.append(form_help_div).append(form_message_div).append(form_body_div);

    // If user is in a manifest group, hide 'Associated profile type(s)' field on "Add Profile" dialog launch
    // because "Stand-alone" is the default value for 'Profile Type'
    if (dialog_title.includes("Add Profile") && groups.length >= 1) {
        $dialogContent.find('.row:nth-child(4) > .col-sm-12').hide()
    }

    // If user is in a manifest group, hide 'Associated profile type(s)' field on "Edit Profile" dialog launch
    // if "Stand-alone" is the value shown for 'Profile Type'

    if (dialog_title.includes("Edit Profile") && groups.length >= 1 && data.form.form_schema[2].data === "Stand-alone") {
        $dialogContent.find('.row:nth-child(4) > .col-sm-12').hide()
    }

    dialog.realize();
    dialog.setMessage($dialogContent);
    dialog.open();
}

//end of json2HtmlProfileForm

function build_form_body(data) {
    const formJSON = data.form;
    const formValue = formJSON.form_value;

    //clean slate for form
    let formCtrl = htmlForm.find("form");
    if (formCtrl.length) {
        formCtrl.empty();
    } else {
        formCtrl = $('<form/>',
            {
                "data-toggle": "validator"
            });
    }

    //generate controls given component schema
    for (let i = 0; i < formJSON.form_schema.length; ++i) {

        const formElem = formJSON.form_schema[i];
        let control = formElem.control;

        let elemValue = null;

        if (formValue) {
            const elem = formElem.id.split(".").slice(-1)[0];
            if (formValue[elem]) {
                elemValue = formValue[elem];
            }
        } else {
            if (formElem.default_value) {
                elemValue = formElem.default_value;
            } else {
                elemValue = "";
            }
        }

        if (formElem.hidden === "true") {
            control = "hidden";
        }

        try {
            formCtrl.append(dispatchFormControl[controlsMapping[control.toLowerCase()]](formElem, elemValue));
        } catch (err) {
            console.log(err);
            formCtrl.append('<div class="form-group copo-form-group"><span class="text-danger">Form Control Error</span> (' + formElem.label + '): Cannot resolve form control!</div>');
        }
    }

    return htmlForm.append(formCtrl);

}

function get_form_message(data) {
    const messageRowDiv = $('<div/>',
        {
            class: "row"
        });

    const messageColDiv = $('<div/>',
        {
            class: "col-sm-12 col-md-12 col-lg-12 formMessageDiv"
        });

    messageRowDiv.append(messageColDiv);

    let message_text = null;
    let message_type = null;


    try {
        message_text = data.form.form_message.text;
        message_type = data.form.form_message.type;

    } catch (err) {
    }

    if (message_text && message_type) {
        let feedback = get_alert_control();
        let alertClass = "alert-" + message_type;

        feedback
            .removeClass("alert-success")
            .addClass(alertClass);

        feedback.find(".alert-message").html(message_text);
        messageColDiv.html(feedback);
    }

    return messageRowDiv;
}

function get_profile_form_title(data) {
    let formTitle = "";
    let formMode = "add";

    if (data.form.target_id) {
        formTitle = "Edit " + data.form.form_label;
        formMode = "edit";
    } else {
        formTitle = "Add " + data.form.form_label;
        formMode = "add";
    }

    return formTitle;
}

function set_up_help_ctrl(ctrlName) {

    // now set up switch button to support the tool tips
    $("[name='" + ctrlName + "']").bootstrapSwitch(
        {
            size: "mini",
            onColor: "primary",
            state: true
        });

    $('input[name="' + ctrlName + '"]').on('switchChange.bootstrapSwitch', function (event, state) {
        if ($(this).closest(".helpDivRow").siblings(".formDivRow").length) {
            toggle_display_help_tips(state, $(this).closest(".helpDivRow").siblings(".formDivRow").first());
        }
    });

}

function set_up_form_help_div(data) {
    const ctrlDiv = $('<div/>',
        {
            class: "row helpDivRow",
            style: "margin-bottom:20px;"
        });

    const cloneCol = $('<div/>',
        {
            class: "col-sm-7 col-md-7 col-lg-7"
        });

    return ctrlDiv.append(cloneCol);
}

function set_up_form_body_div(data) {
    let formBodyDiv = $('<div/>',
        {
            class: "row formDivRow"
        }).append($('<div/>',
        {
            class: "col-sm-12 col-md-12 col-lg-12"
        }).append(htmlForm));
    //build main form
    build_form_body(data);

    return formBodyDiv;
}

function refresh_form_aux_controls() {
    //refresh controls
    refresh_profile_tool_tips();

    //set up help tips
    set_up_help_ctrl("helptips-chk");

    //refresh form validator
    refresh_validator(htmlForm.find("form"));
}

function set_validation_markers(formElem, ctrl) {
    //validation markers

    const validationMarkers = {};
    let errorHelpDiv = "";


    //required marker
    if (formElem.hasOwnProperty("required") && (formElem.required.toString().toLowerCase() === "true")) {
        ctrl.attr("required", true);
        ctrl.attr("data-error", formElem.label + " required!");

        errorHelpDiv = $('<div></div>').attr({class: "help-block with-errors"});
    }

    //unique marker...
    if (formElem.hasOwnProperty("unique") && (formElem.unique.toString().toLowerCase() === "true")) {
        let uniqueArray = [];

        if (formElem.hasOwnProperty("unique_items")) {
            uniqueArray = formElem.unique_items;
        }

        uniqueArray = JSON.stringify(uniqueArray);

        ctrl.attr("data-unique", "unique");
        ctrl.attr("data-unique-array", uniqueArray);
        ctrl.attr('data-unique-error', "The " + formElem.label + " value already exists!");

        errorHelpDiv = $('<div></div>').attr({class: "help-block with-errors"});
    }


    //batch unique marker...allows unique test for siblings of the same kind on the form
    if (formElem.hasOwnProperty("batch") && (formElem.batch.toString().toLowerCase() === "true")) {
        ctrl.attr("data-batch", "batch");
        ctrl.attr("data-family-name", formElem.batchuniquename);
        ctrl.attr('data-batch-error', "The " + formElem.label + " value has already been assigned!");

        errorHelpDiv = $('<div></div>').attr({class: "help-block with-errors"});
    }

    //email marker...
    if (formElem.hasOwnProperty("email") && (formElem.email.toString().toLowerCase() === "true")) {
        ctrl.attr("data-email", "email");
        ctrl.attr('data-email-error', "Please enter a valid value for the " + formElem.label);

        errorHelpDiv = $('<div></div>').attr({class: "help-block with-errors"});
    }

    //phone marker...
    if (formElem.hasOwnProperty("phone") && (formElem.phone.toString().toLowerCase() === "true")) {
        ctrl.attr("data-phone", "phone");
        ctrl.attr('data-phone-error', "Please enter a valid value for the " + formElem.label);

        errorHelpDiv = $('<div></div>').attr({class: "help-block with-errors"});
    }

    //resolver marker...
    if (formElem.hasOwnProperty("igroup") && (formElem.igroup.toString().toLowerCase() === "true")) {
        ctrl.attr("data-igroup", "igroup");
        ctrl.attr('data-igroup-error', "Please click " + formElem.button_label);

        errorHelpDiv = $('<div></div>').attr({class: "help-block with-errors"});
    }

    //characteristic marker
    if (formElem.hasOwnProperty("characteristics") && (formElem.characteristics.toString().toLowerCase() === "true")) {
        ctrl.attr("data-characteristics", "characteristics");
        ctrl.attr('data-characteristics-error', "Value/Unit error!");

        errorHelpDiv = $('<div></div>').attr({class: "help-block with-errors"});
    }

    //validate_ontology marker
    if (formElem.hasOwnProperty("validate_ontology") && (formElem.validate_ontology.toString().toLowerCase() === "true")) {
        ctrl.attr("data-ontology", "ontology");
        ctrl.attr('data-ontology-error', "Please enter a valid ontology.");

        errorHelpDiv = $('<div></div>').attr({class: "help-block with-errors"});
    }

    //ontologyrequired marker
    // if (formElem.hasOwnProperty("control") && (formElem.control.toString().toLowerCase() == "ontology term") &&
    //     formElem.hasOwnProperty("required") && (formElem.required.toString().toLowerCase() == "true")) {
    //     ctrl.attr("data-otr", "otr");
    //     ctrl.attr('data-otr-error', "Please enter a value for the " + formElem.label);
    //
    //     errorHelpDiv = $('<div></div>').attr({class: "help-block with-errors"});
    // }


    validationMarkers['errorHelpDiv'] = errorHelpDiv;
    validationMarkers['ctrl'] = ctrl;

    return validationMarkers;
}

function form_help_ctrl(tip) {
    if (tip) {
        return $('<span/>',
            {
                html: tip,
                class: "form-input-help",
                style: "display:none;"
            });
    } else {
        return '';
    }
}

function form_div_ctrl() {
    return $('<div/>',
        {
            style: "padding-bottom:5px; outline: 0;",
            class: "form-group copo-form-group",
            tabindex: -1
        });
}

function form_label_ctrl(formElem) {
    let lbl = formElem.label;
    const target = formElem.id;
    let lblCtrl = '';

    if (formElem.hasOwnProperty("required") && (formElem.required.toString().toLowerCase() === "true")) {
        lbl = lbl + "<span class='constraint-label required-label'> required</span>";
    } else if (formElem.hasOwnProperty("field_constraint") && (formElem.field_constraint.trim().toLowerCase() !== "")) {
        const dclass = "constraint-label " + formElem.field_constraint.trim().toLowerCase() + "-label";
        const dval = formElem.field_constraint.trim().toLowerCase();
        lbl = lbl + "<span class='" + dclass + "'>" + dval + "</span>";
    }

    if (lbl) {
        lblCtrl = $('<label/>',
            {
                html: lbl,
                for: target,
                class: "control-label"
            });


        var helpTip = '';
        if (formElem.hasOwnProperty('help_tip') && formElem.hasOwnProperty('help_tip') !== '') {
            helpTip = formElem["help_tip"];
        }

        if (helpTip) {
            const item = $('<i/>',
                {
                    style: "margin-left: 5px;",
                    class: "ui grey icon info circle copo-tooltip",
                    "data-html": helpTip
                });
            lblCtrl.append(item);
        }
    }
    return lblCtrl
}

function get_element_clone(ctrlsDiv, counter) {
    const ctrlClone = ctrlsDiv.clone();

    ctrlClone.find(':input').each(function () {
        if (this.id) {
            var elemID = this.id;
            $(this).attr("id", elemID + global_key_split + counter);
            $(this).attr("name", elemID + global_key_split + counter);
        }
    });


    const row = $('<div/>', {
        class: "row control-row"
    });

    const left = $('<div/>', {
        class: "col-sm-9"
    });

    const right = $('<div/>', {
        class: "col-sm-3",
        style: "padding-left: 5px;"
    });

    row
        .append(left)
        .append(right);

    const delBtn = get_del_button();

    delBtn.click(function (event) {
        event.preventDefault();
        row.remove();
    });

    const addBtn = get_add_button();

    addBtn.click(function (event) {
        event.preventDefault();
        ++counter;

        get_element_clone(ctrlsDiv, counter).insertAfter(row);

        //refresh controls
        refresh_profile_tool_tips();
    });


    left.append(ctrlClone);
    right.append(addBtn);
    right.append(delBtn);

    return row
}

function resolve_ctrl_values(ctrlsDiv, counter, formElem, elemValue) {
    const ctrlsWithValuesDiv = ctrlsDiv.clone();
    let ctrlsWithValuesDivArray = '';

    //validate elemValue
    if (Object.prototype.toString.call(elemValue) === '[object Object]') {
        if ($.isEmptyObject(elemValue)) {
            elemValue = "";
        }
    }

    if (elemValue) {
        if (formElem.type === "array") {
            if (elemValue.length > 0) {

                //first element should not be open to deletion
                ctrlsWithValuesDiv.find(":input").each(function () {
                    if (this.id) {
                        let sendOfValue = elemValue;
                        if (Object.prototype.toString.call(elemValue) === '[object Array]') {
                            sendOfValue = elemValue[0];
                        }

                        const resolvedValue = resolve_ctrl_values_aux_1(this.id, formElem, sendOfValue);
                        $(this).val(resolvedValue);
                        this.setAttribute("value", resolvedValue);
                    }
                });

                //sort other elements of the elemValue array
                if (Object.prototype.toString.call(elemValue) === '[object Array]' && elemValue.length > 1) {
                    ctrlsWithValuesDivArray = $('<div/>');

                    for (let i = 1; i < elemValue.length; ++i) {
                        ++counter;

                        const ctrlsWithValuesDivSiblings = get_element_clone(ctrlsDiv.clone(), counter);
                        ctrlsWithValuesDivSiblings.find(":input").each(function () {
                            if (this.id) {

                                var tId = this.id.substring(0, this.id.lastIndexOf(global_key_split)); //strip off subscript

                                var resolvedValue = resolve_ctrl_values_aux_1(tId, formElem, elemValue[i]);
                                $(this).val(resolvedValue);
                                this.setAttribute("value", resolvedValue);
                            }
                        });

                        ctrlsWithValuesDivArray.append(ctrlsWithValuesDivSiblings);
                    }
                }
            }

        } else {//not array type elemValue
            ctrlsWithValuesDiv.find(":input").each(function () {
                if (this.id) {
                    let sendOfValue = elemValue;

                    if (Object.prototype.toString.call(elemValue) === '[object Array]') {
                        sendOfValue = elemValue.join();
                    }

                    const resolvedValue = resolve_ctrl_values_aux_1(this.id, formElem, sendOfValue);
                    $(this).val(resolvedValue);
                    this.setAttribute("value", resolvedValue);

                    if ($(this).prop("tagName") === "SELECT") {//this was what worked, as .val() failed to dance
                        for (var i = 0; i < this.length; ++i) {
                            if (this.options[i].value === resolvedValue) {
                                this.options[i].setAttribute("selected", "selected");
                                break;
                            }
                        }
                    }

                }
            });
        }
    }

    const ctrlObjects = {};
    ctrlObjects['counter'] = counter;
    ctrlObjects['ctrlsWithValuesDivArray'] = ctrlsWithValuesDivArray;
    ctrlObjects['ctrlsWithValuesDiv'] = ctrlsWithValuesDiv;

    return ctrlObjects;
}

function resolve_ctrl_values_aux_1(ctrlObjectID, formElem, elemValue) {
    var embedValue = null;

    if (ctrlObjectID.length === formElem.id.length) { //likely end-point element
        embedValue = elemValue;
    } else if (ctrlObjectID.length > formElem.id.length) { //likely a composite element
        var elemKeys = ctrlObjectID.split(formElem.id + ".").slice(-1)[0].split(".");

        embedValue = elemValue;
        for (var i = 0; i < elemKeys.length; ++i) {
            embedValue = embedValue[elemKeys[i]];
        }
    }

    return embedValue;
}

function add_message_segment(outputCtrl) {
    var row = $('<div/>', {
        class: "row rendered-control"
    });

    var left = $('<div/>', {
        class: "col-sm-12 control-segment"
    });

    left.append(outputCtrl);

    var right = $('<div/>', {
        class: "col-sm-4 message-segment"
    });

    row
        .append(left)
    // .append(right);

    return row;
}

function get_form_ctrl(ctrlsDiv, formElem, elemValue) {
    //control clone parameters...
    var counter = 0;

    //resolve control values
    var ctrlObjects = resolve_ctrl_values(ctrlsDiv.clone(), counter, formElem, elemValue);

    var firstElement = ctrlObjects.ctrlsWithValuesDiv;
    if (formElem.type === "array") {
        firstElement = $('<div/>', {
            class: "row control-row"
        });

        var left = $('<div/>', {
            class: "col-sm-9"
        });

        var right = $('<div/>', {
            class: "col-sm-3",
            style: "padding-left: 5px;"
        });

        firstElement
            .append(left)
            .append(right);

        var addBtn = get_add_button();

        left.append(ctrlObjects.ctrlsWithValuesDiv);
        right.append(addBtn);

        addBtn.click(function (event) {
            event.preventDefault();
            ++counter;

            get_element_clone(ctrlsDiv, counter).insertAfter(firstElement);

            //refresh controls
            refresh_profile_tool_tips();
        });
    }

    return form_div_ctrl()
        .append(form_label_ctrl(formElem))
        .append(firstElement)
        .append(ctrlObjects.ctrlsWithValuesDivArray)
        .append(form_help_ctrl(formElem.help_tip));
}

function validate_forms(formObject) {
    formObject.trigger('submit');
}

function custom_validate(formObject) {
    formObject.validator({
        custom: {
            unique: function ($el) {//validates for unique fields
                //get array of items for test
                //items in array must be of type String for the unique validation to work!!
                const uniqueArray = JSON.parse($el.attr("data-unique-array"));
                const newValue = $el.val().trim().toLowerCase();

                let oKFlag = true;

                $.each(uniqueArray, function (index, item) {
                    if (Object.prototype.toString.call(item) === '[object String]') {
                        if (newValue === item.trim().toLowerCase()) {
                            oKFlag = false;
                            return false;
                        }
                    }
                });

                if (!oKFlag) {
                    return "Not valid!";
                }
            },
            batch: function ($el) {
                //validates for batch unique fields, where the test focuses on siblings of the target element
                //having a common family name

                const uniqueArray = [];

                //get family name
                const familyName = $el.attr("data-family-name");

                //get siblings...with same family name
                $el.closest("form").find("[data-family-name='" + familyName + "']").each(function () {
                    if (this.id !== $el.attr("id")) {
                        uniqueArray.push($(this).val().trim().toLowerCase());
                    }
                });

                const newValue = $el.val().trim().toLowerCase();

                let oKFlag = true;

                if (newValue !== "") {
                    $.each(uniqueArray, function (index, item) {
                        if (Object.prototype.toString.call(item) === '[object String]') {
                            if (newValue === item) {
                                oKFlag = false;
                                return false;
                            }
                        }
                    });
                }

                if (!oKFlag) {
                    return "Not valid!";
                }
            },
            igroup: function ($el) {
                //validates for copo-input-group control

                const hiddenSibling = $("#" + $el.attr("id") + "_hidden");
                const newValue = hiddenSibling.val().trim();

                let oKFlag = true;

                if (newValue === "") {
                    oKFlag = false;
                }

                if (!oKFlag) {
                    return "Not valid!";
                }
            },
            phone: function ($el) {//validates for phone fields
                const re = /^\+?(0|[1-9]\d*)$/;
                const newValue = $el.val().trim();

                const oKFlag = re.test(newValue);

                if (!oKFlag) {
                    return "Not valid!";
                }
            },
            email: function ($el) {//validates for email fields
                const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
                const newValue = $el.val().trim();

                const oKFlag = re.test(newValue);

                if (!oKFlag) {
                    return "Not valid!";
                }
            },
            otr: function ($el) {//validates for ontology fields required
                const validationSource = $el;

                let oKFlag = true;


                validationSource.closest(".ontology-parent").find(".ontology-field-hidden").each(function () {
                    const dataKey = $(this).attr("data-key");

                    if ((dataKey === 'annotationValue' && !$(this).val().trim())) {
                        oKFlag = false;
                    }

                });

                oKFlag = false;


                if (!oKFlag) {
                    return "Not valid!";
                }
            },
            ontology: function ($el) {//validates for ontology fields requiring accessions
                var validationSource = $el;
                var oKFlag = true;

                validationSource.closest(".ontology-parent").find(".ontology-field-hidden").each(function () {
                    var dataKey = $(this).attr("data-key");

                    if ((dataKey === 'termSource' && !$(this).val().trim()) || (dataKey === 'termAccession' && !$(this).val().trim())) {
                        oKFlag = false;
                    }

                });

                if (!oKFlag) {
                    return "Not valid!";
                }
            },
            characteristics: function ($el) {
                //validates for copo-characteristics specific case: using value to validate unit
                const validationSource = $el;

                let oKFlag = true;

                const dataKey = 'annotationValue';
                const elements = validationSource.closest(".ctrlDIV").find(".ontology-parent").find("[data-key='" + dataKey + "']");

                const valueElem = {'unit': '', 'value': ''};

                elements.each(function (indx, item) {
                    if (valueElem.hasOwnProperty(item.getAttribute('data-parent1'))) {
                        valueElem[item.getAttribute('data-parent1')] = $(item).val().trim();
                    }
                });

                let errorMessage = '';

                if (valueElem.value !== '') {
                    //case: numeric value, no unit
                    if ($.isNumeric(valueElem.value) && valueElem.unit === '') {
                        errorMessage = 'Numeric value "' + valueElem.value + '" requires a unit!';
                        oKFlag = false;
                    }
                } else {
                    //case: unit specified for no value
                    if (valueElem.unit !== '') {
                        errorMessage = 'Value required for unit "' + valueElem.unit + '"!';
                        oKFlag = false;
                    }
                }

                if (errorMessage) {
                    alert(errorMessage);
                } else {
                    //clear error flags

                    const valTarget = validationSource.closest(".ctrlDIV").find(".ontology-parent").find(".copo-validation-target");
                    const valSource = validationSource.closest(".ctrlDIV").find(".ontology-parent").find(".copo-validation-source");

                    valTarget.removeAttr("data-error");
                    valTarget.removeAttr("required");
                    valTarget.removeClass("has-error");
                    valTarget.closest(".form-group").removeClass("has-error has-danger");
                    valTarget.closest(".form-group").find(".with-errors").remove();

                    valSource.removeAttr("data-error");
                    valSource.removeAttr("required");
                    valSource.removeClass("has-error");
                    valSource.closest(".form-group").removeClass("has-error has-danger");
                    valSource.closest(".form-group").find(".with-errors").remove();
                }

                if (!oKFlag) {
                    return "Not valid!";
                }
            }
        }
    });
}

function save_form(formJSON, dialogRef) {
    let globalDataBuffer = {};
    let copoFormsURL = "/copo/copo_profile_forms/";
    let task = "save";
    let error_msg = "Couldn't add " + formJSON.form_label + "!";
    if (formJSON.target_id) {
        task = "edit";
        error_msg = "Couldn't edit " + formJSON.form_label + "!";
    }

    //manage auto-generated fields
    const form_values = Object();
    htmlForm.find("form").find(":input").each(function () {
        form_values[this.id] = $(this).val();
    });

    const auto_fields = JSON.stringify(form_values);

    //get the visualisation context (i.e., what to be displayed after form save) and pass on
    let visualize = "";
    if (formJSON.visualize) {
        visualize = formJSON.visualize;
    }

    csrftoken = $.cookie('csrftoken');

    const btnSave = dialogRef.getButton('btnFormSave');
    const btnCancel = dialogRef.getButton('btnFormCancel');
    btnSave.disable();
    btnCancel.disable();
    btnSave.spin();


    $.ajax({
        url: copoFormsURL,
        type: "POST",
        headers: {'X-CSRFToken': csrftoken},
        data: {
            'task': task,
            'auto_fields': auto_fields,
            'component': formJSON.component_name,
            'visualize': visualize,
            'target_id': formJSON.target_id
        },
        success: function (data) {
            globalDataBuffer = data;

            //table data
            if (data.hasOwnProperty("table_data")) {
                var event = jQuery.Event("refreshtable");
                $('body').trigger(event);
            }

            //feedback
            if (data.hasOwnProperty("action_feedback") &&
                data.action_feedback.hasOwnProperty("status") &&
                data.action_feedback.hasOwnProperty("message")) {

                if (["error", "red", "danger", "negative"].indexOf(data.action_feedback.status) > -1) {
                    let feedbackControl = get_alert_control();
                    let alertClass = "alert-danger";

                    feedbackControl
                        .removeClass("alert-success")
                        .addClass(alertClass);
                    feedbackControl.find(".alert-message").html(data.action_feedback.message);

                    dialogRef.getModalBody().find(".formMessageDiv").html(feedbackControl);

                    btnSave.enable();
                    btnCancel.enable();
                    btnSave.stopSpin();

                    let modalId = dialogRef.getModal().closest(".bootstrap-dialog").attr("id");
                    $("#" + modalId).scrollTop(0);

                    return true;
                } else {
                    dialogRef.close();

                    // Close any other dialog that might be opened still if
                    // the prior 'close dialog' action does not close the current dialog
                    $.each(BootstrapDialog.dialogs, function (id, dialog) {
                        dialog.close();
                    });

                    refresh_profile_tool_tips();

                    do_crud_profile_action_feedback(data.action_feedback);

                    // Refresh web page to have change reflected after 3 seconds
                    setTimeout(function () {
                        window.location.reload();
                    }, 3000);
                    return true;
                }
            }

            dialogRef.close();
            refresh_profile_tool_tips();
        },
        error: function (data) {
            console.log(data.responseText);

            let feedbackControl = get_alert_control();
            let alertClass = "alert-danger";

            feedbackControl
                .removeClass("alert-success")
                .addClass(alertClass);
            feedbackControl.find(".alert-message").html(error_msg + ". Please check that you are connected to a network and try again.");

            dialogRef.getModalBody().find(".formMessageDiv").html(feedbackControl);

            btnSave.enable();
            btnCancel.enable();
            btnSave.stopSpin();

            let modalId = dialogRef.getModal().closest(".bootstrap-dialog").attr("id");
            $("#" + modalId).scrollTop(0);

            return true;
        }
    });
} //end of function