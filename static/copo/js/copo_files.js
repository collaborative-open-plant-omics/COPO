var dialog = new BootstrapDialog({
    title: "Upload local files",
    message: "<div><input type='file' id='file' style='display:block' /></div>",
    size: BootstrapDialog.SIZE_WIDE,
    buttons: [{
        id: 'upload_local_files_button',
        label: 'Upload Local Files',
        cssClass: 'btn-primary',
        title: 'Upload Local Files',
        action: function(){
            document.getElementById('file').click();
            //upload_spreadsheet($('#file').prop('files')[0])

        }
    }, {
        label: 'Close',
        action: function(dialogItself){
            dialogItself.close();
        }
    }]               
});

uid = document.location.href
uid = uid.split("/")
uid = uid[uid.length - 2]

$(document).ready(function () {

    //uid = document.location.href
    //uid = uid.split("/")
    //uid = uid[uid.length - 2]
    
    //******************************Event Handlers Block*************************//
    var component = "files";
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


    //details button hover
    /*
    $(document).on("mouseover", ".detail-hover-message", function (event) {
        $(this).prop('title', 'Click to view ' + component + ' details');
    });
    */
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
        if (task == "add_files_by_terminal") {
            do_add_record()
        } else if (task == "add_files_locally") {
            $("#uploadModal").modal('show')
        } else {
            form_generic_task(component, task, records);
        }
        
    }
    function do_add_record() {
        $("#url_upload_controls").show()
        $('#presigned_url_modal')
            .modal('show')
        ;
        $("#command_area").html("")
        $('#copy_urls_button').fadeOut()
        $('#process_urls_button').fadeIn()        
    }
 

    $(document).on("click", "#presigned_urls_modal_button, .new-terminal-file ", function (evt) {
        evt.preventDefault()
        do_add_record()
    })

    $(document).on("click", "#presigned_urls_modal_button, .new-local-file ", function (evt) {
        evt.preventDefault()
        $("#uploadModal").modal('show')
    })


    $(document).on("click", "#process_urls_button", function (evt) {
        // get list of files output from ls -F1
        var data = $("#url_text_area").val()
        filenames = data.split("\n")
        for (var i = 0; i < filenames.length; i++) {
            filenames[i] = filenames[i].trim()
            if (filenames[i].indexOf(" ") > -1) {
                alert("File name cannot contain spaces")
                return
            }
        }
        file_names = JSON.stringify(filenames)
        
        var csrftoken = $.cookie('csrftoken');
        $("#url_upload_controls").fadeOut()
        // pass to get pre-signed urls
        $("#command_area").html("Please wait ...")
        $.ajax({
            url: "/copo/process_urls",
            headers: {'X-CSRFToken': csrftoken},
            method: "POST",
            data: {data: file_names},
            dataType: "json"
        }).done(function (d) {
            $('#copy_urls_button').fadeIn()
            $('#process_urls_button').fadeOut()
            var out = "<kbd> nohup "
            // display each url in <kbd> tag
            $(d).each(function (idx, obj) {
                out = out + "curl --progress-bar -v -T '" + obj.name + "' '" + obj.url + "' | cat;"
            })
            out = out + "</kbd>"
            $("#command_area").html(out)
            $("#command_panel").show()
        }).fail(function (d) {
            $('#command_area').html(d.responseText);
            $('#copy_urls_button').fadeOut()
            $('#process_urls_button').fadeIn()
            console.log(d)
        })

    })

    $(document).on("click", "#copy_urls_button", function(evt) {
        //  $("#command_area").select()
            navigator.clipboard.writeText($("#command_area").text());
    })

    $(document).on("click", "#upload_local_files_button", function(evt) {
        //  $("#command_area").select()
       $("#uploadModal").find('#file').click();
       
    })


});


function upload_files(files) {
    $("#warning_info").fadeOut("fast")
    $("#warning_info2").fadeOut("fast")    

    var csrftoken = $.cookie('csrftoken');
    form = new FormData()
    for (var i = 0; i < files.length; i++) {
        form.append(i.toString(), files[i])
    }


    $('#upload_local_files_button').fadeOut()
    var percent = $(".percent")
    $("#ss_upload_spinner").fadeIn("fast")

    jQuery.ajax({
        url: "/copo/upload_ecs_files/"+uid,
        data: form,
        files: files,
        cache: false,
        dataType: "json",
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
        $('#upload_local_files_button').fadeIn()
        $("#ss_upload_spinner").fadeOut("fast")
        BootstrapDialog.show({
            title: 'Error',
            message: "Error " + data.status + ": " + data.responseText
        });
      
    }).done(function (data) {
        $('#upload_local_files_button').fadeIn()
        $("#ss_upload_spinner").fadeOut("fast")
        $("#uploadModal").modal("hide")
        result_dict = {}
        result_dict["status"] = "success"
        result_dict["message"] = "file/s are uploaded"
        do_crud_action_feedback(result_dict);
        globalDataBuffer = data;
        if (data.hasOwnProperty  ("table_data")) {
            var event = jQuery.Event("refreshtable");
            $('body').trigger(event);
        }

    })
}