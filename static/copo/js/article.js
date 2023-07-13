/**
 * felix.shaw@tgac.ac.uk - 01/05/15.
 */


$(document).ready(function () {
    'use strict';

    var token = $.cookie('csrftoken');
    $('.delete_cell').on('click', delete_handler);
    $('#files_table td').on('click', view_in_figshare);
    $('#btn_save_article').on('click', save_article);

    $('#show_file_modal_button').on('click', modal_setup_handler);

    $('#input_text').on("keypress", save_tags);


    function modal_setup_handler() {
        $('#fileupload')[0].reset();
        $('#files').empty()
    }


    // Change this to the location of your server-side upload handler:
    $('#fileupload').fileupload({
        url: '/rest/small_file_upload/',
        dataType: 'json',
        done: function (e, data) {
            var text = '';
            $.each(data.result, function (index, file) {
                text = text + '<span class="label label-success"><span class="glyphicon glyphicon-picture" aria-hidden="true"></span><span class="spacer"></span>' + file.name + '</span><span class="spacer"></span><input type="hidden" value="' + file.id + '"/>'
            });

            $('#files').append(text);

            //$('#upload_files_button').hide()
        },
        progressall: function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            $('#progress .progress-bar').css(
                'width',
                progress + '%'
            );
        },
        add: function (e, data) {
            $('#progress .progress-bar').css('width', '0%');
            data.submit();
        }

    })
});


function save_tags(e) {
    if (e.keyCode == 13) {
        e.preventDefault();
        var input = $(this).val();
        var tags = input.split(',');
        for (var i = 0; i < tags.length; i++) {
            $(this).val('');
            var text = '<span class="label label-info">' + tags[i] + '<span class="glyphicon glyphicon-remove delete_tag" aria-hidden="true"></span></span>';
            $('#tags_input').append(text);

            $('.delete_tag').on('click', function (e) {
                $(this).parent().remove()
            })
        }
    }
}


function save_article(e) {
    'use strict';
    e.preventDefault();

    // harvest data from form
    var token = $.cookie('csrftoken');
    var file_ids = $('#files').children('input');
    var files = [];
    $.each(file_ids, function (index, value) {
        files.push($(value).val())
    });
    var raw_tags = $('#tags_input').children('.label');
    var tags = [];
    $.each(raw_tags, function (index, value) {
        tags.push($(value).text())
    });
    var description = $('#description').val();
    var article_type = $('#article_type').val();

    // if description or tags not entered, do not submit
    if (description == '') {
        //show do not submit alert
        BootstrapDialog.show({
            title: 'Error',
            message: 'Please enter a description',
            type: BootstrapDialog.TYPE_DANGER
        });
        return false
    }
    if (tags.length == 0) {
        //show do not submit alert
        BootstrapDialog.show({
            title: 'Error',
            message: 'Please enter some tags',
            type: BootstrapDialog.TYPE_DANGER,
        });
        return false
    }

    // call backend method to save metadata and filepath to dal
    $.ajax({
        headers: {'X-CSRFToken': token},
        type: "POST",
        url: "/copo/save_article/",
        dataType: "json",
        data: {"files": files, "tags": tags, "description": description, "article_type": article_type}
    }).done(function (data) {
        // on success create new table row for front end
        var html = '';
        for (var i = 0; i < data.length; i++) {
            html += '<tr><td>' + data[i].original_name + '</td><td>' + data[i].uploaded_on + '</td><td>' + data[i].offset + '</td>';
            html += '<td class="delete_cell" data-article-id="' + data[i].id + '">';
            html += '<span class="glyphicon glyphicon-remove-sign"></span>';
            html += '</td>';
            html += '</tr>'
        }
        $('#files_table tbody').append(html);
        $('#file_upload_modal').modal('hide')
    })
}

function delete_handler(e) {

    var table_row = $(this).closest('tr');

    BootstrapDialog.show({
        title: 'Delete',
        message: 'Do you really want to delete this article?',
        buttons: [
            {
                id: 'btn-close',
                icon: 'glyphicon glyphicon-check',
                label: 'Cancel',
                cssClass: 'btn-default',
                autospin: false,
                action: function (dialogRef) {

                    dialogRef.close();
                }
            },
            {
                id: 'btn-delete',
                icon: 'glyphicon glyphicon-remove-sign',
                label: 'Delete',
                cssClass: 'btn-danger',
                autospin: false,
                action: function (dialogRef) {
                    id = table_row.attr('data-article-id');
                    var token = $.cookie('csrftoken');
                    $.ajax({
                        type: 'POST',
                        url: "/api/delete_figshare_article/" + id,
                        headers: {'X-CSRFToken': token},
                        dataType: 'json',
                        success: function (data) {
                            table_row.parent().remove()
                        },
                        error: function (data) {
                            console.log(data)
                        }
                    });
                    dialogRef.close();
                }
            }
        ]
    });


}

function view_in_figshare(e) {
    e.preventDefault();
    var article_id = $(e.target).closest('tr').attr('data-article-id');
    // ajax call checks if figshare creds are valid
    $.ajax({
        type: "GET",
        url: "/api/get_figshare_url/" + article_id,
        dataType: "json"
    }).done(function (data) {
        url = data.figshare_url;
        window.open(url, "_blank", "toolbar=no, scrollbars=yes, resizable=no, top=500, left=20, width=1024, height=768");
    })
}


