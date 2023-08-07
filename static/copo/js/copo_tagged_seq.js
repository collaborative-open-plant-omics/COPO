var dialog = new BootstrapDialog({
    title: "Upload Barcoding Manifest",
    message: "<div><input type='file' id='fileid' style='display:none' /></div>",
    size: BootstrapDialog.SIZE_WIDE,
    buttons: [{
        id: 'upload_taggedseq_manifest_button',
        label: 'Upload Barcoding Manifest',
        cssClass: 'btn-primary',
        title: 'Upload Barcoding Manifest',
        action: function(){
            document.getElementById('file').click();
            //upload_spreadsheet($('#file').prop('files')[0])

        }
    },{
        id: 'save_taggedseq_button',
        label: 'Finish',
        cssClass: 'btn-primary',
        title: 'Finish',
        disabled: true,
        action: function () {
            var $button = this; // 'this' here is a jQuery object that wrapping the <button> DOM element.
            $button.disable();
            $button.spin();
            dialog.setClosable(false);
            save_taggedseq_data()

        }
    }, {
        label: 'Close',
        action: function (dialogItself) {
            dialogItself.close();
        }
    }]
});

$(document).ready(function () {

    var uid = document.location.href
    uid = uid.split("/")
    uid = uid[uid.length - 2]
    var wsprotocol = 'ws://';
    var s3socket


    if (window.location.protocol === "https:") {
        wsprotocol = 'wss://';
    }
    var wsurl = wsprotocol + window.location.host + '/ws/tagged_seq_status/' + uid

    s3socket = new WebSocket(wsurl);

    s3socket.onclose = function (e) {
        console.log("s3socket closing ", e)
    }
    s3socket.onopen = function (e) {
        console.log("s3socket opened ", e)
    }
    s3socket.onmessage = function (e) {
        d = JSON.parse(e.data)
        element  = $("#" + d.html_id)
        if ($(".modal-dialog").is(':visible')) {
            elem = $(".modal-dialog").find("#" + d.html_id)
            if (elem) {
                element = elem
            }
        }

        if (!d && !$(element).is(":hidden")) {
            $(element).fadeOut("50")
        } else if (d && d.message && $(element).is(":hidden")) {
            $(element).fadeIn("50")
        }
        //$("#" + d.html_id).html(d.message)
        if (d.action === "info") {
            // show something on the info div
            // check info div is visible
            $(element).removeClass("alert-danger").addClass("alert-info")
            $(element).html(d.message)
            //$("#spinner").fadeOut()
        } else if (d.action === "error") {
            // check info div is visible
            $(element).removeClass("alert-info").addClass("alert-danger")
            $(element).html(d.message)
            //$("#spinner").fadeOut()
        } else if (d.action === "make_table") {
            // make table of metadata parsed from spreadsheet
            if ($.fn.DataTable.isDataTable("#" + d.html_id)) {
                $("#" + d.html_id).DataTable().clear().destroy();
            }
            $("#" + d.html_id).find("thead").empty()
            $("#" + d.html_id).find("tbody").empty()
            var body = $("tbody")
            var count = 0
            for (r in d.message) {
                row = d.message[r]
                var tr = $("<tr/>")
                for (c in row) {
                    cell = row[c]
                    if (count === 0) {
                        var td = $("<th/>", {
                            "html": cell
                        })
                    } else {
                        var td = $("<td/>", {
                            "html": cell
                        })
                    }
                    tr.append(td)
                }
                if (count === 0) {
                    $("#" + d.html_id).find("thead").append(tr)
                } else {
                    $("#" + d.html_id).find("tbody").append(tr)
                }
                count++
            }
            $("#sample_info").hide()
            $("#" + d.html_id).DataTable({
                "scrollY": "400px",
                "scrollX": true,
            })
            $("#table_div").fadeIn(1000)
            $("#" + d.html_id).DataTable().draw()
            $("#tabs").fadeIn()
            $("#ena_finish_button").fadeIn()
        }/* else if (d.action === "refresh_table") {
            globalDataBuffer = d.data;
            var event = jQuery.Event("refreshtable");
            $('body').trigger(event);
        } */
        if (d.data.hasOwnProperty  ("table_data")) {
            globalDataBuffer = d.data;
            var event = jQuery.Event("refreshtable");
            $('body').trigger(event);
        }
       
    }
    window.addEventListener("beforeunload", function (event) {
        s3socket.close()
    });


    //******************************Event Handlers Block*************************//
    var component = "taggedseq";
    var copoFormsURL = "/copo/copo_forms/";
    //var copoVisualsURL = "/copo/copo_visuals/";
    var csrftoken = $.cookie('csrftoken');

    //get component metadata
    var componentMeta = get_component_meta(component);

    var args_dict = {}
    args_dict["tagged_seq_checklist_id"] = $("#checklist_id").find(":selected").val();
    load_records(componentMeta, args_dict); // call to load component records
    $('.download-blank-manifest-template').attr("href",  $('#blank_manifest_url_'+args_dict["tagged_seq_checklist_id"]).val())


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
    $(document).on("click", ".new-taggedseq-spreadsheet-template", function (event) {
        url =  "/copo/ena_taggedseq_manifest_validate/" + uid+ "?checklist_id=" + $("#checklist_id").find(":selected").val();
        dialog.realize();
        dialog.setMessage($('<div></div>').load(url));
        dialog.open();   
        dialog.getButton('save_taggedseq_button').disable();
        
        $('.modal-dialog').find("#file").off("change").on("change", (function(event) {
            file = $(this).prop('files')[0]
            if (file == undefined)
                return
            dialog.getButton('upload_taggedseq_manifest_button').disable();
            dialog.getButton('upload_taggedseq_manifest_button').spin();
            dialog.setClosable(false);
            upload_spreadsheet(file)

        }));

    });

 

    $("#checklist_id").change(function(){

        if ($.fn.dataTable.isDataTable('#' + componentMeta.tableID)) {
            //if table instance already exists, then do refresh
            table = $('#' + componentMeta.tableID).DataTable();
            table.clear().destroy();
            $('#' + componentMeta.tableID).empty();
        }
        $('.download-blank-manifest-template').attr("href",  $('#blank_manifest_url_'+this.value).val())
        args_dict["tagged_seq_checklist_id"] = this.value;
        load_records(componentMeta, args_dict); // call to load component records
    });



 

    //******************************Event Handlers Block*************************//


    //details button hover
    /*
    $(document).on("mouseover", ".detail-hover-message", function (event) {
        $(this).prop('title', 'Click to view ' + component + ' details');
    });
    */

    //$(".new-reads-spreadsheet-template").addClass("btn btn-info").attr("data-toggle", "modal").attr("data-target", "#uploadModal")

    //******************************Functions Block******************************//


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
            url = "/copo/ena_annotation/" + uid
            handle_add_n_edit(url)
        } else if (task == "edit") {
            url = "/copo/ena_annotation/" + uid + "/" + records[0].record_id
            handle_add_n_edit(url)
        }
        else {    
            var args_dict = {}
            args_dict["tagged_seq_checklist_id"] = $("#checklist_id").find(":selected").val();            
            form_generic_task("taggedseq", task, records, args_dict);
        }

    }


    $('body').on('posttablerefresh', function (event) {
        table = $('#'+ componentMeta.tableID ).DataTable();
        var numCols = $('#' + componentMeta.tableID + ' thead th').length;
        table.rows()
            .nodes()
            .to$()
            .addClass('highlight_accession');

        for (var i=1; i<=numCols; i++) {
            if ( $(table.column(i).header()).text() == 'ACCESSION' ) {

                var no_accessiion_indexes = table.rows().eq( 0 ).filter( function (rowIdx) {
                    return table.cell( rowIdx, i ).data() == '' ? true : false;
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

function upload_spreadsheet(file) {
    $("#warning_info").fadeOut("fast")
    $("#warning_info2").fadeOut("fast")
    var csrftoken = $.cookie('csrftoken');
    form = new FormData()
    form.append("checklist_id", $("#checklist_id").find(":selected").val())
    form.append("file", file)
    var percent = $(".percent")
    jQuery.ajax({
        url: "/copo/parse_ena_taggedseq_spreadsheet/",
        data: form,
        cache: false,
        contentType: false,
        processData: false,
        method: 'POST',
        type: 'POST', // For jQuery < 1.9
        headers: {"X-CSRFToken": csrftoken},
        xhr: function () {
            var xhr = jQuery.ajaxSettings.xhr();
            xhr.upload.onprogress = function (evt) {
                var percentVal = Math.round(evt.loaded / evt.total * 100)
                percent.html("<b>" + percentVal + "%</b>")
                console.log('progress', percentVal)
            };
            xhr.upload.onload = function () {
                percent.html("")
                console.log('DONE!')
            };
            return xhr;
        }
    }).error(function (data) {
        dialog.getButton('upload_taggedseq_manifest_button').enable();
        dialog.setClosable(true);
        dialog.getButton('upload_taggedseq_manifest_button').stopSpin();
        //console.error(data)
        responseText = data.responseText
        if (responseText != "") {
            BootstrapDialog.show({
                title: 'Error',
                message: "Error " + data.status + ": " + data.responseText
            });
        }
       
    }).done(function (data) {
        dialog.getButton('upload_taggedseq_manifest_button').enable();
        dialog.getButton('save_taggedseq_button').enable();
        dialog.setClosable(true);
        dialog.getButton('upload_taggedseq_manifest_button').stopSpin();

    })
}

function save_taggedseq_data() {
    $.ajax({
        url: "/copo/save_ena_taggedseq_records"
    }).done(function (data) {
        result_dict = {}
        result_dict["status"] = "success"
        result_dict["message"] = "Barcoding records are saved"
        do_crud_action_feedback(result_dict);
        dialog.close()
        globalDataBuffer = data;

        if (data.hasOwnProperty("table_data")) {

            var event = jQuery.Event("refreshtable");
            $('body').trigger(event);
        }
    })
}
