$(document).ready(function () {

    var uid = document.location.href
    uid = uid.split("/")
    uid = uid[uid.length - 2]
    var wsprotocol = 'ws://';
    var s3socket
 
    var dialog = new BootstrapDialog({
        title: "Add Sequence Annotation",
        message: "",
        /*
        onshown: function(dialogRef){
 
            $(".modal-dialog").find("#id_sample").off('change').on("change", (function(event){
                console.log("changed")
                event.preventDefault()
                //var $el =  $(".modal-dialog").find("#id_run");
                //$el.empty(); // remove old options
                //$el =  $(".modal-dialog").find("#id_experiment");
                //$el.empty(); // remove old options
                value = $(".modal-dialog").find("#id_sample").find(":selected").val()
                if (value == undefined || value === "") {
                  var $el =  $(".modal-dialog").find("#id_run");
                  $el.empty(); // remove old options
                  $el =  $(".modal-dialog").find("#id_experiment");
                  $el.empty(); // remove old options
                  return
                }   
        
                jQuery.ajax({
                    url: '/copo/copo_reads/' + value + "/get_read_accessions",
                    type: 'GET', // For jQuery < 1.9
                    headers:
                        {
                            "X-CSRFToken": csrftoken
                        },
                }).error(function (data) {
                    BootstrapDialog.show({
                        title: 'Error',
                        message: "Error " + data.responseText
                    });
                }).done(function (data) {
                    var $el =  $(".modal-dialog").find("#id_run");
                    run = $el.find(":selected").val()
                    $el.empty();
                    $.each(data["run_accessions"], function(index, value) {
                      $el.append($("<option></option>")
                         .attr("value", value)
                         .attr("selected", run!= undefined && run.includes(value)).text(value));
                    });
        
                    $el =  $(".modal-dialog").find("#id_experiment");
                    experiment = $el.find(":selected").val()
                    $el.empty(); // remove old options
                    $.each(data["experiment_accessions"], function(index, value) {
                      $el.append($("<option></option>")
                        .attr("value", value)
                        .attr("selected", experiment != undefined && experiment.includes(value)).text(value));
                    });  
        
                });
                
            }));
            
            selected_sample = $(".modal-dialog").find("#id_sample").find(":selected").val()
            if ( selected_sample == "") {
                var $el =  $(".modal-dialog").find("#id_run");
                $el.empty(); // remove old options
                $el =  $(".modal-dialog").find("#id_experiment");
                $el.empty(); // remove old options             
            } else {
                var event = jQuery.Event("change");
                $(".modal-dialog").find("#id_sample").val(selected_sample).trigger(event);
                console.log("triggered")
            }

        },
        */
        buttons: [{
            id: 'submit_annotation_button',
            label: 'Submit Annotation',
            cssClass: 'btn-primary',
            title: 'Submit Annotation',
            action: function(){
                doPost()
                var $button = this; // 'this' here is a jQuery object that wrapping the <button> DOM element.
                $button.disable();
                $button.spin();
                //dialog.setClosable(false);
            }
        }, {
            label: 'Close',
            action: function(dialogItself){
                dialogItself.close();
            }
        }]               
    });





    if (window.location.protocol === "https:") {
        wsprotocol = 'wss://';
    }
    var wsurl = wsprotocol + window.location.host + '/ws/annotation_status/' + uid

    s3socket = new WebSocket(wsurl);

    s3socket.onclose = function (e) {
        console.log("s3socket closing ", e)
    }
    s3socket.onopen = function (e) {
        console.log("s3socket opened ", e)
    }
    s3socket.onmessage = function (e) {
        d = JSON.parse(e.data)
        element = element = $("#" + d.html_id)
        if ($(".modal-dialog").is(':visible')) {
            elem = $(".modal-dialog").find("#" + d.html_id)
            if (elem) {
                element = elem
            }        
        }  

        if (!d && !$(element).is(":hidden")) {
            $(element).fadeOut("50")
        }
        else if (d && d.message && $(element).is(":hidden")) {
            $(element).fadeIn("50")
        }          
        //$("#" + d.html_id).html(d.message)
        if (d.action === "info") {
            // show something on the info div
            // check info div is visible
            $(element).removeClass("alert-danger").addClass("alert-info")
            $(element).html(d.message)
            if ("table_data" in d.data) {
                globalDataBuffer = d.data;
                var event = jQuery.Event("refreshtable");
                $('body').trigger(event);
            } 
            //$("#spinner").fadeOut()
        } else if (d.action === "error") {
            // check info div is visible
            $(element).removeClass("alert-info").addClass("alert-danger")
            $(element).html(d.message)
            //$("#spinner").fadeOut()
        } else if (d.action == "refresh_table") {
            //table data
            globalDataBuffer = d.data;
            var event = jQuery.Event("refreshtable");
            $('body').trigger(event);
        }
    }
    window.addEventListener("beforeunload", function (event) {
        s3socket.close()
    });



    function submit() {
        var csrftoken = $.cookie('csrftoken');
        var profile_id = $("#profile_id").val();
        
        var fieldset = $(".modal-dialog").find("#annotation_form input, textarea, select")
        const form = new FormData();
        var count = 0
        var files = []
        $(fieldset).each(function (idx, el) {
            if (el.type == "file") {
                form.append(el.name, el.files[0])
            } else if ($.isArray($(el).val())) {
                $(el).val().forEach(function (v) {
                    form.append(el.name, v)
                })
            } else if ($(el).val()) {
                form.append(el.name, $(el).val())
            }
        })
        id = $(".modal-dialog").find("#id_id")
        if (id != undefined) {
            form.append("seq_annotation_id", $(id).val())
        }
        $(".modal-dialog").find("input, textarea, select").prop("disabled", true)
    
    
        form.append("profile_id", profile_id)
        jQuery.ajax({
            url: '/copo/ena_annotation/' + profile_id,
            data: form,
            files: files,
            cache: false,
            contentType: false,
            processData: false,
            type: 'POST', // For jQuery < 1.9
            headers:
                {
                    "X-CSRFToken": csrftoken
                },
        }).error(function (data) {
            dialog.enableButtons(true);
            //dialog.setClosable(true);
            dialog.getButton('submit_annotation_button').stopSpin();
            $(".modal-dialog").find("#annotation_form input, textarea, select").prop("disabled", false)
            $(".modal-dialog").find("#id_study").prop("disabled", true)
            $(".modal-dialog").find("#loading_span").fadeOut()
            BootstrapDialog.show({
                title: 'Error',
                message: "Error " + data.responseText
            });
        }).done(function (data) {
            $(".modal-dialog").find("#submit_annotation_button").fadeOut()
            $(".modal-dialog").find("#annotation_form").hide()
            $(".modal-dialog").find("#loading_span").hide()
            dialog.close()
            var dict = {
                status: "success",
                message: data["success"]
              };          
            do_crud_action_feedback(dict);
            globalDataBuffer = data;
            if (data.hasOwnProperty  ("table_data")) {
                //table data
                var event = jQuery.Event("refreshtable");
                $('body').trigger(event);
            }
 
            //$("input").fadeOut()
            //$("select").fadeOut()
            //$("textarea").fadeOut()
            //
            console.log(data)
        })
    }
    
    
    function doPost() {
        var evt = window.event
        evt.preventDefault()
        submit()
    }
    
    
    //******************************Event Handlers Block*************************//
    var component = "seqannotation";
    var copoFormsURL = "/copo/copo_forms/";
    //var copoVisualsURL = "/copo/copo_visuals/";
    var csrftoken = $.cookie('csrftoken');

    //get component metadata
    var componentMeta = get_component_meta(component);

    load_records(componentMeta); // call to load component records

    //register_resolvers_event(); //register event for publication resolvers

    //instantiate/refresh tooltips
    refresh_tool_tips();

    //trigger refresh of table
    $('body').on('refreshtable', function (event) {
        do_render_component_table(globalDataBuffer, componentMeta);
    });

    //handle task button event
    $('body').on('addbuttonevents', function (event) {
        do_record_task(event);
    });

    //add new component button
    $(document).on("click", ".new-component-template", function (event) {
        url = "/copo/ena_annotation/"+uid 
        handle_add_n_edit(url)
    });

    //details button hover
    /*
    $(document).on("mouseover", ".detail-hover-message", function (event) {
        $(this).prop('title', 'Click to view ' + component + ' details');
    });
    */

    //******************************Functions Block******************************//

 
    function handle_add_n_edit(url) {
        dialog.realize();
        dialog.getButton('submit_annotation_button').disable();
        dialog.setMessage($('<div>Please wait...</div>').load(url, function (response, status, xhr) {

            if ( status == "error" ) {
                var msg = "Sorry but there was an error: ";
                dialog.setMessage($('<div>' + msg + xhr.status + " " + xhr.statusText + '</div>'));
                
            } else {
                dialog.getButton('submit_annotation_button').enable();
                $(".modal-dialog").find("#id_sample").off('change').on("change", (function(event){
                    console.log("changed")
                    event.preventDefault()

                    value = $(".modal-dialog").find("#id_sample").find(":selected").val()
                    if (value == undefined || value === "") {
                      var $el =  $(".modal-dialog").find("#id_run");
                      $el.empty(); // remove old options
                      $el =  $(".modal-dialog").find("#id_experiment");
                      $el.empty(); // remove old options
                      return
                    }   
            
                    jQuery.ajax({
                        url: '/copo/copo_reads/' + value + "/get_read_accessions",
                        type: 'GET', // For jQuery < 1.9
                        headers:
                            {
                                "X-CSRFToken": csrftoken
                            },
                    }).error(function (data) {
                        BootstrapDialog.show({
                            title: 'Error',
                            message: "Error " + data.responseText
                        });
                    }).done(function (data) {
                        var $el =  $(".modal-dialog").find("#id_run");
                        run = $el.find(":selected").val()
                        $el.empty();
                        $.each(data["run_accessions"], function(index, value) {
                          $el.append($("<option></option>")
                             .attr("value", value)
                             .attr("selected", run!= undefined && run.includes(value)).text(value));
                        });
            
                        $el =  $(".modal-dialog").find("#id_experiment");
                        experiment = $el.find(":selected").val()
                        $el.empty(); // remove old options
                        $.each(data["experiment_accessions"], function(index, value) {
                          $el.append($("<option></option>")
                            .attr("value", value)
                            .attr("selected", experiment != undefined && experiment.includes(value)).text(value));
                        });  
            
                    });    
                }));
                selected_sample = $(".modal-dialog").find("#id_sample").find(":selected").val()
                if ( selected_sample == "") {
                    var $el =  $(".modal-dialog").find("#id_run");
                    $el.empty(); // remove old options
                    $el =  $(".modal-dialog").find("#id_experiment");
                    $el.empty(); // remove old options             
                } else {
                    var event = jQuery.Event("change");
                    $(".modal-dialog").find("#id_sample").val(selected_sample).trigger(event);
                    console.log("triggered")
                }
                           
            }  
                
        } )); 
         dialog.open();  
       
        dialog.setClosable(false);
    }

    function do_record_task(event) {
        var task = event.task.toLowerCase(); //action to be performed e.g., 'Edit', 'Delete'
        var tableID = event.tableID; //get target table

        //retrieve target records and execute task
        var table = $('#' + tableID).DataTable();
        var records = []; //
        $.map(table.rows('.selected').data(), function (item) {
            records.push(item);
        });

        //add task
        if (task == "add") {
            url = "/copo/ena_annotation/"+uid 
            handle_add_n_edit(url)
        }
        else if (task == "edit") {
            url = "/copo/ena_annotation/"+uid+"/"+records[0].record_id  
            handle_add_n_edit(url)
        }
        else {
            form_generic_task(component, task, records);
        }        
    }


    $('body').on('posttablerefresh', function (event) {
        table = $('#'+ component + '_table').DataTable();
        var numCols = $('#' + component + '_table thead th').length;
        table.rows()
        .nodes()
        .to$()
        .addClass( 'highlight_accession' );

        for (var i=1; i<=numCols; i++) {
            if ( $(table.column(i).header()).text() == 'ACCESSION' ) {

                var no_accessiion_indexes = table.rows().eq( 0 ).filter( function (rowIdx) {
                    return table.cell( rowIdx, i ).data() === '' ? true : false;
                } );
                table.rows( no_accessiion_indexes )
                .nodes()
                .to$()
                .addClass( 'highlight_no_accession' );
                break  
            }
        }
    })     

});