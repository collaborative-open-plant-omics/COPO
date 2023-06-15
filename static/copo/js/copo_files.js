$(document).ready(function () {

    var uid = document.location.href
    uid = uid.split("/")
    uid = uid[uid.length - 2]
    
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
        if (task == "add") {
            do_add_record()
        }
        else {
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
 

    $(document).on("click", "#presigned_urls_modal_button, .new-component-template ", function (evt) {
        evt.preventDefault()
        do_add_record()
    })

    $(document).on("click", "#process_urls_button", function (evt) {
        // get list of files output from ls -F1
        var data = $("#url_text_area").val()
        file_names = JSON.stringify(data.split("\n"))
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

});