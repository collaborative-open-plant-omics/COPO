var finishBtnStatus;
var confirmBtnStatus;
var permitBtnStatus;
var isNew = true

function upload_image_files(file) {
    var csrftoken = $.cookie('csrftoken');
    var validation_record_id = $(document).data('validation_record_id');
    $('#images_label').addClass('disabled');
    $('#images_label').attr('disabled', 'true');
    $('#images_label').find('input').attr('disabled', 'true');
    $('#ss_upload_spinner').fadeIn('fast');
    finishBtnStatus = $('#finish_button').is(':hidden');
    confirmBtnStatus = $('#confirm_button').is(':hidden');
    permitBtnStatus = $('#files_label').hasClass('disabled');
    if (!permitBtnStatus) {
        $('#files_label').addClass('disabled');
        $('#files_label').attr('disabled', 'true');
        $('#files_label').find('input').attr('disabled', 'true');
    }
    $('#finish_button').hide();
    $('#confirm_button').hide();
    form = new FormData();
    var count = 0;
    for (f in file) {
        form.append(count.toString(), file[f]);
        count++;
    }
    form.append('validation_record_id', validation_record_id);
    var percent = $('.percent');
    jQuery
        .ajax({
            url: '/copo/sample_images/',
            data: form,
            cache: false,
            contentType: false,
            processData: false,

            type: 'POST', // For jQuery < 1.9
            headers: {'X-CSRFToken': csrftoken},
            xhr: function () {
                var xhr = jQuery.ajaxSettings.xhr();
                xhr.upload.onprogress = function (evt) {
                    var percentVal = Math.round((evt.loaded / evt.total) * 100);
                    percent.html('<b>' + percentVal + '%</b>');
                    console.log('progress', percentVal);
                };
                xhr.upload.onload = function () {
                    percent.html('');
                    console.log('DONE!');
                };
                return xhr;
            },
        })
        .error(function (data) {
            $('#ss_upload_spinner').fadeOut('fast');
            $('#upload_controls').fadeIn();
            console.error(data);
            BootstrapDialog.show({
                title: 'Error',
                message: 'Error ' + data.status + ': ' + data.statusText,
                type: BootstrapDialog.TYPE_DANGER,
            });
        })
        .done(function (data) {
            $('#ss_upload_spinner').fadeOut('fast');
        });
}

function upload_permit_files(file) {
    var csrftoken = $.cookie('csrftoken');
    var validation_record_id = $(document).data('validation_record_id');
    form = new FormData();
    var count = 0;
    for (f in file) {
        form.append(count.toString(), file[f]);
        count++;
    }
    form.append('validation_record_id', validation_record_id);
    var percent = $('.percent');
    jQuery
        .ajax({
            url: '/copo/sample_permits/',
            data: form,
            cache: false,
            contentType: false,
            processData: false,

            type: 'POST', // For jQuery < 1.9
            headers: {'X-CSRFToken': csrftoken},

            xhr: function () {
                var xhr = jQuery.ajaxSettings.xhr();
                xhr.upload.onprogress = function (evt) {
                    var percentVal = Math.round((evt.loaded / evt.total) * 100);
                    percent.html('<b>' + percentVal + '%</b>');
                    console.log('progress', percentVal);
                };
                xhr.upload.onload = function () {
                    percent.html('');
                    console.log('DONE!');
                };
                return xhr;
            },
        })
        .error(function (data) {
            $('#ss_upload_spinner').fadeOut('fast');
            $('#upload_controls').fadeIn();
            console.error(data);
            BootstrapDialog.show({
                title: 'Error',
                message: 'Error ' + data.status + ': ' + data.statusText,
                type: BootstrapDialog.TYPE_DANGER,
            });
        })
        .done(function (data) {
            $('#ss_upload_spinner').fadeOut('fast');
        });
}

function upload_spreadsheet(upload_type = upload_type, file = file) {
    if (upload_type === 'ena_seq_reads') {
        url = '/copo/parse_ena_spreadsheet/';
    } else if (upload_type === 'sample_spreadsheet') {
        url = '/copo/sample_spreadsheet/';
    }
    $('#upload_label').fadeOut('fast');
    $('#ss_upload_spinner').fadeIn('fast');
    $('#warning_info').fadeOut('fast');
    $('#warning_info2').fadeOut('fast');
    var csrftoken = $.cookie('csrftoken');
    form = new FormData();
    form.append('file', file);
    var percent = $('.percent');
    jQuery
        .ajax({
            url: url,
            data: form,
            cache: false,
            contentType: false,
            processData: false,
            method: 'POST',
            type: 'POST', // For jQuery < 1.9
            headers: {'X-CSRFToken': csrftoken},
            xhr: function () {
                var xhr = jQuery.ajaxSettings.xhr();
                xhr.upload.onprogress = function (evt) {
                    var percentVal = Math.round((evt.loaded / evt.total) * 100);
                    percent.html('<b>' + percentVal + '%</b>');
                    console.log('progress', percentVal);
                };
                xhr.upload.onload = function () {
                    percent.html('');
                    console.log('DONE!');
                };
                return xhr;
            },
        })
        .error(function (data) {
            $('#ss_upload_spinner').fadeOut('fast');
            $('#upload_controls').fadeIn();
            console.error(data);
            BootstrapDialog.show({
                title: 'Error',
                message: 'Error ' + data.status + ': ' + data.responseText,
                type: BootstrapDialog.TYPE_DANGER,
            });
        })
        .done(function (data) {
            $('#ss_upload_spinner').fadeOut('fast');
        });
}

$(document).ready(function () {
    $(document).on('click', '#finish_button', function (el) {
        el.preventDefault();
        if ($(el.currentTarget).hasOwnProperty('disabled')) {
            return false;
        }
        BootstrapDialog.show({
            title: 'Submit Samples',
            message:
                'Do you really want to submit these samples? ' +
                '</br><strong>This must be the ' +
                "definitive version of the manifest.</strong> You won't be able to update any field " +
                'involved in the compliance process.</br> ' +
                'The sample metadata will be sent to a Tree of Life curator for checking',
            cssClass: 'copo-modal1',
            closable: true,
            animate: true,
            type: BootstrapDialog.TYPE_INFO,
            buttons: [
                {
                    id: 'cancelBtnID',
                    label: 'Cancel',
                    cssClass: 'tiny ui basic button',
                    action: function (dialogRef) {
                        dialogRef.close();
                    },
                },
                {
                    id: 'confirmBtnID',
                    label: 'Confirm',
                    cssClass: 'tiny ui basic button dialog_confirm',
                    action: function (dialogRef) {
                        $('#finish_button').hide();
                        $('#ss_upload_spinner').fadeIn('fast');
                        
                        dialogRef.getButton('cancelBtnID').disable(); // Disable 'Cancel' button

                        // Disable the 'Confirm' button and show spinner
                        let $button = this;
                        $button.disable();
                        $button.spin();
                        dialogRef.setClosable(false);
                        
                        $.ajax({
                            url: '/copo/create_spreadsheet_samples',
                            data: {
                                validation_record_id: $(document).data('validation_record_id'),
                            },
                        })
                            .done(function (data) {
                                dialogRef.close(); // Close 'Confirm' modal

                                // Refresh table
                                let result_dict = {};
                                result_dict['status'] = 'success';
                                result_dict['message'] =
                                    'Samples have been created successfully';
                                do_crud_action_feedback(result_dict);

                                globalDataBuffer = data;

                                if (data.hasOwnProperty('table_data')) {
                                    const event = jQuery.Event('refreshtable');
                                    $('body').trigger(event);
                                }
                                $('#sample_spreadsheet_modal').modal('hide'); // Close 'Upload Spreadsheet' modal
                            })
                            .error(function (data) {
                                console.error(data);
                            });
                    },
                },
            ],
        });
    });

    $(document).on('click', '#confirm_button', function (el) {
        if ($(el.currentTarget).hasOwnProperty('disabled')) {
            return false;
        }
        BootstrapDialog.show({
            title: 'Submit Samples',
            message: 'Do you really want to make these changes to the samples?',
            cssClass: 'copo-modal1',
            closable: true,
            animate: true,
            type: BootstrapDialog.TYPE_INFO,
            buttons: [
                {
                    id: 'cancelBtnID',
                    label: 'Cancel',
                    cssClass: 'tiny ui basic button',
                    action: function (dialogRef) {
                        dialogRef.close();
                    },
                },
                {
                    id: 'updateBtnID',
                    label: 'Update',
                    cssClass: 'tiny ui basic button',
                    action: function (dialogRef) {
                        $('#confirm_button').hide();
                        $('#ss_upload_spinner').fadeIn('fast');

                        dialogRef.getButton('cancelBtnID').disable(); // Disable 'Cancel' button

                        // Disable the 'Update' button and show spinner
                        let $button = this;
                        $button.disable();
                        $button.spin();
                        dialogRef.setClosable(false);
                        
                        $.ajax({
                            url: '/copo/update_spreadsheet_samples',
                            data: {
                                validation_record_id: $(document).data('validation_record_id'),
                            },
                        })
                            .done(function (data) {
                                dialogRef.close(); // Close 'Update' modal
                                // Refresh table
                                let result_dict = {};
                                result_dict['status'] = 'success';
                                result_dict['message'] =
                                    'Samples have been updated successfully';
                                do_crud_action_feedback(result_dict);
                                globalDataBuffer = data;

                                if (data.hasOwnProperty('table_data')) {
                                    const event = jQuery.Event('refreshtable');
                                    $('body').trigger(event);
                                }
                                $('#sample_spreadsheet_modal').modal('hide'); // Close 'Upload Spreadsheet' modal
                            })
                            .error(function (data) {
                                console.error(data);
                            });
                    },
                },
            ],
        });
    });

    var profileId = $('#profile_id').val();
    var wsprotocol = 'ws://';
    var socket;
    var socket2;
    window.addEventListener('beforeunload', function (event) {
        socket.close();
        socket2.close();
    });

    if (window.location.protocol === 'https:') {
        wsprotocol = 'wss://';
    }

    socket = new WebSocket(
        wsprotocol + window.location.host + '/ws/sample_status/' + profileId
    );
    socket2 = new ReconnectingWebSocket(
        wsprotocol + window.location.host + '/ws/dtol_status'
    );

    socket2.onopen = function (e) {
        console.log('opened ', e);
    };
    socket2.onmessage = function (e) {
        //d = JSON.parse(e.data)
        //console.log(d)
    };

    socket.onerror = function (e) {
        console.log('error ', e);
    };
    socket.onclose = function (e) {
        console.log('closing ', e);
    };
    socket.onopen = function (e) {
        console.log('opened ', e);
    };
    socket2.onmessage = function (e) {
        console.log('received message');
        //handlers for channels messages sent from backend
        d = JSON.parse(e.data);
        //actions here should be performed regardeless of profile
        if (d.action === 'store_validation_record_id') {
            $(document).data('validation_record_id', d.message);
        }
        if (d.action === 'delete_row') {
            console.log('deleteing row');
            s_id = d.html_id;
            //$('tr[sample_id=s_id]').fadeOut()
            $('tr[sample_id="' + s_id + '"]').remove();
        }

        //actions here should only be performed by sockets with matching profile_id
        if (d.data.hasOwnProperty('profile_id')) {
            if ($('#profile_id').val() == d.data.profile_id) {
                if (d.action == 'hide_sub_spinner') {
                    $('#sub_spinner').fadeOut(fadeSpeed);
                }
                if (d.action === 'close') {
                    $('#' + d.html_id).fadeOut('50');
                } else if (d.action === 'make_valid') {
                    $('#' + d.html_id)
                        .html('Validated')
                        .removeClass('alert-info, alert-danger')
                        .addClass('alert-success');
                } else if (d.action === 'info') {
                    // show something on the info div
                    // check info div is visible
                    if (!$('#' + d.html_id).is(':visible')) {
                        $('#' + d.html_id).fadeIn('50');
                    }
                    $('#' + d.html_id)
                        .removeClass('alert-danger')
                        .addClass('alert-info');

                    $('#' + d.html_id).html(d.message);
                    $('#spinner').fadeOut();
                } else if (d.action === 'csv_updates') {
                    // show something on the info div
                    // check info div is visible
                    if (!$('#' + d.html_id).is(':visible')) {
                        $('#' + d.html_id).fadeIn('50');
                    }
                    t = '<table>';
                    t = t + '<th><td>Sample Name</td></th>';
                    $(d.message.csv_samples).each(function (idx, el) {
                        t = t + '<tr><td>' + el.name + '</td></tr>';
                    });
                    t = t + '</table>';
                    $('#' + d.html_id).html(t);
                    $('#spinner').fadeOut();
                } else if (d.action === 'warning') {
                    // show something on the info div
                    // check info div is visible
                    if (!$('#' + d.html_id).is(':visible')) {
                        $('#' + d.html_id).fadeIn('50');
                    }
                    $('#' + d.html_id)
                        .removeClass('alert-info')
                        .addClass('alert-warning');
                    $('#' + d.html_id).html(d.message);
                    $('#spinner').fadeOut();
                } else if (d.action === 'error') {
                    // check info div is visible
                    if (!$('#' + d.html_id).is(':visible')) {
                        $('#' + d.html_id).fadeIn('50');
                    }
                    $('#' + d.html_id)
                        .removeClass('alert-info')
                        .addClass('alert-danger');
                    $('#' + d.html_id).html(d.message);
                    $('#export_errors_button').fadeIn();
                    $('#spinner').fadeOut();
                } else if (d.action === 'success') {
                    // check info div is visible
                    if (!$('#' + d.html_id).is(':visible')) {
                        $('#' + d.html_id).fadeIn('50');
                    }
                    $('#' + d.html_id)
                        .removeClass('alert-info')
                        .addClass('alert-success');
                    $('#' + d.html_id).html(d.message);
                    $('#export_errors_button').fadeIn();
                    $('#spinner').fadeOut();
                } else if (d.action === 'make_images_table') {
                    // make table of images matched to
                    // headers
                    $('#images_label').removeClass('disabled');
                    $('#images_label').removeAttr('disabled');
                    $('#images_label').find('input').removeAttr('disabled');
                    $('#ss_upload_spinner').fadeOut('fast');
                    if (!finishBtnStatus) {
                        $('#finish_button').show();
                    }
                    if (!confirmBtnStatus) {
                        $('#confirm_button').show();
                    }
                    if (!permitBtnStatus) {
                        $('#files_label').removeClass('disabled');
                        $('#files_label').removeAttr('disabled');
                        $('#files_label').find('input').removeAttr('disabled');
                    }

                    var headers = $(
                        '<tr><th>Specimen ID</th><th>Image File</th></th><th>Image</th></tr>'
                    );
                    $('#image_table').find('thead').empty().append(headers);
                    $('#image_table').find('tbody').empty();
                    var table_row;
                    for (r in d.message) {
                        row = d.message[r];
                        img_tag = '';
                        if (row.specimen_id === '') {
                            img_tag =
                                'Sample images must be named as {Specimen_ID}-{n}.[jpg|png]';
                        } else if (row.thumbnail != '') {
                            img_tag =
                                "<a target='_blank' href='" +
                                row.file_name +
                                "'> <img src='" +
                                row.thumbnail +
                                "' /></a>";
                        }
                        table_row =
                            '<tr><td>' +
                            row.specimen_id +
                            '</td><td>' +
                            row.file_name.split('\\').pop().split('/').pop() +
                            '</td><td>' +
                            img_tag +
                            '</td></tr>'; // split-pop thing is to get filename from full path
                        $('#image_table').append(table_row);
                    }
                    $('#image_table').DataTable();
                    $('#image_table_nav_tab').click();
                    //$("#finish_button").fadeIn()
                } else if (d.action === 'make_permits_table') {
                    // make table of permits matched to
                    // specimen_ids
                    if ($.fn.DataTable.isDataTable('#permits_table')) {
                        $('#permits_table').DataTable().clear().destroy();
                    }
                    var headers = $(
                        '<tr><th>Specimen ID</th><th>Permit Type</th><th>Permit Files</th><th>Notes</th></tr>'
                    );
                    $('#permits_table').find('thead').empty().append(headers);
                    $('#permits_table').find('tbody').empty();
                    var table_row;

                    // Filter out duplicates
                    d.message = d.message.filter(
                        (item, index, self) =>
                            self.findIndex(
                                (x) =>
                                    x.specimen_id === item.specimen_id &&
                                    x.permit_type === item.permit_type
                            ) === index
                    );

                    for (let r in d.message) {
                        row = d.message[r];

                        if (row.file_name === 'None') {
                            var img_tag =
                                'Filename of permit must be named ' +
                                '<strong>' +
                                row.file_name_expected +
                                '</strong>';
                        } else {
                            var img_tag = '';
                        }
                        table_row =
                            '<tr><td>' +
                            row.specimen_id +
                            '</td><td>' +
                            row.permit_type +
                            '</td><td>' +
                            row.file_name.split('\\').pop().split('/').pop() +
                            '</td><td>' +
                            img_tag +
                            '</td></tr>'; // split-pop thing is to get filename from full path
                        $('#permits_table').append(table_row);
                    }
                    $('#permits_table').DataTable();
                    $('#permits_table_nav_tab').click();
                    if (d.data.hasOwnProperty('fail_flag') && d.data.fail_flag == true) {
                    } else {
                        if (isNew) {
                            $('#finish_button').fadeIn();
                        } else {
                            $('#confirm_button').fadeIn();
                        }    
                    }
                } else if (d.action === 'make_table') {
                    isNew = true
                    // make table of metadata parsed from spreadsheet
                    if ($.fn.DataTable.isDataTable('#sample_parse_table')) {
                        $('#sample_parse_table').DataTable().clear().destroy();
                    }
                    $('#sample_parse_table').find('thead').empty();
                    $('#sample_parse_table').find('tbody').empty();
                    var body = $('tbody');
                    var count = 0;
                    for (r in d.message) {
                        row = d.message[r];
                        var tr = $('<tr/>');
                        for (c in row) {
                            cell = row[c];
                            if (count === 0) {
                                var td = $('<th/>', {
                                    html: cell,
                                });
                            } else {
                                var td = $('<td/>', {
                                    html: cell,
                                });
                            }
                            tr.append(td);
                        }
                        if (count === 0) {
                            $('#sample_parse_table').find('thead').append(tr);
                        } else {
                            $('#sample_parse_table').find('tbody').append(tr);
                        }
                        count++;
                    }
                    $('#sample_info').hide();
                    $('#sample_parse_table').DataTable({
                        scrollY: '400px',
                        scrollX: true,
                    });
                    $('#table_div').fadeIn(1000);
                    $('#sample_parse_table').DataTable().draw();
                    $('#files_label, #barcode_label').removeAttr('disabled');
                    $('#files_label, #barcode_label')
                        .find('input')
                        .removeAttr('disabled');
                    //$("#confirm_info").fadeIn(1000)
                    $('#tabs').fadeIn();
                    $('#files_label').removeClass('disabled');
                    $('#images_label').removeClass('disabled');
                    $('#images_label').removeAttr('disabled');
                    $('#images_label').find('input').removeAttr('disabled');
                    if (
                        d.data.hasOwnProperty('permits_required') &&
                        d.data.permits_required == true
                    ) {
                        $('#finish_button').fadeOut();
                    } else {
                        if ($('#files_label').is(':visible')) {
                            // $("#files_label").fadeOut()
                            $('#files_label').addClass('disabled');
                            $('#files_label').attr('disabled', 'true');
                            $('#files_label').find('input').attr('disabled', 'true');
                        }
                        $('#ena_finish_button').fadeIn();
                        $('#finish_button').fadeIn();
                    }
                } else if (d.action === 'make_update') {
                    // make table of metadata parsed from spreadsheet
                    isNew = false
                    if ($.fn.DataTable.isDataTable('#sample_parse_table')) {
                        $('#sample_parse_table').DataTable().clear().destroy();
                    }
                    $('#sample_parse_table').find('thead').empty();
                    $('#sample_parse_table').find('tbody').empty();
                    var body = $('tbody');
                    var count = 0;
                    for (r in d.message) {
                        row = d.message[r];
                        var tr = $('<tr/>');
                        for (c in row) {
                            cell = row[c];
                            if (count === 0) {
                                var td = $('<th/>', {
                                    html: cell,
                                });
                            } else {
                                var td = $('<td/>', {
                                    html: cell,
                                });
                            }
                            tr.append(td);
                        }
                        if (count === 0) {
                            $('#sample_parse_table').find('thead').append(tr);
                        } else {
                            $('#sample_parse_table').find('tbody').append(tr);
                        }
                        count++;
                    }
                    $('#sample_info').hide();
                    $('#sample_parse_table').DataTable({
                        scrollY: '400px',
                        scrollX: true,
                    });
                    $('#table_div').fadeIn(1000);
                    $('#sample_parse_table').DataTable().draw();
                    $('#files_label, #barcode_label').removeAttr('disabled');
                    $('#files_label, #barcode_label')
                        .find('input')
                        .removeAttr('disabled');
                    $('#files_label, #barcode_label').removeClass('disabled');
                    $('#images_label').removeAttr('disabled');
                    $('#images_label').removeClass('disabled');
                    $('#images_label').find('input').removeAttr('disabled');
                    //$("#confirm_info").fadeIn(1000)
                    $('#tabs').fadeIn();
                    if (
                        d.data.hasOwnProperty('permits_required') &&
                        d.data.permits_required == true
                    ) {
                        $('#confirm_button').fadeOut();


                    } else {
                        $('#confirm_button').fadeIn();
                    }
                } else if (d.action == 'require_permits') {
                    $('#confirm_button').fadeOut();
                    $('#finish_button').fadeOut();
                    $('#files_label').removeAttr('disabled');
                    $('#files_label').removeClass('disabled');
                    $('#files_label').find('input').removeAttr('disabled');
                }
            }
        }
    };
});

$(document).on(
    'click',
    '.new-samples-spreadsheet-template, .new-samples-spreadsheet-template-erga',
    function (event) {
        $('#sample_spreadsheet_modal').modal('show');

        $('#warning_info').fadeOut('fast');
        $('#warning_info2').fadeOut('fast');
        $('#warning_info3').fadeOut('fast');

        $('#images_label').addClass('disabled');
        $('#images_label').attr('disabled', 'true');
        $('#images_label').find('input').attr('disabled', 'true');
        $('#ss_upload_spinner').fadeOut('fast');
        $('#files_label').addClass('disabled');
        $('#files_label').attr('disabled', 'true');
        $('#files_label').find('input').attr('disabled', 'true');
        $('#finish_button').fadeOut('fast');
        $('#confirm_button').fadeOut('fast');
        $('#export_errors_button').fadeOut('fast');
    }
);

$(document).on(
    'click',
    '.new-samples-spreadsheet-template-erga',
    function (event) {
        BootstrapDialog.show({
            title: 'Accept Code of Conduct',
            message:
                "By uploading a manifest to COPO you confirm that you are an ERGA member and thus adhere to ERGA's " +
                'code of conduct. You further confirm that you read, understood and followed the ' +
                "<a href='https://bit.ly/3zHun36'>ERGA Sample " +
                'Code of Practice</a>',
            cssClass: 'copo-modal1',
            closable: true,
            animate: true,
            type: BootstrapDialog.TYPE_INFO,
            buttons: [
                {
                    label: 'Cancel',
                    cssClass: 'tiny ui basic' + ' button',
                    id: 'code_cancel',
                    action: function (dialogRef) {
                        $('#sample_spreadsheet_modal').modal('hide');
                        dialogRef.close();
                    },
                },
                {
                    label: 'Ok',
                    cssClass: 'tiny ui basic button',
                    action: function (dialogRef) {
                        dialogRef.close();
                    },
                },
            ],
        });
    }
);

$(document).on('click', '#code_cancel', function (event) {
    var data = $('#sample_info').html();
});

$(document).on('click', '#ena_finish_button', function (event) {
    event.preventDefault();
    $.ajax({
        url: '/copo/save_ena_records',
    }).done(function (d) {
        window.location.href =
            '/copo/copo_submissions/' + $('#profile_id').val() + '/view';
    });
});

$(document).on('click', '#export_errors_button', function (event) {
    var data = $('#sample_info').html();
    //data = data.replace("<br>", "\r\n")
    //data = data.replace(/<[^>]*>/g, '');
    download('errors.html', data);
});

function download(filename, text) {
    // make filename
    f = $('#sample_info')
        .find('h4')
        .html()
        .replace(/\.[^/.]+$/, '_errors.html');
    var pom = document.createElement('a');
    pom.setAttribute(
        'href',
        'data:text/html;charset=utf-8,' + encodeURIComponent(text)
    );
    pom.setAttribute('download', f);

    if (document.createEvent) {
        var event = document.createEvent('MouseEvents');
        event.initEvent('click', true, true);
        pom.dispatchEvent(event);
    } else {
        pom.click();
    }
}
