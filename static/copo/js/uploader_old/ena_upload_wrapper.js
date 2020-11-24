//this function is called on when the file upload changes, and sets some option in the
//jquery file upload plugin. If the file is larger than chunk_threshold, it should be chunked
var upload_size = 0;
var chunk_size = 0;
//var chunk_threshold = 200000000; // size of chunks in bytes
var chunk_threshold = 1000000;

function get_chunk_size(event) {
    upload_size = event.currentTarget.files[0].size;
    if (upload_size < chunk_threshold) {
        chunk_size = 0;
        $(event.currentTarget).parent().parent().fileupload(
            'option',
            {
                maxChunkSize: 0,
                url: '/rest/receive_data_file/'
            }
        );
    }
    else {
        chunk_size = chunk_threshold;
        //chunk_size = 10000000
        $(event.currentTarget).parent().parent().fileupload(
            'option',
            {
                maxChunkSize: chunk_threshold,
                url: '/rest/receive_data_file_chunked/'
            }
        );
    }
}


$(document).ready(function () {

    var u_id = undefined;
    var token = $.cookie('csrftoken');
    var f = $('#file_upload');
    $('input[name=upload_id]').val('');
    //this is the zip image being hidden
    $('.zip_image').hide();
    //hide the hashing image
    $('.hash_image').hide();
    //$('#input_md5_checksum').val('To Be Calculated...')
    //this is how many upload panels are on the screen
    $('#upload_info_count').val('0');

    $('#add_upload_group_button').hide();
    $('#select_file_type').change(function () {
        $('#file_type_guess').animate({opacity: "0"}, "fast")
    });


    $('body').on('click', '.file_info', function (data) {
        resume_upload()
    })

    // get partial uploads
    /*
     $.getJSON('/rest/get_partial_uploads/', function(result){
     result = JSON.parse(result)
     for(var k = 0; k < result.length; k++){
     f = result[k].fields
     html = make_upload_div(f.filename)
     var insert_node = $('.file_status_label')
     $(html).appendTo(insert_node);
     }
     })
     */

    $(function () {
        'use strict';
        //file upload plugin
        var s;
        $(document).on('click', 'form[id^=upload]', function () {

            $(this).fileupload({
                dataType: 'json',
                headers: {'X-CSRFToken': token},
                progressInterval: '300',
                bitrateInterval: '300',
                maxChunkSize: chunk_size,
                singleFileUploads: true,
                sequentialUploads: true,
                maxRetries: 100,
                retryTimeout: 500,
                fail: function (e, data) {
                    BootstrapDialog.show({
                        type: BootstrapDialog.TYPE_DANGER,
                        title: 'Something Went Wrong',
                        message: 'For some reason this upload failed. Please try again. If you are using a laptop, make sure you leave the lid open and adjust your settings to prevent hibernation. If this problem persists please contact the administrator.',
                        buttons: [{
                            label: 'Close',
                            action: function (dialog) {
                                dialog.close();
                            }
                        }]
                    });
                },
                done: function (e, data) {
                    var final = data.result.upload_id;
                    $(this).find('input[name=upload_id]').val('');
                    finalise_upload(e, data, final, this)
                },
                error: function (e, data) {
                    console.log($.makeArray(arguments));
                },
                start: function (e, data) {
                    $(this).parents().eq(2).find('.c').show()
                },
                add: function (e, data) {
                    for (var k = 0; k < data.files.length; k++) {
                        // for each file selected in the file picker
                        // check if it has an existing unfinished entry in the backend
                        var that = this;
                        var d_file = data.files[k];
                        $.ajax({
                            url: '/rest/resume_chunked/',
                            data: {'filename': d_file.name},
                            type: 'GET',
                            contentType: false,
                            dataType: 'json'
                        }).done(function (result) {

                            var insert_node = $('.file_status_label');
                            var size = parseFloat(d_file.size);
                            size = size / 1000000.0;
                            size = size.toFixed(2) + ' MB';
                            var file_name = d_file.name.substr(0, d_file.name.indexOf('.'));
                            $('#upload_files_button').attr('disabled', 'disabled');
                            var upload_div = make_upload_div(file_name)
                            $(upload_div).appendTo(insert_node)

                            var html = make_progress_bar(file_name, size)

                            $(html).appendTo(insert_node);
                            if (result != '') {
                                // for existing files, set current offset and upload id to continue upload
                                var file = JSON.parse(result)[0].fields
                                data.uploadedBytes = parseInt(file && file.offset);
                                data.formData = {'upload_id': file.upload_id}
                            }
                            $.blueimp.fileupload.prototype.options.add.call(that, e, data);
                            data.data = null;
                            data.submit();
                        })
                    }
                },
                progress: function (e, data) {
                    //get name of the file for which the progress update is for
                    var file_name = data.files[0].name;
                    file_name = file_name.substr(0, file_name.indexOf('.'));

                    //add new value to array
                    var speeds = $(document).data(file_name)
                    if (speeds == undefined) {
                        speeds = new Array()
                    }
                    speeds.push(data.bitrate)
                    $(document).data(file_name, speeds)

                    // calc mean bitrate
                    var tot = 0
                    for (var x = 0; x < speeds.length; x++) {
                        tot += speeds[x]
                    }
                    var bitrate = 1 / speeds.length * tot

                    var progress = parseInt(data.loaded / data.total * 100, 10);
                    var selector = '#progress_' + file_name;
                    $(selector + ' .bar').css(
                        'width',
                        progress + '%'
                    );
                    //display uploaded bytes
                    var uploaded = parseFloat(data.loaded) / 1000000.0;
                    s = uploaded.toFixed(2) + " MB of";
                    $('#progress_info_' + file_name).children('#progress_label').html(s);
                    //display upload bitrate
                    var bit = " @ " + (bitrate / 1000.0 / 1000.0 / 8).toFixed(2) + " MB/sec";
                    $('#progress_info_' + file_name).children('#bitrate').html(bit)
                }
            }).on('fileuploadchunkdone', function (e, data) {
                var file_name = data.files[0].name.substr(0, data.files[0].name.indexOf('.'));
                //console.log(data)
                $(this).find('input[name=upload_id]').val(data.result.upload_id);
            }).bind('fileuploadchange', function (e, data) {
            })
        })
    })
    ;


//function called to finalised chunked upload
    function finalise_upload(e, data, final, tform) {
        //serialise form
        form = $(tform).serializeFormJSON();
        panel_id = $(tform).attr('id');
        panel_id = panel_id.split('_')[1];
        token = $.cookie('csrftoken');
        var output;
        if (chunk_size > 0) {
            //if we have a chunked upload, call the complete view method in web
            $.ajax({
                headers: {'X-CSRFToken': token},
                url: "/rest/complete_upload/",
                type: "POST",
                data: {'upload_id': final, 'panel_id': panel_id},
                success: function (data) {
                    update_html(data, tform)
                },
                error: function () {
                    alert('error');
                    console.log($.makeArray(arguments));
                },
                dataType: 'json'
            })
        }
        else {
            //if we have a non chunked upload, just call the update_html method
            update_html(data, tform)
        }

    }

//update the html based on the results of the upload process
    function update_html(data, tform) {
        var x;
        if (chunk_size > 0) {
            x = $(data.files)
        }
        else {
            x = $(data.result.files)
        }

        var zipping_img = $('#zipping_image').val();
        var hashing_img = $('#hashing_image').val();
        for (var i = 0; i < x.size(); i++) {
            var file_name = x[i].name;
            file_name = file_name.substr(0, file_name.indexOf('.'));
            $('#progress_' + file_name).remove();
            $('#progress_info_' + file_name).remove();
            $('#id_' + file_name).remove();
            div = $('<div/>');
            var html = "<a href='#' class='close' data-dismiss='alert' aria-label='close'>&times;</a>";
            html += "<div class='row'><div class='col-sm-9 col-md-9 col-lg-9'>"
                + "<input name='file_id' type='hidden' value='" + x[i].id + "'/> <ul class='list-inline'><li><strong>" + x[i].name + "</strong></li><li class='file_size'>" + x[i].size.toFixed(1) + " MB</li></ul>"
                + "</div><div class='col-sm-3 col-md-3 col-lg-3'>"
                + '<span class="text-right zip-image"><img src="' + zipping_img + '" height="20px" class="pull-right"/>'
                + '<h4 style="margin-right:30px">Zipping</h4></span>'
                + '<span class="text-right hash-image"><img src="' + hashing_img + '" height="20px" class="pull-right"/>'
                + '<h4 style="margin-right:30px">Hashing</h4></span></div></div>';
            insert_node = $(tform).parents().eq(2).find('.file_status_label');
            div.addClass('alert alert-success file_info').html(html).appendTo(insert_node).fadeIn();
            div.find('.zip-image').hide();
            div.find('.hash-image').hide();
        }

        if ($.active < 2) {

            $('#upload_files_button').removeAttr('disabled')
        }

        //now call function to inspect files
        inspect_uploaded_files(x[0].id, tform)
    }


    function inspect_uploaded_files(file_id, tform) {
        //this function calls the server to ask it to inspect the files just uploaded and provide
        //the front end with any information to present to the user

        $.ajax({
            url: '/rest/inspect_file/',
            type: 'GET',
            dataType: 'json',
            data: {
                'file_id': file_id
            }
        }).done(function (data) {
            //refresh datafiles table
            do_render_server_side_table(get_component_meta("datafile"));

            //check if the file needs compression; send request to server to gzip
            if (data.do_compress) {

                $("input[value='" + file_id + "']").parent().next().children('.zip-image').fadeIn('4000');
                $.ajax({
                    url: '/rest/zip_file/',
                    type: 'GET',
                    dataType: 'json',
                    data: {
                        'file_id': file_id
                    },
                    success: function (data) {
                        $("input[value='" + file_id + "']").parent().next().children('.zip-image').fadeOut('4000');
                        //now change the file name and file size in the alert div
                        var new_name = data.file_name;
                        var new_size = data.file_size;
                        var node = $('input[value=' + file_id + ']');
                        $(node).next().find('strong').html(new_name);
                        $(node).next().find('.file_size').html(new_size + ' MB');
                        //do hash
                        get_hash(file_id, tform)

                        //update table data
                        do_render_server_side_table(get_component_meta("datafile"));

                    },
                    error: function (data) {
                        console.log(data)
                    }
                })
            }
            else {
                get_hash(file_id, tform)
            }
        })
    }

});

function get_hash(id, tform) {
    $("input[value='" + id + "']").parent().next().children('.hash-image').show();

    $.ajax({
        url: "/rest/hash_upload/",
        type: "GET",
        data: {
            file_id: id
        },
        dataType: 'json'
    }).done(function (data) {
        //now find the correct div and append the hash to it
        $d = $("input[value='" + data.file_id + "']").parent();
        html = '<h5><span class="hash_span label label-success">' + data.output_hash + '</span></h5>';
        $d.children('ul').append(html);
        $("input[value='" + id + "']").parent().next().children('.hash-image').hide();
        $("input[value='" + data.file_id + "']").closest(".file_info").remove();

        do_render_server_side_table(get_component_meta("datafile"));

    });

}

function make_progress_bar(file_name, size) {
    html = '<div id="progress_info_' + file_name + '" class="progress_info">' +
        '<input type="hidden" id="upload_id_' + file_name + '" value="" />' +
        '<span id="progress_label"></span>' +
        '<span id="total_label"> of ' + size + '</span>' +
        '<span id="bitrate"></span>' +
        '</div>' +
        '<div id="progress_' + file_name + '" class="progress">' +
        '<div style="width: 0%;height: 20px;background: green" class="bar"></div>' +
        '<div class="progress-bar progress-bar-success"></div>' +
        '</div>';
    return html
}

function make_upload_div(file_name) {
    //check if div with same name already exists
    $('.file_info').each(function (index, value) {
        if ($(value).text() == file_name) {
            $(this).remove()
            $('#progress_info_' + $(value).text()).remove()
            $('#progress_' + $(value).text()).remove()
        }
    })
    return $('<div/>').addClass('alert alert-warning file_info').attr('id', 'id_' + file_name).html("<strong>" + file_name + "</strong><i class='fa fa-upload pull-right' aria-hidden='true'></i>")
}

function resume_upload(e, data) {

}
/*
var url_string = window.location.href
var url = new URL(url_string);
var c = url.searchParams.get("test");
if (c == "yes") {
    $('#copo_data_upload_tab').show()
    $('form[id^=upload]').fileupload(
        {
            add: ["/small1_test.fastq"],

        })
}*/