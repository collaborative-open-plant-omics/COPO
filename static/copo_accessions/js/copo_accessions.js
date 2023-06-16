var wizardMessages;
var sampleDescriptionToken = '';
var sampleTableInstance = null;

$(document).ready(function () {
    $(document).data("showAllCOPOAccessions", false)
    $(document).data("isSampleProfileTypeStandalone", false)
    $(document).data("isUserProfileActive", true)
    //****************************** Event Handlers Block *************************//

    // test begins
    // test ends
    //page global variables
    const csrftoken = $('[name="csrfmiddlewaretoken"]').val();
    const component = "accessions";
    const wizardURL = "/rest/sample_wiz/";
    const copoFormsURL = "/copo/copo_forms/";
    const copoVisualsURL = "/copo/copo_accessions_visualise/";

    const wizardElement = $('#sampleWizard');

    //get component metadata
    const componentMeta = get_component_meta(component);

    let componentName = $("#nav_component_name").val();

    //set up global navigation components
    do_page_controls(componentName);

    //load records
    load_accessions_records(componentMeta, copoVisualsURL);
    // toggle_accessions_view()

    //load pending description
    // pending_sample_description();

    //description table data
    var dtRows = [];
    var dtColumns = [];


    // handle/attach events to table buttons
    $('body').on('addbuttonevents', function (event) {
        do_record_task(event);
    });

    //trigger refresh of table
    $('body').on('refreshtable', function (event) {
        render_accessions_table(globalDataBuffer, componentMeta);
    });

    if (groups.includes("dtol_sample_managers") || groups.includes("erga_sample_managers") || groups.includes("dtolenv_sample_managers")) {
        $(".accept_reject_samples").show()
    }

    if (groups.includes("dtol_users") || groups.includes("dtol_sample_managers") || groups.includes("erga_users") || groups.includes("erga_sample_managers") || groups.includes("dtolenv_sample_managers")) {
        $(".tol_inspect").show()
    }

    $(document).on("click", ".accept_reject_samples", function (evt) {
        document.location = "/copo/accept_reject_sample"
    })

    $(document).on("click", ".tol_inspect", function (evt) {
        document.location = "/copo/tol_inspect"
    })

    $(document).on("click", ".copo_accessions", function (evt) {
        $(document).data("showAllCOPOAccessions", true)
        const tableLoader = $('<div class="copo-i-loader"></div>');
        let table_id = "*"
        // load_all_COPO_accessions_records(componentMeta, copoVisualsURL)
        load_accessions_records(componentMeta, copoVisualsURL);
        if (tableLoader) tableLoader.remove(); //remove loader
        // if ($(".table-parent-div").length) {
        //     $(table_id).find(".table-parent-div").show();
        // }
        if ($(".page-welcome-message").length) {
            $(table_id).find(".page-welcome-message").hide();
        }
    })

    // $(document).on("change", "#number_of_samples", function (evt) {
    //     let count = parseInt($(evt.currentTarget).val())
    //     disable_rack_id(count)
    // })


    // function disable_rack_id(count) {
    //     if (count > 1) {
    //         $("#rack_id").removeAttr("disabled")
    //     } else {
    //         $("#rack_id").attr("disabled", "disabled")
    //     }
    // }


    //custom stage renderers
    // var dispatchStageRenderer = {
    //     perform_sample_generation: function (stage) {
    //         generate_sample_edit_table(stage);
    //     },
    //     generate_dtol_stage: function (stage) {
    //         generate_dtol_stage(stage);
    //     }
    // }; //end of dispatchStageCallback

    //Enter-key event for table cell update...
    // $(document).on('keypress', '.cell-edit-panel', function (event) {
    //     var keyCode = event.keyCode || event.which;
    //     if (keyCode === 13) {
    //         event.preventDefault();
    //
    //         var cells = sampleTableInstance.cells('.focus');
    //
    //         if (cells && cells[0].length > 0) {
    //             $(document).find(".copo-form-group").webuiPopover('destroy');
    //
    //             var cell = cells[0];
    //             var targetCell = sampleTableInstance.cell(cell[0].row, cell[0].column);
    //
    //             manage_cell_edit(sampleTableInstance, targetCell);
    //         }
    //
    //         return false;
    //     }
    // });
    //
    // //handle file description file upload
    // $(document).on('change', '#description_file', function (e) {
    //     if ($(this).prop('files').length > 0) {
    //         var file = this.files[0];
    //         var file_type = file.type;
    //
    //         var permitted_types = ["text/csv"];
    //
    //         if (permitted_types.indexOf(file_type) > -1) {
    //             formdata = new FormData();
    //             formdata.append("csv", file);
    //             formdata.append("request_action", "description_csv");
    //             formdata.append("description_token", sampleDescriptionToken + "");
    //             var dialog = null;
    //
    //             $.ajax({
    //                 type: 'POST',
    //                 url: wizardURL,
    //                 headers: {
    //                     'X-CSRFToken': csrftoken
    //                 },
    //                 data: formdata,
    //                 contentType: false,
    //                 cache: false,
    //                 processData: false,
    //                 beforeSend: function () {
    //                     dialog = trigger_csv_upload();
    //                     dialog.realize();
    //                     dialog.open();
    //                     $(dialog.getModalBody()).find(".feedbackrow").find(".feedbackcol").html("<div>Processing <strong>" + file.name + "</strong></div><div style='margin-top: 5px;'>Please wait...</div>");
    //                 },
    //                 success: function (data) {
    //                     var result = data.result;
    //                     if (result.hasOwnProperty("status") && result.status == "success") {
    //                         dialog.setType(BootstrapDialog.TYPE_SUCCESS);
    //                         $(dialog.getModalBody()).find(".feedbackrow").find(".feedbackcol").html("<span class='text-success'>Successfully ingested metadata from " + file.name + "</span>");
    //                         $($(dialog.getModalFooter()).find("#btn-cancel-process")[0])
    //                             .addClass('green')
    //                             .html('Refresh table');
    //                     } else if (result.hasOwnProperty("status") && result.status == "error") {
    //                         dialog.setType(BootstrapDialog.TYPE_DANGER);
    //                         $(dialog.getModalBody()).find(".feedbackrow").find(".feedbackcol").html("<span class='text-danger'>" + result.message + "</span>");
    //                         $($(dialog.getModalFooter()).find("#btn-cancel-process")[0])
    //                             .addClass('red')
    //                             .html('Abort');
    //                     }
    //                 }
    //             });
    //
    //         } else {
    //             BootstrapDialog.show({
    //                 title: "File Type Error",
    //                 message: "Please select a valid CSV file",
    //                 cssClass: 'copo-modal3',
    //                 closable: false,
    //                 animate: true,
    //                 type: BootstrapDialog.TYPE_DANGER,
    //                 buttons: [{
    //                     label: 'OK',
    //                     cssClass: 'tiny ui basic red button',
    //                     action: function (dialogRef) {
    //                         dialogRef.close();
    //                     }
    //                 }]
    //             });
    //             $(this).val('');
    //             return false;
    //         }
    //     }
    //
    // });


    //---------------------

    $(document).on("click", ".btn-toggle1 .btn-toggle2", toggle_accessions_view)

    //******************************* wizard events *******************************//

    //handle event for saving description for later...
    // $('#reload_act').on('click', function (event) {
    //     window.location.reload();
    // });

    //handle event for discarding current description...
    // $('#remove_act').on('click', function (event) {
    //     //confirm user decision
    //     BootstrapDialog.show({
    //         title: "Discard description",
    //         message: "Are you sure you want to discard the current description?",
    //         cssClass: 'copo-modal3',
    //         closable: false,
    //         animate: true,
    //         type: BootstrapDialog.TYPE_DANGER,
    //         buttons: [
    //             {
    //                 label: 'Cancel',
    //                 cssClass: 'tiny ui basic button',
    //                 action: function (dialogRef) {
    //                     dialogRef.close();
    //                 }
    //             },
    //             {
    //                 label: '<i class="copo-components-icons fa fa-times"></i> Discard',
    //                 cssClass: 'tiny ui basic red button',
    //                 action: function (dialogRef) {
    //                     if (sampleDescriptionToken == '') {
    //                         dialogRef.close();
    //                         window.location.reload();
    //                     } else {
    //                         $.ajax({
    //                             url: wizardURL,
    //                             type: "POST",
    //                             headers: {
    //                                 'X-CSRFToken': csrftoken
    //                             },
    //                             data: {
    //                                 'request_action': "discard_description",
    //                                 'description_token': sampleDescriptionToken
    //
    //                             },
    //                             success: function (data) {
    //                                 dialogRef.close();
    //                                 window.location.reload();
    //
    //                             },
    //                             error: function () {
    //                                 alert("An error occurred!");
    //                             }
    //                         });
    //                     }
    //                 }
    //             }
    //         ]
    //     });
    //
    // });
    //
    // $('.wiz-showme').on('click', function (e) {
    //     e.preventDefault();
    //
    //     var target = $(this).attr("data-target");
    //     var label = $(this).attr("data-label");
    //     var item = null;
    //
    //     if ($("#" + target).length) {
    //         item = $("#" + target);
    //     } else if ($("." + target).length) {
    //         item = $("." + target)[0];
    //     }
    //
    //     if (item) {
    //         item.webuiPopover('destroy');
    //         item.webuiPopover({
    //             title: label,
    //             content: '<div class="webpop-content-div">Click x to dismiss</div>',
    //             trigger: 'sticky',
    //             width: 200,
    //             arrow: true,
    //             closeable: true,
    //             backdrop: true
    //         });
    //     }
    // });
    //
    //
    // //handle events for step change
    // wizardElement.on('actionclicked.fu.wizard', function (evt, data) {
    //     $(self).data('step', data.step);
    //
    //     stage_navigate(evt, data);
    // });
    //
    // //handle events for step change
    // wizardElement.on('changed.fu.wizard', function (evt, data) {
    //     //form controls help tip
    //     refresh_accessions_tool_tips();
    //     var activeStageIndx = wizardElement.wizard('selectedItem').step;
    //
    //     //set up validator
    //     set_up_validator($("#wizard_form_" + activeStageIndx));
    // });
    //
    // //sample accession resolution
    // $(document).on("click", ".resolver-submit", function (event) {
    //     event.preventDefault();
    //
    //     var parentElem = $(this).closest(".copo-form-group");
    //     var dataElem = parentElem.find(".resolver-data");
    //     var resolverValue = dataElem.val().replace(/^\s+|\s+$/g, '');
    //
    //
    //     if (resolverValue.length == 0) {
    //         return false;
    //     }
    //
    //     var spinnerElem = $('<button/>',
    //         {
    //             type: "button",
    //             class: "btn btn-default",
    //             html: '<i class="fa fa-spinner fa-pulse fa-1x"></i>'
    //         });
    //
    //     spinnerElem.insertBefore($(this));
    //
    //     //get resolver uri
    //     var resolverURL = dataElem.attr("data-resolve-uri") + resolverValue;
    //
    //     //get resolver component
    //     var resolverComponent = dataElem.attr("data-resolve-component");
    //
    //     if (resolverComponent.toLowerCase() == "biosample") {
    //         $.ajax({
    //             url: wizardURL,
    //             type: "POST",
    //             headers: {
    //                 'X-CSRFToken': csrftoken
    //             },
    //             data: {
    //                 'request_action': "resolve_uri",
    //                 'resolver_uri': resolverURL
    //
    //             },
    //             success: function (data) {
    //                 spinnerElem.remove();
    //                 if (data.resolved_output.status == 'success') {
    //                     //set hidden value, and display result to user
    //                     parentElem.removeClass("has-error has-danger");
    //                     parentElem.find(".help-block").html("Successfully resolved accession. Resolved sample has been registered, and also displayed below. Click 'Next' to proceed.");
    //                     $('#' + dataElem.attr('id') + "_hidden").val(JSON.stringify(data.resolved_output.value));
    //                     parentElem.find(".feedback-element").html(JSON.stringify(data.resolved_output.value));
    //                 } else {
    //                     $('#' + dataElem.attr('id') + "_hidden").val('');
    //                     parentElem.find(".feedback-element").html('');
    //                     parentElem.addClass("has-error has-danger");
    //                     parentElem.find(".help-block").html("Couldn't resolve " + resolverValue + "!");
    //                 }
    //             },
    //             error: function () {
    //                 alert("Error while attempting to resolve accession!");
    //             }
    //         });
    //     }
    // });
    //
    // $(document).on("change", ".copo-input-data", function () {
    //     if (["provided_names", "bundle_name"].indexOf(this.id) > -1) {
    //         var shownValue = $(this).val().trim();
    //         var hiddenValue = $('#' + this.id + "_hidden").val().trim();
    //
    //         if (shownValue != hiddenValue) {
    //             $(this).closest(".copo-form-group").find(".help-block").html('');
    //             $('#' + this.id + "_hidden").val('');
    //             return false;
    //         }
    //     }
    // });
    //
    // //copo-trigger-submit control handling
    // $(document).on("click", ".copo-trigger-submit", function (event) {
    //     event.preventDefault();
    //
    //     var parentElem = $(this).closest(".copo-form-group");
    //     var triggerTarget = $(this).attr("data-target");
    //     var dataElem = parentElem.find(".copo-input-data");
    //     var inputValue = dataElem.val().replace(/^\s+|\s+$/g, '');
    //
    //
    //     if (inputValue.length == 0) {
    //         parentElem.find(".feedback-element").html('');
    //         parentElem.addClass("has-error has-danger");
    //         parentElem.find(".help-block").html('');
    //         parentElem.find(".help-block").eq(0).html("Please enter a value for " + parentElem.find("label").html() + "!");
    //         return false;
    //     }
    //
    //     parentElem.find(".spinner-element").remove();
    //
    //     var spinnerElem = $('<button/>',
    //         {
    //             type: "button",
    //             class: "btn btn-default spinner-element",
    //             html: '<i class="fa fa-spinner fa-pulse fa-1x"></i>'
    //         });
    //
    //     spinnerElem.insertBefore($(this));
    //
    //
    //     if (triggerTarget == "provided_names") {
    //         $.ajax({
    //             url: wizardURL,
    //             type: "POST",
    //             headers: {
    //                 'X-CSRFToken': csrftoken
    //             },
    //             data: {
    //                 'request_action': "validate_sample_names",
    //                 'sample_names': inputValue,
    //                 'description_token': sampleDescriptionToken
    //
    //             },
    //             success: function (data) {
    //                 spinnerElem.remove();
    //                 if (data.validation_result.status == "success") {
    //                     //set hidden value, and give all clear signal
    //                     parentElem.find(".help-block").html('');
    //                     parentElem.removeClass("has-error has-danger");
    //                     parentElem.find(".help-block").eq(0).html("Supplied names are valid and have been registered! Click 'Next' to proceed.");
    //                     $('#' + dataElem.attr('id') + "_hidden").val(inputValue);
    //                     parentElem.find(".feedback-element").html('');
    //                     dataElem.trigger('change'); //this was needed to properly propagate error reporting
    //                 } else {
    //                     parentElem.find(".help-block").html('');
    //                     $('#' + dataElem.attr('id') + "_hidden").val('');
    //                     parentElem.find(".feedback-element").html('');
    //                     parentElem.addClass("has-error has-danger");
    //                     parentElem.find(".help-block").eq(0).html("Validation error! Please see below for details.");
    //
    //                     var tbl = $('<table/>',
    //                         {
    //                             id: "feedback_provided_names",
    //                             "class": "ui celled table hover copo-noborders-table",
    //                             cellspacing: "0",
    //                             width: "100%"
    //                         });
    //
    //                     var dataSet = data.validation_result.errors;
    //
    //                     parentElem.find(".feedback-element").append(tbl);
    //
    //
    //                     $('#feedback_provided_names').DataTable({
    //                         data: dataSet,
    //                         "paging": false,
    //                         "lengthChange": false,
    //                         "searching": false,
    //                         columns: data.validation_result.error_columns
    //                     });
    //                 }
    //             },
    //             error: function () {
    //                 alert("Error while attempting to validate sample names!");
    //             }
    //         });
    //     } else if (triggerTarget == "bundle_name") {
    //         $.ajax({
    //             url: wizardURL,
    //             type: "POST",
    //             headers: {
    //                 'X-CSRFToken': csrftoken
    //             },
    //             data: {
    //                 'request_action': "validate_bundle_name",
    //                 'bundle_name': inputValue,
    //                 'description_token': sampleDescriptionToken
    //
    //             },
    //             success: function (data) {
    //                 spinnerElem.remove();
    //                 if (data.validation_status == "success") {
    //                     //set hidden value, and give all clear signal
    //                     parentElem.find(".help-block").html('');
    //                     parentElem.removeClass("has-error has-danger");
    //                     parentElem.find(".help-block").eq(0).html("Bundle name is valid and will be used to generate sample names of the form: " + inputValue + "_1, " + inputValue + "_2,...! " + " Click 'Next' to proceed.");
    //                     $('#' + dataElem.attr('id') + "_hidden").val(inputValue);
    //                     dataElem.trigger('change'); //this was needed to properly propagate error reporting
    //                 } else {
    //                     parentElem.find(".help-block").html('');
    //                     $('#' + dataElem.attr('id') + "_hidden").val('');
    //                     parentElem.addClass("has-error has-danger");
    //                     parentElem.find(".help-block").eq(0).html("Generating sample names from bundle name will violate unique constraint! Please enter another bundle name and click 'Validate!'");
    //                 }
    //             },
    //             error: function () {
    //                 alert("Error while attempting to validate bundle name!");
    //             }
    //         });
    //     }
    // });


    //instantiate/refresh tooltips
    refresh_accessions_tool_tips();


    //****************************** Functions Block ******************************//
    function toggle_disable_next() {
        //disables/enables wizard's next button
        var elem = $(".btn-next");
        if (elem.hasClass("loading")) {
            elem.removeClass("loading");
            elem.prop('disabled', false);
        } else {
            elem.addClass("loading");
            elem.prop('disabled', true);
        }
    }

    function add_step(auto_fields) {

        // retrieve and/or re-validate next stage
        $.ajax({
            url: wizardURL,
            type: "POST",
            headers: {'X-CSRFToken': csrftoken},
            data: {
                'request_action': 'next_stage',
                'description_token': sampleDescriptionToken,
                'auto_fields': auto_fields
            },
            success: function (data) {
                var wizard_components = data.next_stage;
                if (wizard_components.hasOwnProperty('abort') && wizard_components.abort) {
                    //abort the description

                    BootstrapDialog.show({
                        title: 'Wizard Error!',
                        message: "Can't continue with description due to incomplete control information. Please restart the description process.",
                        cssClass: 'copo-modal3',
                        closable: false,
                        animate: true,
                        type: BootstrapDialog.TYPE_DANGER,
                        buttons: [
                            {
                                label: '<i class="copo-components-icons fa fa-times"></i> OK',
                                cssClass: 'tiny ui basic red button',
                                action: function (dialogRef) {
                                    dialogRef.close();
                                    window.location.reload();
                                }
                            }
                        ]
                    });

                    return false;
                }

                //call to refresh wizard
                if (wizard_components.hasOwnProperty('refresh_wizard') && wizard_components.refresh_wizard) {
                    refresh_wizard();
                }

                //check for and set stage
                if (wizard_components.hasOwnProperty('stage')) {
                    process_wizard_stage(wizard_components.stage);
                }
            },
            error: function () {
                alert("Couldn't retrieve next stage!");
            }
        });
    }

    // function stage_navigate(evt, data) {
    //     if (data.direction == 'next') {
    //
    //         evt.preventDefault();
    //
    //         //end of wizard intercept
    //         // call this if we are on the last stage....
    //         if (wizardElement.find('.steps li.active:first').attr('data-name') == 'review') {
    //             finalise_description();
    //             return false;
    //         }
    //
    //         //get referenced stage
    //         var activeStageIndx = wizardElement.wizard('selectedItem').step;
    //
    //         // get form inputs
    //         var form_values = {};
    //
    //         //trigger form validation
    //         var stageForm = $("#wizard_form_" + activeStageIndx);
    //         if (stageForm.length) {
    //             stageForm.trigger('submit');
    //
    //             if (stageForm.find("#bcopovalidator").val() == "false") {
    //                 stageForm.find("#bcopovalidator").val("true");
    //                 return false;
    //             }
    //
    //             $('#wizard_form_' + activeStageIndx).find(":input").each(function () {
    //                 form_values[this.id] = $(this).val();
    //             });
    //         }
    //
    //         //call to load next stage
    //
    //         add_step(JSON.stringify(form_values));
    //         toggle_disable_next();
    //
    //     } else if (data.direction == 'previous') {
    //         // get the proposed or intended state, for which action is intercepted
    //         evt.preventDefault();
    //
    //         set_wizard_stage(data.step - 1);
    //
    //         //re-enable stage navigation button
    //         var elem = $(".btn-next");
    //         if (elem.hasClass("loading")) {
    //             elem.removeClass("loading");
    //             elem.prop('disabled', false);
    //         }
    //     }
    //
    // }

    // function set_wizard_stage(proposedState) {
    //     wizardElement.wizard('selectedItem', {
    //         step: proposedState
    //     });
    //
    //     toggle_disable_next();
    // }
    //
    // function refresh_wizard() {
    //     //get referenced stage
    //     var activeStageIndx = wizardElement.wizard('selectedItem').step;
    //
    //     //remove steps from wizard to start from current step
    //     var numSteps = wizardElement.find('.steps li').length;
    //     var stepIndex = activeStageIndx + 1;
    //     var howMany = numSteps - stepIndex;
    //
    //     wizardElement.wizard('removeSteps', stepIndex, howMany);
    //     wizardElement.find('.steps li:last-child').hide();
    // }
    //
    //
    // function process_wizard_stage(stage) {
    //     // get next step index
    //     var numSteps = wizardElement.find('.steps li').length;
    //
    //
    //     if (!stage.hasOwnProperty("ref")) {
    //         //no stage returned, signalling last stage
    //         wizardElement.find('.steps li:last-child').show();
    //         set_wizard_stage(numSteps);
    //
    //         return false;
    //     }
    //
    //     //check stage has not been rendered already
    //     var foundStage = false;
    //
    //     wizardElement.find('.steps li').each(function () {
    //         if ($(this).find(".wiz-title").attr("data-stage") == stage.ref) {
    //             foundStage = true;
    //             return false;
    //         }
    //     });
    //
    //     if (foundStage) {
    //         set_wizard_stage(wizardElement.wizard('selectedItem').step + 1);
    //         return false;
    //     }
    //
    //
    //     //generate stage content
    //     var stage_pane = '<div id="custom-renderer_' + stage.ref + '"></div>';
    //
    //     if (!stage.hasOwnProperty("renderer")) {
    //         stage_pane = get_pane_content(wizardStagesForms(stage), numSteps, stage.message);
    //     }
    //
    //     wizardElement.wizard('addSteps', numSteps, [
    //         {
    //             label: '<span data-stage="' + stage.ref + '" class=wiz-title>' + stage.title + '</span>',
    //             pane: stage_pane
    //         }
    //     ]);
    //
    //
    //     //set focus to the currently added stage
    //     set_wizard_stage(numSteps);
    //
    //     //get custom renderer
    //     if (stage.hasOwnProperty("renderer")) {
    //         toggle_disable_next();
    //         //custom content will sit here...
    //
    //         $('#custom-renderer_' + stage.ref).append('<div class="stage-content"></div>');
    //
    //         //add form to stage to capture current_stage and other required properties
    //         var formDiv = $('<div/>');
    //         var hiddenCtrl = $('<input/>',
    //             {
    //                 type: "hidden",
    //                 id: "current_stage",
    //                 name: "current_stage",
    //                 value: stage.ref
    //             });
    //
    //         //append to this form, if need be, within a renderer
    //
    //         var formCtrl = $('<form/>',
    //             {
    //                 id: "wizard_form_" + numSteps,
    //                 class: "wizard-dynamic-form"
    //             });
    //
    //         formCtrl.append(hiddenCtrl);
    //
    //         formDiv.append(formCtrl);
    //         $('#custom-renderer_' + stage.ref).append(formDiv);
    //
    //         dispatchStageRenderer[stage.renderer](stage);
    //
    //         set_up_validator($("#wizard_form_" + numSteps)); //needed here to account for delay in content display
    //         toggle_disable_next();
    //     }
    //
    // } //end of func


    function set_up_validator(theForm) {
        //validate on submit event

        if (!theForm.length) {
            return false;
        }

        if (!theForm.find("#bcopovalidator").length) {
            custom_validate(theForm);
            refresh_validator(theForm);

            var bvalidator = $('<input/>',
                {
                    type: "hidden",
                    id: "bcopovalidator",
                    name: "bcopovalidator",
                    value: "true"
                });

            //add validator flag
            theForm.append(bvalidator);

            theForm.validator().on('submit', function (e) {
                if (e.isDefaultPrevented()) {
                    $(this).find("#bcopovalidator").val("false");
                    return false;
                } else {
                    e.preventDefault();
                    $(this).find("#bcopovalidator").val("true");
                }
            });
        }

    } //end set_up_validator()

    function get_pane_content(stage_content, step, stage_message) {
        var row = $('<div/>', {
            class: "row"
        });

        var left = $('<div/>', {
            class: "col-sm-9"
        });

        var right = $('<div/>', {
            class: "col-sm-3"
        });

        var message = $('<div/>', {class: "webpop-content-div"});
        message.append(stage_message);

        var feedback = get_feedback_pane();
        feedback.find(".close").remove();
        feedback
            .removeClass("success");

        feedback.find(".header").html("");
        feedback.find("p").append(message);

        right.append(feedback);

        row
            .append(left)
            .append(right);


        var stageHTML = $('<div/>');

        left.append(stageHTML);

        //form controls
        var formPanel = $('<div/>', {
            style: "margin-top: 5px; font-size: 14px;"
        });


        stageHTML.append(formPanel);

        var formPanelBody = $('<div/>');

        formPanel.append(formPanelBody);

        var formDiv = $('<div/>', {
            style: "margin-top: 20px;"
        });

        formPanelBody.append(formDiv);

        var formCtrl = $('<form/>',
            {
                id: "wizard_form_" + step,
                class: "wizard-dynamic-form"
            });

        formCtrl.append(stage_content);

        formDiv.append(formCtrl);

        var navrow = $('<div/>', {
            class: "row",
            style: "margin-top:20px;"
        });

        var navcol = $('<div/>', {
            class: "col-sm-12"
        });

        var navbuttons = '<div class="large ui buttons">\n' +
            '  <button class="ui button wiz-btn-prev">Prev</button>\n' +
            '  <div class="or"></div>\n' +
            '  <button class="ui primary button wiz-btn-next">Next</button>\n' +
            '</div>';

        navcol.append(navbuttons);
        navrow.append(navcol);
        left.append('<hr/>');
        left.append(navrow);

        return row;
    }

    // function initiate_description(parameters) {
    //     $('[data-toggle="tooltip"]').tooltip('destroy');
    //
    //     if (!$("#wizard_toggle").is(":visible")) {
    //         var $dialogContent = $('<div/>');
    //         var notice_div = $('<div/>').html("Initiating description...");
    //         var spinner_div = $('<div/>', {style: "margin-left: 40%; padding-top: 15px; padding-bottom: 15px;"}).append($('<div class="copo-i-loader"></div>'));
    //
    //         var description_token = '';
    //         if (parameters.hasOwnProperty('description_token')) {
    //             description_token = parameters.description_token;
    //         }
    //
    //         var dialog = new BootstrapDialog({
    //             type: BootstrapDialog.TYPE_PRIMARY,
    //             size: BootstrapDialog.SIZE_NORMAL,
    //             title: function () {
    //                 return $('<span>Samples description</span>');
    //             },
    //             closable: false,
    //             animate: true,
    //             draggable: false,
    //             onhide: function (dialogRef) {
    //                 //nothing to do for now
    //             },
    //             onshown: function (dialogRef) {
    //                 $.ajax({
    //                     url: wizardURL,
    //                     type: "POST",
    //                     headers: {
    //                         'X-CSRFToken': csrftoken
    //                     },
    //                     data: {
    //                         'request_action': "initiate_description",
    //                         'description_token': description_token,
    //                         'profile_id': $('#profile_id').val()
    //                     },
    //                     success: function (data) {
    //                         if (data.result.status == 'success') {
    //                             //set description token
    //                             sampleDescriptionToken = data.result.description_token;
    //
    //                             //set wizard messages
    //                             wizardMessages = data.result.wiz_message;
    //
    //                             //display wizard
    //                             $("#wizard_toggle").collapse("toggle");
    //
    //                             //hide the review stage -- to be redisplayed when all the dynamic stages are displayed
    //                             wizardElement.find('.steps li:last-child').hide();
    //
    //                             //remove sample incomplete description object from info pane
    //                             if (parameters.hasOwnProperty('info_object')) {
    //                                 parameters.info_object.closest(".inc-desc-badge").remove();
    //                             }
    //
    //                             set_up_validator($("#wizard_form_1"));
    //
    //                             dialogRef.close();
    //
    //                         } else {
    //                             var $feeback = $('<div/>', {
    //                                 "class": "webpop-content-div",
    //                                 style: "padding-bottom: 15px;"
    //                             }).html("Please resolve the following issue to proceed with your description.<div style='margin-top: 10px; margin-bottom: 15px;'>" + data.result.message + "</div>");
    //                             var $button = $('<div class="tiny ui basic red button">Resolve issue</div>');
    //                             $button.on('click', {dialogRef: dialogRef}, function (event) {
    //                                 event.data.dialogRef.close();
    //                             });
    //
    //                             dialog.setType(BootstrapDialog.TYPE_DANGER);
    //                             dialog.getModalBody().html('').append($feeback).append($button);
    //                         }
    //
    //                     },
    //                     error: function () {
    //                         alert("Error instantiating description!");
    //                     }
    //                 });
    //             },
    //             buttons: []
    //         });
    //
    //
    //         $dialogContent.append(notice_div).append(spinner_div);
    //         dialog.realize();
    //         dialog.setMessage($dialogContent);
    //         dialog.open();
    //
    //     } else {//wizard is already visible
    //         var message = "<div class='webpop-content-div'>There's an ongoing description. Terminate the current description, before attempting to initiate a new description or reload a previous one.</div>";
    //
    //         BootstrapDialog.show({
    //             title: 'Description instantiation',
    //             message: message,
    //             // cssClass: 'copo-modal3',
    //             closable: false,
    //             animate: true,
    //             type: BootstrapDialog.TYPE_WARNING,
    //             buttons: [
    //                 {
    //                     label: 'OK',
    //                     cssClass: 'tiny ui basic orange button',
    //                     action: function (dialogRef) {
    //                         dialogRef.close();
    //                     }
    //                 }
    //             ]
    //         });
    //     }
    //
    //     $("[data-toggle='tooltip']").tooltip();
    // }


    // function show_sample_source() {
    //     //show description bundle
    //
    //     var tableID = 'sample_source_view_tbl';
    //     var tbl = $('<table/>',
    //         {
    //             id: tableID,
    //             "class": "ui celled table hover copo-noborders-table",
    //             cellspacing: "0",
    //             width: "100%"
    //         });
    //
    //     var $dialogContent = $('<div/>');
    //     var table_div = $('<div/>').append(tbl);
    //     var spinner_div = $('<div/>', {style: "margin-left: 40%; padding-top: 15px; padding-bottom: 15px;"}).append($('<div class="copo-i-loader"></div>'));
    //
    //     var dialog = new BootstrapDialog({
    //         type: BootstrapDialog.TYPE_PRIMARY,
    //         size: BootstrapDialog.SIZE_NORMAL,
    //         title: function () {
    //             return $('<span>Sample source</span>');
    //         },
    //         closable: false,
    //         animate: true,
    //         draggable: false,
    //         onhide: function (dialogRef) {
    //             //nothing to do for now
    //         },
    //         onshown: function (dialogRef) {
    //             $.ajax({
    //                 url: copoVisualsURL,
    //                 type: "POST",
    //                 headers: {
    //                     'X-CSRFToken': csrftoken
    //                 },
    //                 data: {
    //                     'task': "table_data",
    //                     'component': "source"
    //                 },
    //                 success: function (data) {
    //                     var dataSet = data.table_data.dataSet;
    //                     var cols = data.table_data.columns;
    //                     spinner_div.remove();
    //
    //                     var dtd = dataSet;
    //                     var cols = cols;
    //
    //                     var table = null;
    //
    //                     table = $('#' + tableID).DataTable({
    //                         data: dtd,
    //                         searchHighlight: true,
    //                         "lengthChange": false,
    //                         order: [
    //                             [1, "asc"]
    //                         ],
    //                         scrollY: "300px",
    //                         scrollX: true,
    //                         scrollCollapse: true,
    //                         paging: false,
    //                         language: {
    //                             "info": " _START_ to _END_ of _TOTAL_ sources",
    //                             "search": " "
    //                         },
    //                         select: {
    //                             style: 'multi',
    //                             selector: 'td:first-child'
    //                         },
    //                         columns: cols,
    //                         dom: 'lfit<"row">rp'
    //                     });
    //
    //                     $('#' + tableID + '_wrapper')
    //                         .find(".dataTables_filter")
    //                         .find("input")
    //                         .removeClass("input-sm")
    //                         .attr("placeholder", "Search sample source");
    //
    //                     //handle event for table details
    //                     $('#' + tableID + ' tbody')
    //                         .off('click', 'td.summary-details-control')
    //                         .on('click', 'td.summary-details-control', function (event) {
    //                             event.preventDefault();
    //
    //                             var event = jQuery.Event("posttablerefresh"); //individual compnents can trap and handle this event as they so wish
    //                             $('body').trigger(event);
    //
    //                             var tr = $(this).closest('tr');
    //                             var row = table.row(tr);
    //                             tr.addClass('showing');
    //
    //                             if (row.child.isShown()) {
    //                                 // This row is already open - close it
    //                                 row.child('');
    //                                 row.child.hide();
    //                                 tr.removeClass('showing');
    //                                 tr.removeClass('shown');
    //                             } else {
    //                                 $.ajax({
    //                                     url: copoVisualsURL,
    //                                     type: "POST",
    //                                     headers: {
    //                                         'X-CSRFToken': csrftoken
    //                                     },
    //                                     data: {
    //                                         'task': "attributes_display",
    //                                         'component': "source",
    //                                         'target_id': row.data().record_id
    //                                     },
    //                                     success: function (data) {
    //                                         if (data.component_attributes.columns) {
    //                                             // expand row
    //
    //                                             var contentHtml = $('<table/>', {
    //                                                 // cellpadding: "5",
    //                                                 cellspacing: "0",
    //                                                 border: "0",
    //                                                 // style: "padding-left:50px;"
    //                                             });
    //
    //                                             for (var i = 0; i < data.component_attributes.columns.length; ++i) {
    //                                                 var colVal = data.component_attributes.columns[i];
    //
    //                                                 var colTR = $('<tr/>');
    //                                                 contentHtml.append(colTR);
    //
    //                                                 colTR
    //                                                     .append($('<td/>').append(colVal.title))
    //                                                     .append($('<td/>').append(data.component_attributes.data_set[colVal.data]));
    //
    //                                             }
    //
    //                                             row.child($('<div></div>').append(contentHtml).html()).show();
    //                                             tr.removeClass('showing');
    //                                             tr.addClass('shown');
    //                                         }
    //                                     },
    //                                     error: function () {
    //                                         alert("Couldn't retrieve " + component + " attributes!");
    //                                         return '';
    //                                     }
    //                                 });
    //                             }
    //                         });
    //
    //                 },
    //                 error: function () {
    //                     alert("Couldn't sample source!");
    //                     dialogRef.close();
    //                 }
    //             });
    //         },
    //         buttons: [{
    //             label: 'OK',
    //             cssClass: 'tiny ui basic primary button',
    //             action: function (dialogRef) {
    //                 dialogRef.close();
    //             }
    //         }]
    //     });
    //
    //
    //     $dialogContent.append(table_div).append(spinner_div);
    //     dialog.realize();
    //     dialog.setMessage($dialogContent);
    //     dialog.open();
    // } // end of function

    //handles button events on a record or group of records
    function do_record_task(event) {
        var task = event.task.toLowerCase(); //action to be performed e.g., 'Edit', 'Delete'
        var tableID = event.tableID; //get target table

        //describe task
        if (task == "describe") {
            initiate_description({});
            return false;
        }

        //show sample source table
        //sample-source
        if (task == "sample-source") {
            show_sample_source();
            return false;
        }

        //retrieve target records and execute task
        var table = $('#' + tableID).DataTable();
        var records = []; //
        $.map(table.rows('.selected').data(), function (item) {
            records.push(item);
        });


        //edit task
        if (task == "edit") {
            $.ajax({
                url: copoFormsURL,
                type: "POST",
                headers: {'X-CSRFToken': csrftoken},
                data: {
                    'task': 'form',
                    'component': component,
                    'target_id': records[0].record_id //only allowing row action for edit, hence first record taken as target
                },
                success: function (data) {
                    json2HtmlForm(data);
                },
                error: function () {
                    alert("Couldn't build sample form!");
                }
            });
        }

        //table.rows().deselect(); //deselect all rows


    } //end of func

    function wizardStagesForms(stage) {
        var formValue = stage.data;

        var formDiv = $('<div/>');

        //build form elements
        for (var i = 0; i < stage.items.length; ++i) {
            var formElem = stage.items[i];
            var control = formElem.control;

            var elemValue = null;

            //set default values
            if (formElem.default_value) {
                elemValue = formElem.default_value;
            } else {
                elemValue = "";
            }

            if (formValue) {
                var elem = formElem.id.split(".").slice(-1)[0];
                if (formValue[elem]) {
                    elemValue = formValue[elem];
                }
            }

            if (formElem.hidden == "true") {
                control = "hidden";
            }

            try {
                formDiv.append(dispatchFormControl[controlsMapping[control.toLowerCase()]](formElem, elemValue));
            } catch (err) {
                formDiv.append('<div class="form-group copo-form-group"><span class="text-danger">Form Control Error</span> (' + formElem.label + '): Cannot resolve form control!</div>');
            }

        }

        //add current stage to form
        var hiddenCtrl = $('<input/>',
            {
                type: "hidden",
                id: "current_stage",
                name: "current_stage",
                value: stage.ref
            });

        formDiv.append(hiddenCtrl);

        return formDiv;
    }

    function manage_cell_edit(table, cell) {
        // function handles editing of cell

        var node = cell.node();

        //does cell have 'focus'?
        var nodeClass = node.className.split(" ");

        if (nodeClass.indexOf("focus") == -1) {
            return false;
        }

        //get record id of target cell
        var recordID = table.row(cell.index().row).id().split("row_")[1];


        //is it a call to edit or save?
        if ($(node).find(".cell-edit-panel").length) { // call to save
            //get cell form data
            var form_values = {};
            $(node).find(".cell-edit-panel").find(":input").each(function () {
                try {
                    form_values[this.id] = $(this).val().trim();
                } catch (err) {
                    form_values[this.id] = $(this).val();
                }
            });

            $(node).find("#cell-loader").show();
            $(node).find(".cell-edit-panel").hide();

            $.ajax({
                url: wizardURL,
                type: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    'request_action': "save_cell_data",
                    'cell_reference': dtColumns[cell.index().column].data,
                    'target_id': recordID,
                    'auto_fields': JSON.stringify(form_values),
                    'description_token': sampleDescriptionToken

                },
                success: function (data) {
                    if (data.cell_update.status == 'success') {

                        //set data and redraw table
                        table
                            .cell(cell.index().row, cell.index().column)
                            .data(data.cell_update.value)
                            .invalidate()
                            .draw();

                        //refresh search box
                        table
                            .search('')
                            .draw();


                        //re-enable table navigation keys
                        table.keys.enable();

                        //deselect previously selected rows
                        table.rows('.selected').deselect();

                        //set focus on next row
                        table.cell(cell.index().row + 1, cell.index().column).focus();
                    } else {
                        $(node).find("#cell-loader").hide();
                        $(node).find(".cell-edit-panel").show();
                        alert("Error: " + data.cell_update.message);
                    }
                },
                error: function () {
                    alert("Error while attempting to update sample cell!");
                }
            });

        } else { // call to edit
            //disable table navigation keys
            table.keys.disable();

            $.ajax({
                url: wizardURL,
                type: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    'request_action': "get_cell_control",
                    'cell_reference': dtColumns[cell.index().column].data,
                    'target_id': recordID,
                    'description_token': sampleDescriptionToken

                },
                success: function (data) {
                    var formElem = data.cell_control.control_schema;
                    var elemValue = data.cell_control.schema_data;
                    var htmlCtrl = dispatchFormControl[controlsMapping[formElem.control.toLowerCase()]](formElem, elemValue);
                    // htmlCtrl.find("label").remove();

                    var cellEditPanel = get_cell_edit_panel();
                    cellEditPanel.find("#cell-loader").hide();
                    cellEditPanel.find(".cell-edit-panel").append(htmlCtrl);
                    $(node)
                        .html('')
                        .append(cellEditPanel);

                    //set focus to control
                    if (cellEditPanel.find(".form-control")) {
                        cellEditPanel.find(".form-control").focus();
                    } else if (cellEditPanel.find(".input-copo")) {
                        cellEditPanel.find(".input-copo").focus();
                    }

                    refresh_accessions_tool_tips();

                    //set focus to selectize control
                    if (selectizeObjects.hasOwnProperty(formElem.id)) {
                        var selectizeControl = selectizeObjects[formElem.id];
                        selectizeControl.focus();
                    }
                },
                error: function () {
                    alert("Error while attempting to build cell form!");
                    table.keys.enable();
                    return false;
                }
            });
        }
    }

    function get_cell_edit_panel() {
        var attributesPanel = $('<div/>', {
            class: "cell-edit-panel",
            style: "min-width:450px; border:none; margin-bottom:0px; padding:5px;"
        });

        var loaderObject = $('<div>', {
            style: 'text-align: center; margin-top: 3px;',
            id: "cell-loader",
            html: "<span class='fa fa-spinner fa-pulse fa-2x'></span>"
        });

        return $('<div>').append(attributesPanel).append(loaderObject);
    }

    // function generate_dtol_stage(stage) {
    //     $('#custom-renderer_' + stage.ref).find(".stage-content").html('');
    //     var formValue = stage.data;
    //
    //     var stagearea = $('#custom-renderer_' + stage.ref).find("form")
    //
    //     // firstly add a dropdown to select type of dtol sample
    //     var label = '<label for="dtol_type_select">Select Sample Sub Type</label>'
    //     var dd = $("<select/>", {
    //         id: "dtol_type_select",
    //         class: "form-control",
    //         "style": "margin-bottom:30px"
    //     })
    //     // the values of these options point to json files in wizards/sample/dtol_manifests
    //     $(dd).append($("<option></option>"))
    //     $(dd).append($("<option value='dtol_aquatic'>aquatic</option>"))
    //     $(dd).append($("<option value='dtol_protist'>protist</option>"))
    //     $(dd).append($("<option value=''dtol_other'>other</option>"))
    //     $(stagearea).append(label).append(dd)
    //
    //     // get the fields into the right order according to the groupings in stage.field_groupings
    //     var grouped_fields = new Object()
    //     for (var group_idx in stage.field_groupings) {
    //         group = stage.field_groupings[group_idx]
    //         group_name = group.group_name
    //         var fieldset = new Array()
    //         for (var order_idx in group.fields) {
    //             order_name = group.fields[order_idx]
    //             //now look for order_name in stage.items
    //             for (field in stage.items) {
    //                 item = stage.items[field]
    //                 if (item.id == order_name) {
    //                     fieldset.push(item)
    //                 }
    //             }
    //         }
    //         grouped_fields[group_name] = fieldset
    //     }
    //     // grouped fields now contains all the fields required split into categories
    //     // each of these groups should be rendered as an accordion panel
    //     var accordion_head = '<div hidden class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">'
    //
    //
    //     for (var title in grouped_fields) {
    //         var header = '<hr/><div hidden class="panel panel-default" id="section_' + title.replace(" ", "_") + '">' +
    //             '<div class="panel-heading" role="tab" id="heading_' + title.replace(" ", "_") + '">' +
    //             '<h4 class="panel-title">' +
    //             '<a role="button" data-toggle="collapse" data-parent="#accordion" href="#' + title.replace(" ", "_") + '" aria-expanded="true" aria-controls="' + title.replace(" ", "_") + '">' + title + '</a></h4></div>'
    //         var body = '<div id="' + title.replace(" ", "_") + '" class="panel-collapse collapse" role="tabpanel" aria-labelledby="heading_"' + title.replace(" ", "_") + '>' +
    //             '<div class="panel-body">'
    //         for (var control in grouped_fields[title]) {
    //             var formElem = grouped_fields[title][control]
    //             var elemValue = null;
    //             if (formValue) {
    //                 var elem = formElem.id.split(".").slice(-1)[0];
    //                 if (formValue[elem]) {
    //                     elemValue = formValue[elem];
    //                 }
    //             }
    //             //set default values
    //             if (formElem.default_value) {
    //                 elemValue = formElem.default_value;
    //             } else {
    //                 elemValue = "";
    //             }
    //             var htmlCtrl = dispatchFormControl[controlsMapping[formElem.control.toLowerCase()]](formElem, elemValue);
    //             body = body + $(htmlCtrl).prop('outerHTML')
    //         }
    //         body = body + '</div></div></div>'
    //         var content = header + body
    //         accordion_head = accordion_head + content
    //     }
    //     $(accordion_head).appendTo(stagearea);
    //     refresh_accessions_tool_tips();
    // }

    // function generate_sample_edit_table(stage) {
    //     //function provides stage information for sample attribute editing
    //     var btnNext = $(".btn-next");
    //     btnNext.addClass("loading");
    //     btnNext.prop('disabled', true);
    //
    //     var tableID = stage.ref + "_table";
    //     var stageHTML = $('<div/>', {"class": "alert alert-default"});
    //
    //
    //     var messageDiv = $('<a/>',
    //         {
    //             html: '<i class="fa fa-2x fa-info-circle text-info"></i><span class="action-label" style="padding-left: 8px;">Attributes editing tips...</span>',
    //             class: "text-info",
    //             style: "line-height: 150%; display:none;",
    //             href: "#attributes-edit",
    //             "data-toggle": "collapse"
    //         });
    //
    //     //add info for user
    //     var message = $('<div/>', {class: "webpop-content-div"});
    //     message.append(stage.message);
    //
    //     var panel = get_panel('info');
    //     panel.addClass('edit-sample-badge');
    //     panel.find('.panel-body').append(message);
    //     panel.find('.panel-heading').remove();
    //     panel.find(".panel-footer").remove();
    //
    //     var messageDivContent = $('<div/>',
    //         {
    //             class: "collapse",
    //             id: "attributes-edit"
    //         }
    //     );
    //
    //     messageDivContent.append(panel);
    //
    //
    //     // refresh dynamic content
    //     $('#custom-renderer_' + stage.ref).find(".stage-content").html('');
    //     $('#custom-renderer_' + stage.ref).find(".stage-content").append(stageHTML);
    //
    //     stageHTML.append($('<div/>', {style: "margin-bottom: 10px;"}).append(messageDiv));
    //     stageHTML.append(messageDivContent);
    //
    //     //table element
    //     var tableDiv = $('<div/>');
    //     stageHTML.append(tableDiv);
    //
    //     var tbl = $('<table/>',
    //         {
    //             id: tableID,
    //             "class": "ui celled table hover copo-noborders-table",
    //             cellspacing: "0",
    //             width: "100%"
    //         });
    //
    //     tableDiv.append(tbl);
    //
    //     //loader element
    //     var loaderHTML = $('<div/>');
    //     var loaderMessage = $('<div/>', {
    //         class: "text-primary",
    //         style: "margin-top: 5px; font-weight:bold;",
    //         html: "Generating samples..."
    //     });
    //
    //     loaderHTML.append(loaderMessage);
    //     loaderHTML.append(get_spinner_image());
    //     stageHTML.append(loaderHTML);
    //
    //     $.ajax({
    //         url: wizardURL,
    //         type: "POST",
    //         headers: {
    //             'X-CSRFToken': csrftoken
    //         },
    //         data: {
    //             'request_action': "get_discrete_attributes",
    //             'description_token': sampleDescriptionToken
    //
    //         },
    //         success: function (data) {
    //             loaderHTML.remove();
    //             messageDiv.show();
    //
    //             dtColumns = data.table_data.columns;
    //             dtRows = data.table_data.rows;
    //
    //             var table = $('#' + tableID).DataTable({
    //                 data: dtRows,
    //                 dom: 'Bfr<"row"><"row info-rw" i>tlp',
    //                 "bSortClasses": false,
    //                 searchHighlight: true,
    //                 lengthChange: true,
    //                 "lengthMenu": [100000],
    //                 select: {
    //                     style: 'os',
    //                     selector: 'td:first-child'
    //                 },
    //                 order: [[0, 'asc']],
    //                 buttons: [
    //                     'selectAll',
    //                     {
    //                         text: 'Select filtered',
    //                         action: function (e, dt, node, config) {
    //                             var filteredRows = dt.rows({order: 'index', search: 'applied'});
    //                             if (filteredRows.count() > 0) {
    //                                 dt.rows().deselect();
    //                                 filteredRows.select();
    //                             }
    //                         }
    //                     },
    //                     'selectNone',
    //                     {
    //                         extend: 'csv',
    //                         text: 'Export CSV',
    //                         title: null,
    //                         filename: "copo_samples_" + get_timestamp()
    //                     }
    //                 ],
    //                 language: {
    //                     "info": " _START_ to _END_ of _TOTAL_ samples",
    //                     buttons: {
    //                         selectAll: "Select all",
    //                         selectNone: "Select none",
    //                     },
    //                     select: {
    //                         rows: {
    //                             _: "%d selected records can be <strong>batch-updated using focused cell value</strong><span class='focused-table-info'></span>",
    //                             0: "<span>Select one or more records to batch-update</span><span class='focused-table-info'></span>",
    //                             1: "%d selected record can be updated using focused cell value<span class='focused-table-info'></span>"
    //                         }
    //                     }
    //                 },
    //                 keys: {
    //                     columns: ':not(:first-child)',
    //                     focus: ':eq(1)', // cell that will receive focus when the table is initialised, set to the first editable cell defined
    //                     keys: [9, 13, 37, 39, 38, 40],
    //                     blurable: false
    //                 },
    //                 scrollX: true,
    //                 // scroller: true,
    //                 // scrollY: 300,
    //                 columns: dtColumns
    //             });
    //
    //             sampleTableInstance = table;
    //
    //             table
    //                 .buttons()
    //                 .nodes()
    //                 .each(function (value) {
    //                     $(this)
    //                         .removeClass("btn btn-default")
    //                         .addClass('tiny ui basic button');
    //                 });
    //
    //             //add custom buttons
    //
    //             var customButtons = $('<span/>', {
    //                 style: "padding-left: 15px;",
    //                 class: "copo-table-cbuttons"
    //             });
    //
    //
    //             $(table.buttons().container()).append(customButtons);
    //
    //             //apply to selected rows button
    //             var applyButton = $('<button/>',
    //                 {
    //                     class: "tiny ui basic primary button",
    //                     id: "updating_cell_button",
    //                     type: "button",
    //                     html: '<span>Update selected records</span>',
    //                     click: function (event) {
    //                         event.preventDefault();
    //
    //                         if (!$(this).hasClass('updating')) {
    //                             $(this).addClass('updating');
    //                             batch_update_records(table);
    //                         }
    //                     }
    //                 });
    //
    //
    //             customButtons.append(applyButton);
    //
    //             var applyCsvButton = $('<button/>',
    //                 {
    //                     class: "tiny ui basic primary button",
    //                     id: "updating_column_button",
    //                     type: "button",
    //                     html: '<span>Update column from CSV</span>',
    //                     click: function (event) {
    //                         event.preventDefault();
    //
    //                         handle_csv_button_click(table)
    //                     }
    //                 });
    //             customButtons.append(applyCsvButton);
    //
    //             refresh_accessions_tool_tips();
    //
    //             //add event for enter key press and cell double-click
    //             table
    //                 .on('dblclick', 'td', function () {
    //                     var cell = table.cell($(this));
    //                     manage_cell_edit(table, cell);
    //                 });
    //
    //             table
    //                 .on('key', function (e, datatable, key, cell, originalEvent) {
    //                     if (key === 13) {//trap enter key for editing a cell
    //                         manage_cell_edit(table, cell);
    //                     }
    //                 });
    //
    //             //add event for cell focus
    //             table
    //                 .on('key-focus', function (e, datatable, cell, originalEvent) {
    //                     var rowIndx = cell.index().row + 1;
    //                     $('.focused-table-info').html($('<span style="margin-left: 5px; padding: 5px; font-size: 14px;"> Focused cell in row ' + rowIndx + '</span>'));
    //                 })
    //                 .on('key-blur', function (e, datatable, cell) {
    //                     //;
    //                 });
    //
    //             //add event for column highlighting and tooltip
    //             $('#' + tableID + ' tbody')
    //                 .on('mouseenter', 'td', function () {
    //                     var colIdx = table.cell(this).index().column;
    //
    //                     $(this).prop("title", "[" + dtRows[table.cell(this).index().row].name + ", " + dtColumns[colIdx].title + "" + "]");
    //
    //                     $(table.cells().nodes()).removeClass('copo-higlighted-column');
    //                     $(table.column(colIdx).nodes()).addClass('copo-higlighted-column');
    //                 });
    //
    //
    //             btnNext.removeClass("loading");
    //             btnNext.prop('disabled', false);
    //         },
    //         error: function () {
    //             alert("Couldn't generate samples!");
    //         }
    //     });
    // }
    //
    //
    // function batch_update_records(table) {
    //     //function uses value from focused cell to update selected records
    //     var cells = table.cells('.focus');
    //     var cell = null;
    //
    //     //get referenced cell
    //     if (cells && cells[0].length > 0) {
    //         cell = cells[0];
    //         cell = table.cell(cell[0].row, cell[0].column);
    //     } else {
    //         $("#updating_cell_button").removeClass('updating');
    //         return false;
    //     }
    //
    //     //var node = cell.node();
    //
    //     //get record id of target cell
    //     var recordID = table.row(cell.index().row).id().split("row_")[1];
    //
    //     //get selected rows ids for batch update
    //     var target_rows = table.rows('.selected').ids().toArray();
    //
    //
    //     if (target_rows.length == 0) {
    //         BootstrapDialog.show({
    //             title: "Batch update action",
    //             message: "Select one or more records to update corresponding cells",
    //             cssClass: 'copo-modal3',
    //             closable: false,
    //             animate: true,
    //             type: BootstrapDialog.TYPE_WARNING,
    //             buttons: [{
    //                 label: 'OK',
    //                 cssClass: 'tiny ui basic orange button',
    //                 action: function (dialogRef) {
    //                     dialogRef.close();
    //                     $("#updating_cell_button").removeClass('updating');
    //                     return false;
    //                 }
    //             }]
    //         });
    //
    //         $("#updating_cell_button").removeClass('updating');
    //         return false;
    //     }
    //
    //     //ask user confirmation
    //     if (target_rows.length > 0) {
    //         BootstrapDialog.show({
    //             title: "Confirm batch update",
    //             message: "Corresponding cells in column <span style='color: #ff0000;'>" + dtColumns[cell.index().column].title + "</span> for the selected records will be assigned the value: <span style='color: #ff0000;'>" + dtRows[cell.index().row][dtColumns[cell.index().column].data] + "</span>.<div style='margin-top: 10px;'>Do you want to continue?</div>",
    //             // cssClass: 'copo-modal3',
    //             closable: false,
    //             animate: true,
    //             type: BootstrapDialog.TYPE_WARNING,
    //             buttons: [
    //                 {
    //                     label: 'Cancel',
    //                     cssClass: 'tiny ui basic button',
    //                     action: function (dialogRef) {
    //                         table.rows().deselect();
    //                         $("#updating_cell_button").removeClass('updating');
    //                         dialogRef.close();
    //                         return false;
    //                     }
    //                 },
    //                 {
    //                     label: 'Continue',
    //                     cssClass: 'tiny ui basic orange button',
    //                     action: function (dialogRef) {
    //                         dialogRef.close();
    //
    //                         //disable table navigation keys
    //                         table.keys.disable();
    //
    //                         var loaderObject = $('<div>', {
    //                             style: 'text-align: center; margin-top: 3px;',
    //                             html: "<span class='fa fa-spinner fa-pulse fa-2x'></span>"
    //                         });
    //
    //                         $("#updating_cell_button").html("");
    //                         $("#updating_cell_button").append("<span>Updating records, please wait</span>");
    //                         $("#updating_cell_button").append(loaderObject);
    //
    //
    //                         $.ajax({
    //                             url: wizardURL,
    //                             type: "POST",
    //                             headers: {
    //                                 'X-CSRFToken': csrftoken
    //                             },
    //                             data: {
    //                                 'request_action': "batch_update",
    //                                 'cell_reference': dtColumns[cell.index().column].data,
    //                                 'target_id': recordID,
    //                                 'target_rows': JSON.stringify(target_rows),
    //                                 'description_token': sampleDescriptionToken
    //
    //                             },
    //                             success: function (data) {
    //                                 if (data.batch_update) {
    //                                     if (data.batch_update.status == "success") {
    //                                         if (data.batch_update.data_set) {
    //                                             dtRows = data.batch_update.data_set;
    //
    //                                             table.rows().deselect();
    //
    //                                             table
    //                                                 .clear()
    //                                                 .draw();
    //                                             table
    //                                                 .rows
    //                                                 .add(dtRows);
    //                                             table
    //                                                 .columns
    //                                                 .adjust()
    //                                                 .draw();
    //                                             table
    //                                                 .search('')
    //                                                 .columns()
    //                                                 .search('')
    //                                                 .draw();
    //                                         } else {
    //                                             //get selected rows indexes for batch update
    //
    //                                             var rowIndexes = table.rows('.selected').indexes().toArray(); //get selected rows index
    //
    //                                             var cellNodes = table.cells(rowIndexes, cell.index().column).nodes(); //get target cells node
    //                                             $(cellNodes).html(data.batch_update.value); //batch update cells display with new value
    //
    //                                             var col = dtColumns[cell.index().column].data; //get target column
    //
    //                                             for (var i = 0; i < rowIndexes.length; ++i) { //update data-source
    //                                                 dtRows[rowIndexes[i]][col] = data.batch_update.value;
    //                                             }
    //
    //                                             table.rows().deselect();
    //
    //                                             table
    //                                                 .rows()
    //                                                 .invalidate()
    //                                                 .draw();
    //
    //                                             //refresh search box
    //                                             table
    //                                                 .search('')
    //                                                 .draw();
    //                                         }
    //
    //                                         table.cell(cell.index().row, cell.index().column).focus();
    //
    //                                     } else {
    //                                         alert(data.batch_update.message);
    //                                     }
    //
    //                                     table.keys.enable();
    //
    //                                     $("#updating_cell_button").html("");
    //                                     $("#updating_cell_button").append("<span>Update selected records</span>");
    //
    //                                 }
    //
    //                                 $("#updating_cell_button").removeClass('updating');
    //                             },
    //                             error: function () {
    //                                 alert("Batch update error!");
    //                                 table.keys.enable();
    //
    //                                 $("#updating_cell_button").html("");
    //                                 $("#updating_cell_button").append("<span>Update selected records</span>");
    //                                 $("#updating_cell_button").removeClass('updating');
    //                             }
    //                         });
    //                     }
    //                 }
    //             ]
    //         });
    //     }
    // }
    //
    // function finalise_description() {
    //     const $dialogContent = $('<div/>');
    //     const notice_div = $('<div/>').html("Finalising description...");
    //     const spinner_div = $('<div/>', {style: "margin-left: 40%; padding-top: 15px; padding-bottom: 15px;"}).append($('<div class="copo-i-loader"></div>'));
    //
    //     const dialog = new BootstrapDialog({
    //         type: BootstrapDialog.TYPE_PRIMARY,
    //         size: BootstrapDialog.SIZE_NORMAL,
    //         title: function () {
    //             return $('<span>Sample description</span>');
    //         },
    //         closable: false,
    //         animate: true,
    //         draggable: false,
    //         onhide: function (dialogRef) {
    //             //nothing to do for now
    //         },
    //         onshown: function (dialogRef) {
    //             $.ajax({
    //                 url: wizardURL,
    //                 type: "POST",
    //                 headers: {
    //                     'X-CSRFToken': csrftoken
    //                 },
    //                 data: {
    //                     'request_action': "finalise_description",
    //                     'description_token': sampleDescriptionToken
    //
    //                 },
    //                 success: function (data) {
    //                     if (data.finalise_result.status === 'success') {
    //                         window.location.reload();
    //                     } else {
    //                         var $feeback = $('<div/>', {
    //                             "class": "webpop-content-div",
    //                             style: "padding-bottom: 15px;"
    //                         }).html("The following error was encountered while finalising description! Please click the review button to effect changes.");
    //                         var $button = $('<div class="tiny ui red button">Review description</div>');
    //                         $button.on('click', {dialogRef: dialogRef}, function (event) {
    //                             event.data.dialogRef.close();
    //                         });
    //
    //                         dialog.setType(BootstrapDialog.TYPE_DANGER);
    //                         dialog.getModalBody().html('').append($feeback).append($button);
    //                     }
    //
    //                 },
    //                 error: function () {
    //                     alert("Error finalising description!");
    //                 }
    //             });
    //         },
    //         buttons: []
    //     });
    //
    //
    //     $dialogContent.append(notice_div).append(spinner_div);
    //     dialog.realize();
    //     dialog.setMessage($dialogContent);
    //     dialog.open();
    // }

    // function pending_sample_description() {
    //     $.ajax({
    //         url: wizardURL,
    //         type: "POST",
    //         headers: {
    //             'X-CSRFToken': csrftoken
    //         },
    //         data: {
    //             'request_action': "pending_description",
    //             'profile_id': $('#profile_id').val()
    //         },
    //         success: function (data) {
    //             if (data.pending.length) {
    //                 const infoPanelElement = trigger_global_notification();
    //
    //                 for (let i = 0; i < data.pending.length; ++i) {
    //                     const rec = data.pending[i];
    //                     const message = $('<div/>', {class: "webpop-content-div"});
    //                     message.append("<span>Modified on: </span>");
    //                     message.append(rec.created_on);
    //                     message.append("<div></div>");
    //                     message.append("<span>Number of samples: </span>");
    //                     message.append(rec.number_of_samples);
    //                     message.append("<div></div>");
    //                     message.append("<span>Last visited stage: </span>");
    //                     message.append(rec.last_rendered_stage);
    //                     message.append("<div style='margin-top: 5px;'></div>");
    //                     message.append("<div style='margin-top: 5px;'></div>");
    //
    //                     const deletedesc = '<a class="delete-description-i pull-right" href="#" role="button" ' +
    //                         'style="text-decoration: none; color:  #c93c00;" data-target="' + rec._id + '" title="delete description" aria-haspopup="true" aria-expanded="false">' +
    //                         '<i class="fa fa-times-circle" aria-hidden="true">' +
    //                         '</i>&nbsp; Delete</a>';
    //
    //                     const reloaddesc = '<a class="reload-description-i" href="#" role="button" ' +
    //                         'style="text-decoration: none; color: #35637e;" data-target="' + rec._id + '" title="reload description" aria-haspopup="true" aria-expanded="false">' +
    //                         '<i class="fa fa-refresh" aria-hidden="true">' +
    //                         '</i>&nbsp; Reload</a>';
    //
    //
    //                     const panel = get_panel('info');
    //                     panel.addClass('inc-desc-badge');
    //                     panel.find('.panel-body').append(message);
    //                     panel.find('.panel-footer').append(deletedesc);
    //                     panel.find('.panel-footer').append(reloaddesc);
    //                     panel.find('.panel-heading').append('Incomplete description');
    //
    //                     infoPanelElement.prepend(panel);
    //                 }
    //             }
    //         },
    //         error: function () {
    //             console.log("Couldn't complete request for pending description");
    //         }
    //     });
    // }

    // function delete_incomplete_description(elem, description_token) {
    //     $.ajax({
    //         url: wizardURL,
    //         type: "POST",
    //         headers: {
    //             'X-CSRFToken': csrftoken
    //         },
    //         data: {
    //             'request_action': "delete_pending_description",
    //             'description_token': description_token
    //         },
    //         success: function (data) {
    //             elem.closest(".inc-desc-badge").remove();
    //         },
    //         error: function () {
    //             console.log("Couldn't complete request for deleting description");
    //         }
    //     });
    // }


    function trigger_csv_upload() {
        //function handles upload of description csv file

        const message = $('<div/>', {class: "webpop-content-div upload-modal"});
        const feedbackRow = $('<div class="row feedbackrow"><div class="col-sm-12 feedbackcol"></div></div>');
        message.append(feedbackRow);

        return new BootstrapDialog({
            title: "Metadata Ingestion",
            message: message,
            closable: false,
            animate: true,
            type: BootstrapDialog.TYPE_INFO,
            size: BootstrapDialog.SIZE_NORMAL,
            buttons: [
                {
                    id: 'btn-cancel-process',
                    label: 'Cancel',
                    cssClass: 'tiny ui basic button',
                    action: function (dialogRef) {
                        dialogRef.close();
                    }
                }
            ]
        });
    }

    let profile_type = $("#profile_type").val()
    if (!profile_type.includes("Stand-alone")) {
        $("#edit_button").hide()
    }


}); //end document ready


//_________________________________________________
// Handlers
// Set COPO frontpage properties in this dictionary
function get_component_meta(component) {
    let componentMeta = null;
    const components = get_copo_accessions_components();

    components.forEach(function (comp) {
        if (comp.component === component) {
            componentMeta = comp;
            return false;
        }
    });

    return componentMeta
}

function get_copo_accessions_components() {
    return [
        {
            component: 'profile',
            title: 'Work Profiles',
            buttons: ["quick-tour-template", "new-component-template"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
            tableID: 'copo_profiles_table',
            secondaryTableID: 'copo_shared_profiles_table',
            visibleColumns: 4,
            recordActions: ["add_record_all", "edit_record_single", "delete_record_multi"] //specifies action buttons for records manipulation
        },
        {
            component: 'sample',
            title: 'Samples',
            iconClass: "fa fa-filter",
            semanticIcon: "filter", //semantic UI equivalence of fontawesome icon
            countsKey: "num_sample",
            buttons: ["quick-tour-template", "new-samples-template", "new-samples-spreadsheet-template", "new-samples-spreadsheet-template-erga", "accept_reject_samples", "tol_inspect"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
            colorClass: "samples_color",
            color: "olive",
            profile_component: true,
            tableID: 'sample_table',
            recordActions: ["show_sample_source", "describe_record_all", "edit_record_single"],
            visibleColumns: 3 //no of columns to be displayed, if tabular data is required. remaining columns will be displayed in a sub-table
        },
        {
            component: 'accessions',
            title: 'Accessions',
            iconClass: "fa fa-barcode",
            semanticIcon: "barcode", //semantic UI equivalence of fontawesome icon
            countsKey: "num_accessions",
            buttons: ["copo_accessions", "tol_inspect", "accept_reject_samples"],
            sidebarPanels: ["copo-sidebar-info"],
            colorClass: "accessions_color",
            color: "pink",
            profile_component: true,
            tableID: 'accessions_table',
            recordActions: ["btn-toggle1", "btn-toggle2"],
            visibleColumns: 3 //no of columns to be displayed, if tabular data is required. remaining columns will be displayed in a sub-table
        },
        {
            component: 'datafile',
            title: 'Datafiles',
            iconClass: "fa fa-database",
            semanticIcon: "database",
            countsKey: "num_data",
            colorClass: "data_color",
            color: "black",
            buttons: ["quick-tour-template"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
            tableID: 'datafile_table',
            profile_component: true,
            // recordActions: ["describe_record_multi", "unbundle_record_multi", "undescribe_record_multi"],
            recordActions: [],
            visibleColumns: 3
        },
        {
            component: 'submission',
            title: 'Submissions',
            iconClass: "fa fa-envelope",
            semanticIcon: "mail outline",
            countsKey: "num_submission",
            buttons: ["quick-tour-template"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
            colorClass: "submissions_color",
            color: "green",
            tableID: 'submission_table',
            profile_component: true,
            recordActions: [],
            visibleColumns: 3
        },
        {
            component: 'publication',
            title: 'Publications',
            iconClass: "fa fa-paperclip",
            semanticIcon: "attach",
            countsKey: "num_pub",
            buttons: ["quick-tour-template", "new-component-template"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
            colorClass: "pubs_color",
            color: "orange",
            tableID: 'publication_table',
            profile_component: true,
            recordActions: ["add_record_all", "edit_record_single", "delete_record_multi"],
            visibleColumns: 4
        },
        {
            component: 'metadata_template',
            title: 'Metadata Template',
            iconClass: "fa fa-table",
            semanticIcon: "attach",
            countsKey: "num_temp",
            buttons: ["quick-tour-template", "new-component-template"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
            colorClass: "pubs_color",
            color: "blue",
            tableID: 'metadata_template_table',
            recordActions: ["add_record_all", "edit_record_single", "delete_record_multi"],
            visibleColumns: 4
        },
        {
            component: 'person',
            title: 'People',
            iconClass: "fa fa-users",
            semanticIcon: "users",
            countsKey: "num_person",
            buttons: ["quick-tour-template", "new-component-template"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help"],
            colorClass: "people_color",
            color: "red",
            tableID: 'person_table',
            profile_component: true,
            recordActions: ["add_record_all", "edit_record_single"],
            visibleColumns: 5
        },/*
        {
            component: 'annotation',
            title: 'Generic Annotations',
            iconClass: "fa fa-pencil",
            semanticIcon: "write",
            countsKey: "num_annotation",
            buttons: ["quick-tour-template"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help", "copo-sidebar-annotate"],
            colorClass: "annotations_color",
            color: "violet",
            tableID: 'annotation_table',
            recordActions: ["delete_record_multi"],
            visibleColumns: 10000
        }, TODO - these need to be reactivated in the future sometime
        {
            component: 'repository',
            title: 'Repositories',
            iconClass: "fa fa-pencil",
            semanticIcon: "write",
            countsKey: "num_annotation",
            buttons: ["quick-tour-template", "new-component-template"],
            sidebarPanels: ["copo-sidebar-info", "copo-sidebar-help", "copo-sidebar-annotate"],
            colorClass: "annotations_color",
            color: "violet",
            tableID: 'repository_table',
            recordActions: ["delete_record_multi"],
            visibleColumns: 10000
        }*/
    ];
}

function set_empty_accessions_component_message(dataRows, table_id = "*") {
    //decides, based on presence of record, to display table or getting started info

    if (dataRows === 0) {
        if ($(".table-parent-div").length) {
            $(table_id).find(".table-parent-div").hide();
            $("#wizard_submissions_label").hide()
            $("#manifest_submissions_label").hide()
        }

        if ($(".page-welcome-message").length) {
            $(table_id).find(".page-welcome-message").show();
        }

    } else {
        if ($(".table-parent-div").length) {
            $(table_id).find(".table-parent-div").show();
            $("#wizard_submissions_label").show()
            $("#manifest_submissions_label").show()
        }

        if ($(".page-welcome-message").length) {
            $(table_id).find(".page-welcome-message").hide();
        }
    }
}

function button_event_alert(message) {
    BootstrapDialog.show({
        title: "Record action",
        message: message,
        cssClass: 'copo-modal3',
        closable: false,
        animate: true,
        type: BootstrapDialog.TYPE_WARNING,
        buttons: [{
            label: 'OK',
            cssClass: 'tiny ui basic orange button',
            action: function (dialogRef) {
                dialogRef.close();
            }
        }]
    });
}

function do_table_buttons_events() {
    //attaches events to table buttons

    $(document).on("click", ".copo-dt", function (event) {
        event.preventDefault();

        $('.copo-dt').webuiPopover('destroy');


        var elem = $(this);
        var task = elem.attr('data-action').toLowerCase(); //action to be performed e.g., 'Edit', 'Delete'
        var tableID = elem.attr('data-table'); //get target table
        var btntype = elem.attr('data-btntype'); //type of button: single, multi, all
        var title = elem.find(".action-label").html();
        var message = elem.attr("data-error-message");

        if (!message) {
            message = "No records selected for " + title + " action";
        }

        //validate event before passing to handler
        var table = $('#' + tableID).DataTable();
        var selectedRows = table.rows({
            selected: true
        }).count(); //number of rows selected

        var triggerEvent = true;

        //do button type validation based on the number of records selected
        if (btntype == "single" || btntype == "multi") {
            if (selectedRows == 0) {
                triggerEvent = false;
            } else if (selectedRows > 1 && btntype == "single") { //sort out 'single record buttons'
                triggerEvent = false;
            }
        }

        if (triggerEvent) { //trigger button event, else deal with error
            var event = jQuery.Event("addbuttonevents");
            event.tableID = tableID;
            event.task = task;
            event.title = title;
            $('body').trigger(event);
        } else {
            //alert user
            button_event_alert(message);
        }

    });
}

function place_accessions_task_buttons(componentMeta) {
    let class_name = $(document).data("showAllCOPOAccessions") ? "btn-toggle2" : "btn-toggle1";
    //place custom buttons on table

    if (!componentMeta.recordActions.length) {
        return;
    }

    const table = $('#' + componentMeta.tableID).DataTable();

    const customButtons = $('<span/>', {
        style: "padding-left: 15px;",
        class: "copo-table-cbuttons"
    });

    if (class_name === "btn-toggle1") {
        $(table.buttons().container()).append(customButtons);
    }

    if (class_name === "btn-toggle2") {
        $(table.buttons().container()).append(customButtons);
    }

    const actionBTN = $(".accessions-record-action-templates").find("." + class_name).clone();

    actionBTN.attr("data-table", componentMeta.tableID);
    customButtons.append(actionBTN);

    if (!$(document).data("showAllCOPOAccessions")) {
        // Truncate profile title if it is too long
        let profile_title = $("#profile_title")
        let truncated_profile_title = profile_title.val().length > 10 ?
            jQuery.trim(profile_title.val()).substring(0, 10).trim(this) + '...'
            : profile_title.val()

        // Add profile title to the active toggle button
        $(".btn-toggle1").find(".btn-success").text(`View Profile: ${truncated_profile_title} Accessions`)
    }

    refresh_accessions_tool_tips();

    //table action buttons
    do_table_buttons_events();
}

function render_accessions_table(data, cols, dataSet, componentMeta) {
    const tableID = componentMeta.tableID;
    //set data
    let table = null;

    if ($.fn.dataTable.isDataTable('#' + tableID)) {
        //if table instance already exists, then do refresh
        table = $('#' + tableID).DataTable();
    }

    if (table) {
        //clear old, set new data
        table.rows().deselect();
        table
            .clear()
            .draw();
        table
            .rows
            .add(dataSet);
        table
            .columns
            .adjust()
            .draw();
        table
            .search('')
            .columns()
            .search('')
            .draw();
    } else {
        table = $('#' + tableID).DataTable({
            data: dataSet,
            select: false,
            searchHighlight: true,
            // fixedHeader: true,
            ordering: true,
            lengthChange: true,
            scrollX: true,
            scrollY: 350,
            buttons: [
                {
                    extend: 'csv',
                    text: 'Export CSV',
                    title: null,
                    filename: "copo_" + String(tableID) + "_data"
                },
            ],
            language: {
                "info": "Showing _START_ to _END_ of _TOTAL_ records",
                "search": " ",
                "lengthMenu": "show _MENU_ records",
                select: {
                    rows: {
                        _: "%d records selected",
                        0: "<span class='extra-table-info'>Click <span class='fa-stack' style='color:green; font-size:10px;'><i class='fa fa-circle fa-stack-2x'></i><i class='fa fa-plus fa-stack-1x fa-inverse'></i></span> beside a record to view extra details</span>",
                        1: "%d record selected"
                    }
                },
                buttons: {}
            },
            order: [[1, 'asc']],

            fnDrawCallback: function () {
                refresh_accessions_tool_tips();
                const event = jQuery.Event("posttablerefresh"); //individual compnents can trap and handle this event as they so wish
                $('body').trigger(event);
            },
            columns: cols,

            "columnDefs": [
                {
                    "targets": "_all", // all fields
                    "createdCell": function (td, cellData, rowData, row, col) {
                        if (cellData === "") {
                            $(td).addClass("cell-no-content")
                        }
                    }
                },
                {
                    'targets': [3, 5], // 'biosampleAccession' column & 'sraAccession' column respectively
                    'render': function (data, type, full, meta) {
                        let ebi_url = `https://www.ebi.ac.uk/ena/browser/view/${data}`
                        return '<a class="no-underline" href="' + ebi_url + '"  target="_blank">' + data + '</a>';
                    }
                },
                {
                    'targets': [4], // 'manifest_id' column
                    'render': function (data, type, full, meta) {
                        let get_samples_by_manifestID_url = `/api/manifest/${data}`
                        return '<a class="no-underline" href="' + get_samples_by_manifestID_url + '"  target="_blank">' + data + '</a>';
                    }
                }
            ],

            createdRow: function (row, data, index) {
                //add class to row for ease of selection later
                let recordId = index;
                try {
                    recordId = data.record_id;
                } catch (err) {
                }

                $(row).addClass(tableID + recordId);
            },

            dom: 'Bfr<"row"><"row info-rw" i>tlp'
        });

        table
            .buttons()
            .nodes()
            .each(function (value) {
                $(this)
                    .removeClass("btn btn-default")
                    .addClass('tiny ui basic button');
            });

        place_accessions_task_buttons(componentMeta);
    }
    let table_wrapper = $('#' + tableID + '_wrapper')

    table_wrapper
        .find(".dataTables_filter")
        .find("label").css({"padding": "20px 0 20px 0", "margin-top": "10px"})
        .find("input")
        .removeClass("input-sm")
        .attr("placeholder", "Search " + componentMeta.title)
        .attr("size", 30);

    // Add css to align the buttons to the right
    table_wrapper.find(".dt-buttons").addClass("pull-right")
    table_wrapper.find('.info-rw').hide() // Hide showing 'x' of 'x' row

    // Insert breakpoints after the toggle button
    if ($(document).data("showAllCOPOAccessions")) {
        $("<br><br>").insertAfter(table_wrapper.find(".dt-buttons"))
    } else {
        const actionBTN2 = $(".accessions-record-action-templates").find("." + "groupBtn2").clone();
        table_wrapper.find(".dt-buttons").append($("<br><br>")).append(actionBTN2).append($("<br><br>"))
    }

    // Set height of table to fit the content in the table
    table_wrapper.find(".dataTables_scrollBody").css("height", "fit-content")

    // Add padding between table and show records filter
    table_wrapper.find(".dataTables_length").css("padding-top", "20px")

    //handle event for table details
    $('#' + tableID + ' tbody')
        .off('click', 'td.summary-details-control')
        .on('click', 'td.summary-details-control', function (event) {
            event.preventDefault();

            var event = jQuery.Event("posttablerefresh"); //individual compnents can trap and handle this event as they so wish
            $('body').trigger(event);

            var tr = $(this).closest('tr');
            var row = table.row(tr);
            tr.addClass('showing');

            if (row.child.isShown()) {
                // This row is already open - close it
                row.child('');
                row.child.hide();
                tr.removeClass('showing');
                tr.removeClass('shown');
            } else {
                $.ajax({
                    url: copoVisualsURL,
                    type: "POST",
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    data: {
                        'task': "attributes_display",
                        'component': componentMeta.component,
                        'target_id': row.data().record_id
                    },
                    success: function (data) {
                        if (data.component_attributes.columns) {
                            // expand row

                            var contentHtml = $('<table/>', {
                                // cellpadding: "5",
                                cellspacing: "0",
                                border: "0",
                                // style: "padding-left:50px;"
                            });

                            for (var i = 0; i < data.component_attributes.columns.length; ++i) {
                                var colVal = data.component_attributes.columns[i];

                                var colTR = $('<tr/>');
                                contentHtml.append(colTR);

                                colTR
                                    .append($('<td/>').append(colVal.title))
                                    .append($('<td/>').append(data.component_attributes.data_set[colVal.data]));

                            }

                            row.child($('<div></div>').append(contentHtml).html()).show();
                            tr.removeClass('showing');
                            tr.addClass('shown');
                        }
                    },
                    error: function () {
                        alert("Couldn't retrieve " + component + " attributes!");
                        return '';
                    }
                });
            }
        });

} //end of func

// function load_all_COPO_accessions_records(componentMeta, copoVisualsURL) {
//     let component_table_loder = $("#component_table_loader")
//     const csrftoken = $.cookie('csrftoken');
//
//     //loader
//     let tableLoader = null;
//
//     if (component_table_loder.length) {
//         tableLoader = $('<div class="copo-i-loader"></div>');
//         component_table_loder.append(tableLoader);
//     }
//
//     $.ajax({
//         url: copoVisualsURL,
//         type: "POST",
//         headers: {
//             'X-CSRFToken': csrftoken
//         },
//         data: {
//             "isSampleProfileTypeStandalone": false,
//             "isUserProfileActive": false,
//         },
//         dataType: "json",
//         success: function (data) {
//             let cols = [];
//             let dataSet = []
//
//             // Sort data by key
//             $.each(data, function (index, item) {
//                 // Remove "_id" from key-value pair from the original object
//                 if (item.hasOwnProperty("_id")) delete data[index]["_id"];
//
//                 // Sort element dictionary by key
//                 data[index] = Object.keys(data[index]).sort().reduce((a, c) => (a[c] = data[index][c], a), {})
//                 dataSet.push(Object.values(item))
//             });
//
//             // Get element keys
//             // If there exists at least one element, the keys will remain the same so just get the
//             // keys from the first element
//             Object.keys(data[0]).forEach(item => {
//                 cols.push({title: convertStringToTitleCase(item), value: item});
//             })
//
//             render_accessions_table(data, cols, dataSet, componentMeta);
//
//             //remove loader
//             if (tableLoader) tableLoader.remove();
//         },
//         error: function () {
//             alert("Couldn't retrieve " + componentMeta.component + " data!");
//         }
//     });
// }

function load_accessions_records(componentMeta, copoVisualsURL) {
    let component_table_loder = $("#component_table_loader")
    const csrftoken = $.cookie('csrftoken');
    let isSampleProfileTypeStandalone = $(document).data("showAllCOPOAccessions") ? false : $(document).data("isSampleProfileTypeStandalone")
    let isUserProfileActive = $(document).data("showAllCOPOAccessions") ? false : $(document).data("isUserProfileActive")

    //loader
    let tableLoader = null;

    if (component_table_loder.length) {
        tableLoader = $('<div class="copo-i-loader"></div>');
        component_table_loder.append(tableLoader);
    }

    $.ajax({
        url: copoVisualsURL,
        type: "POST",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            "isSampleProfileTypeStandalone": isSampleProfileTypeStandalone, //$(document).data("isSampleProfileTypeStandalone"),
            "isUserProfileActive": isUserProfileActive //$(document).data("isUserProfileActive")

        },
        dataType: "json",
        success: function (data) {

            let cols = [];
            let dataSet = []

            // Sort data by key
            $.each(data, function (index, item) {
                // Remove "_id" from key-value pair from the original object
                if (item.hasOwnProperty("_id")) delete data[index]["_id"];

                // Sort element dictionary by key
                data[index] = Object.keys(data[index]).sort().reduce((a, c) => (a[c] = data[index][c], a), {})
                dataSet.push(Object.values(item))
            });

            if ($(document).data("showAllCOPOAccessions")) {
                console.log("showAllCOPOAccessions is true")
                console.log("data", data)
                console.log("dataSet", dataSet)
                // load_accessions_records(componentMeta, copoVisualsURL)
                // Get element keys
                // If there exists at least one element, the keys will remain the same so just get the
                // keys from the first element
                Object.keys(data[0]).forEach(item => {
                    cols.push({title: convertStringToTitleCase(item), value: item});
                })

                render_accessions_table(data, cols, dataSet, componentMeta);

                //remove loader
                if (tableLoader) tableLoader.remove();

            } else {
                console.log("showAllCOPOAccessions is false")
                set_empty_accessions_component_message(dataSet.length); //display empty component message when there's no record

                if (dataSet.length === 0) {
                    if (tableLoader) tableLoader.remove(); //remove loader
                    $(".copo_accessions").show()
                    return false;
                } else {
                    // Get element keys
                    // If there exists at least one element, the keys will remain the same so just get the
                    // keys from the first element
                    Object.keys(data[0]).forEach(item => {
                        cols.push({title: convertStringToTitleCase(item), value: item});
                    })

                    render_accessions_table(data, cols, dataSet, componentMeta);

                    if (tableLoader) tableLoader.remove(); //remove loader
                }
            }


        },
        error: function () {
            alert("Couldn't retrieve " + componentMeta.component + " data!");
        }
    });
}

function refresh_accessions_tool_tips() {
    $("[data-toggle='tooltip']").tooltip();
    $("[data-toggle='popover']").popover();
    $('.ui.dropdown')
        .dropdown()
    ;
    $('.copo-tooltip')
        .popup()
    ;
    //
    // apply_color();
    // refresh_selectbox();
    // refresh_select2box();
    // refresh_multiselectbox();
    // refresh_multiselect2box();
    // refresh_singleselectbox();
    // refresh_multisearch();
    // refresh_ontology_select();
    // refresh_general_ontology_search();
    // refresh_general_ontology_select();
    // refresh_copo_lookup();
    // refresh_copo_lookup2();
    //
    // refresh_range_slider();
    // auto_complete();
    //
    // setup_datepicker();

} //end of func

function toggle_accessions_view() {
    const component = "accessions";
    const copoVisualsURL = "/copo/copo_accessions_visualise/";
    const componentMeta = get_component_meta(component);

    $('.btn-toggle').click(function () {
        $(this).find('.btn').toggleClass('active');

        if ($(this).find('.btn-primary').size() > 0) {
            $(this).find('.btn').toggleClass('btn-primary');
        }
        if ($(this).find('.btn-danger').size() > 0) {
            $(this).find('.btn').toggleClass('btn-danger');
        }
        if ($(this).find('.btn-success').size() > 0) {
            $(this).find('.btn').toggleClass('btn-success');
        }
        if ($(this).find('.btn-info').size() > 0) {
            $(this).find('.btn').toggleClass('btn-info');
        }

        $(this).find('.btn').toggleClass('btn-default');

        // Show all accessions
        if ($(this).find('.active').text().includes("All COPO Accessions")) {
            $(".page-title-custom").find("[title='Profile title']").hide() // Hide profile title
            $(document).data("isUserProfileActive", false)
            load_accessions_records(componentMeta, copoVisualsURL)

            // let copo_accessions_options = $(".dt-buttons ").clone()
            //
            // // Remove breakpoints before the toggle button
            // // copo_accessions_options.previousSibling.remove()
            // copo_accessions_options.prev("br").remove();
            // console.log("previousSibling: ", copo_accessions_options.prev())
            //
            // copo_accessions_options.find('.buttons-csv').remove()
            //
            // copo_accessions_options.insertBefore($(`#${componentMeta.tableID}_filter`))
            //     .find('.active').text('Other Projects\' Accessions')
            //
            // copo_accessions_options.find('.btn-default').text('Stand-alone Projects\' Accessions')
        } else {
            $(".page-title-custom").find("[title='Profile title']").show()
            $(document).data("isUserProfileActive", true)
            load_accessions_records(componentMeta, copoVisualsURL)
        }
    });
}

//builds component-page navbar
function do_page_controls(componentName) {
    let component = null;
    const components = get_copo_accessions_components();

    components.forEach(function (comp) {
        if (comp.component === componentName) {
            component = comp;
            return false;
        }
    });

    if (component == null) {
        return false;
    }

    generate_component_control(component);

} //end of func

function generate_component_control(component) {
    const pageHeaders = $(".copo-page-headers"); //page header/icons
    const pageIcons = $(".copo-page-icons"); //profile component icons
    const sideBar = $(".copo-sidebar"); //sidebar panels
    let profileTitleID = $("#profile_title") // profile title ID

    //add profile title
    if (profileTitleID.length) {
        const profileTitle = $('<div/>', {
            class: "page-title-custom",
            style: "margin-right:10px;",
            html: "<span title='Profile title' style='color: #8c8c8c; font-size: 18px;'>Profile: " + profileTitleID.val() + "</span>"
        });

        pageHeaders.append(profileTitle);
    }

    //add page title
    const PageTitle = $('<span/>', {
        class: "page-title-custom",
        style: "margin-right:10px;",
        html: component.title
    });

    pageHeaders.append(PageTitle);


    //create panels
    if (component.sidebarPanels) {
        const sidebarTemplate = $(".copo-sidebar-templates")
        const sidebarPanels = sidebarTemplate.clone();
        const sidebarPanels2 = sidebarPanels.clone();
        sidebarPanels.find(".nav-tabs").html('');
        sidebarPanels.find(".tab-content").html('');
        sidebarTemplate.remove();


        component.sidebarPanels.forEach(function (item) {
            sidebarPanels.find(".nav-tabs").append(sidebarPanels2.find(".nav-tabs").find("." + item));
            sidebarPanels.find(".tab-content").append(sidebarPanels2.find(".tab-content").find("." + item));
            // sidebarPanels.find(".profiles-legend").append(sidebarPanels2.find(".profiles-legend").find("." + item));
        });

        sideBar
            .append(sidebarPanels.find(".nav-tabs"))
            .append(sidebarPanels.find(".tab-content"))
        // .append(sidebarPanels.find(".profiles-legend"));


    }

    //create buttons
    const buttonsSpan = $('<span/>', {style: "white-space:nowrap;"});
    pageHeaders.append(buttonsSpan);
    component.buttons.forEach(function (item) {
        if (component.buttons) {
            component.buttons.forEach(function (item) {
                buttonsSpan.append($("." + item)).append("<span style='display: inline;'>&nbsp;</span>");
            });
        }
    });

    //...and profile component buttons
    if (component.hasOwnProperty("profile_component") && component.profile_component.toString() === "true") {
        const pcomponentHTML = $(".pcomponents-icons-templates").clone().removeClass("pcomponents-icons-templates");
        const pcomponentAnchor = pcomponentHTML.find(".pcomponents-anchor").clone().removeClass("pcomponents-anchor");
        pcomponentHTML.find(".pcomponents-anchor").remove();

        pageIcons.append(pcomponentHTML);

        const components = get_copo_accessions_components();

        for (let i = 1; i < components.length; ++i) {
            const comp = components[i];
            if (comp.hasOwnProperty("profile_component") && comp.profile_component.toString() === "true") {

                if ((comp.component === component.component)) {
                    continue;
                }

                const newAnchor = pcomponentAnchor.clone();
                pcomponentHTML.append(newAnchor);

                newAnchor.attr("title", "Navigate to " + comp.title);
                newAnchor.attr("href", $("#" + comp.component + "_url").val());
                newAnchor.find("i")
                    .addClass(comp.color)
                    .addClass(comp.semanticIcon);

            }
        }
    }

    //refresh components...
    // quick_tour_event();
    refresh_accessions_tool_tips();
}

//#------------- Helpers -----------------#
function convertStringToTitleCase(str) {
    return str.replace(
        /\w\S*/g,
        function (txt) {
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        }
    ).replace("_id", " ID")
        .replace("_name", " Name")
        .replace("accession", " Accession")
        .replace("Sra", "SRA")


}
