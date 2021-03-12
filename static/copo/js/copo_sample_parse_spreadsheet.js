function upload_image_files(file) {
    var csrftoken = $.cookie('csrftoken');

    form = new FormData()
    var count = 0
    for (f in file) {
        form.append(count.toString(), file[f])
        count++
    }
    jQuery.ajax({
        url: '/copo/sample_images/',
        data: form,
        cache: false,
        contentType: false,
        processData: false,

        type: 'POST', // For jQuery < 1.9
        headers: {"X-CSRFToken": csrftoken},

    }).error(function (data) {
        $("#upload_controls").fadeIn()
        console.error(data)
        BootstrapDialog.show({
            title: 'Error',
            message: "Error " + data
        });
    }).done(function (data) {

    })
}


function upload_spreadsheet(file) {
    $("#upload_label").fadeOut("fast")
    $("#ss_upload_spinner").fadeIn("fast")
    $("#warning_info").fadeOut("fast")
    var csrftoken = $.cookie('csrftoken');
    form = new FormData()
    form.append("file", file)
    jQuery.ajax({
        url: '/copo/sample_spreadsheet/',
        data: form,
        cache: false,
        contentType: false,
        processData: false,
        method: 'POST',
        type: 'POST', // For jQuery < 1.9
        headers: {"X-CSRFToken": csrftoken},

    }).error(function (data) {
        $("#upload_controls").fadeIn()
        console.error(data)
        BootstrapDialog.show({
            title: 'Error',
            message: "Error " + data.status + ": " + data.statusText
        });
    }).done(function (data) {
        $("#ss_upload_spinner").fadeOut("fast")
    })
}


$(document).ready(function () {

    // event listener for barcoding file upload button
    const barcode_input = document.getElementById("barcode_file");
    barcode_input.addEventListener("change", handleBarcodeUpload, false);

    $(document).on("click", "#finish_button", function (el) {
        if ($(el.currentTarget).hasOwnProperty("disabled")) {
            return false
        }
        BootstrapDialog.show({

            title: "Submit Samples",
            message: "Do you really want to submit these samples? They will be sent to a Darwin Tree of Life curator for checking",
            cssClass: "copo-modal1",
            closable: true,
            animate: true,
            type: BootstrapDialog.TYPE_INFO,
            buttons: [
                {
                    label: "Cancel",
                    cssClass: "tiny ui basic button",
                    action: function (dialogRef) {
                        dialogRef.close();
                    }
                },
                {
                    label: "Submit",
                    cssClass: "tiny ui basic button",
                    action: function (dialogRef) {
                        $("#finish_button").hide()

                        $.ajax({
                            url: "/copo/create_spreadsheet_samples",

                        }).done(function () {
                            location.reload()
                        }).error(function (data) {
                            console.error(data)
                        })
                        dialogRef.close();
                    }
                }
            ]

        })
    })


    var profileId = $('#profile_id').val();
    var wsprotocol = 'ws://';
    var socket;
    var socket2;
    window.addEventListener("beforeunload", function (event) {
        socket.close()
    });

    if (window.location.protocol === "https:") {
        wsprotocol = 'wss://';
    }
    socket = new WebSocket(
        wsprotocol + window.location.host +
        '/ws/sample_status/' + profileId);
    socket2 = new WebSocket(
        wsprotocol + window.location.host +
        '/ws/dtol_status');
    socket2.onopen = function (e) {
        console.log("opened ", e)
    }
    socket2.onmessage = function (e) {
        //d = JSON.parse(e.data)
        //console.log(d)
        //
    }
    socket.onerror = function (e) {
        console.log("error ", e)
    }
    socket.onclose = function (e) {
        console.log("closing ", e)
    }
    socket.onopen = function (e) {
        console.log("opened ", e)
    }
    socket2.onmessage = function (e) {
        console.log("received message")
        //handlers for channels messages sent from backend
        d = JSON.parse(e.data)
        //actions here should be performed regardeless of profile
        if (d.action === "delete_row") {
            console.log("deleteing row")
            s_id = d.html_id
            //$('tr[sample_id=s_id]').fadeOut()
            $('tr[sample_id="' + s_id + '"]').remove()
        }
        //actions here should only be performed by sockets with matching profile_id
        if (d.data.hasOwnProperty("profile_id")) {
            if ($("#profile_id").val() == d.data.profile_id) {
                if (d.action == "hide_sub_spinner") {
                    $("#sub_spinner").fadeOut(fadeSpeed)
                }
                if (d.action === "close") {
                    $("#" + d.html_id).fadeOut("50")
                } else if (d.action === "make_valid") {
                    $("#" + d.html_id).html("Validated").removeClass("alert-info, alert-danger").addClass("alert-success")
                } else if (d.action === "info") {
                    // show something on the info div
                    // check info div is visible
                    if (!$("#" + d.html_id).is(":visible")) {
                        $("#" + d.html_id).fadeIn("50")
                    }
                    $("#" + d.html_id).removeClass("alert-danger").addClass("alert-info")
                    $("#" + d.html_id).html(d.message)
                    $("#spinner").fadeOut()
                } else if (d.action === "warning") {
                    // show something on the info div
                    // check info div is visible
                    if (!$("#" + d.html_id).is(":visible")) {
                        $("#" + d.html_id).fadeIn("50")
                    }
                    $("#" + d.html_id).removeClass("alert-info").addClass("alert-warning")
                    $("#" + d.html_id).html(d.message)
                    $("#spinner").fadeOut()
                } else if (d.action === "error") {
                    // check info div is visible
                    if (!$("#" + d.html_id).is(":visible")) {
                        $("#" + d.html_id).fadeIn("50")
                    }
                    $("#" + d.html_id).removeClass("alert-info").addClass("alert-danger")
                    $("#" + d.html_id).html(d.message)
                    $("#export_errors_button").fadeIn()
                    $("#spinner").fadeOut()
                } else if (d.action === "make_images_table") {
                    // make table of images matched to
                    // headers
                    var headers = $("<tr><th>Specimen ID</th><th>Image File</th></th><th>Image</th></tr>")
                    $("#image_table").find("thead").empty().append(headers)
                    $("#image_table").find("tbody").empty()
                    var table_row
                    for (r in d.message) {
                        row = d.message[r]
                        if (row.file_name === "None") {
                            var img_tag = "Sample images must be named using the same Specimen ID as the manifest"
                        } else {
                            var img_tag = "<img src=" + row.file_name + "/>"
                        }
                        table_row = ("<tr><td>" + row.specimen_id + "</td><td>" + row.file_name.split('\\').pop().split('/').pop() + "</td><td>" + img_tag + "</td></tr>") // split-pop thing is to get filename from full path
                        $("#image_table").append(table_row)
                    }
                    $("#image_table").DataTable()
                    $("#image_table_nav_tab").click()
                    $("#finish_button").fadeIn()
                } else if (d.action === "make_table") {
                    // make table of metadata parsed from spreadsheet
                    if ($.fn.DataTable.isDataTable('#sample_parse_table')) {
                        $("#sample_parse_table").DataTable().clear().destroy();
                    }
                    $("#sample_parse_table").find("thead").empty()
                    $("#sample_parse_table").find("tbody").empty()
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
                            $("#sample_parse_table").find("thead").append(tr)
                        } else {
                            $("#sample_parse_table").find("tbody").append(tr)
                        }
                        count++
                    }
                    $("#sample_info").hide()
                    $("#sample_parse_table").DataTable({
                        "scrollY": "400px",
                        "scrollX": true,
                    })
                    $("#table_div").fadeIn(1000)
                    $("#sample_parse_table").DataTable().draw()
                    $("#files_label, #barcode_label").removeAttr("disabled")
                    $("#files_label, #barcode_label").find("input").removeAttr("disabled")
                    //$("#confirm_info").fadeIn(1000)
                    $("#tabs").fadeIn()
                    $("#finish_button").fadeIn()
                }
            }
        }
    }
})


$(document).on("click", ".new-samples-spreadsheet-template", function (event) {
    $("#sample_spreadsheet_modal").modal("show")
    $("#warning_info").fadeOut("fast")
})
$(document).on("click", ".barcoding_manifest", function (event) {
    $("#sample_barcoding_modal").modal("show")
    $("#warning_info").fadeOut("fast")
})
$(document).on("click", "#export_errors_button", function (event) {
    var data = $("#sample_info").html()
    //data = data.replace("<br>", "\r\n")
    //data = data.replace(/<[^>]*>/g, '');
    download("errors.html", data)
})

function download(filename, text) {
    // make filename
    f = $("#sample_info").find("h4").html().replace(/\.[^/.]+$/, "_errors.html")
    var pom = document.createElement('a');
    pom.setAttribute('href', 'data:text/html;charset=utf-8,' + encodeURIComponent(text));
    pom.setAttribute('download', f);

    if (document.createEvent) {
        var event = document.createEvent('MouseEvents');
        event.initEvent('click', true, true);
        pom.dispatchEvent(event);
    } else {
        pom.click();
    }
}

function handleBarcodeUpload(data) {
    let f = this.files[0];
    var csrftoken = $.cookie('csrftoken');
    form = new FormData()
    form.append("file", f)
    $.ajax({
        url: "/copo/upload_barcoding_manifest/",
        data: form,
        cache: false,
        contentType: false,
        processData: false,
        method: 'POST',
        dataType: "json",
        type: 'POST', // For jQuery < 1.9
        headers: {"X-CSRFToken": csrftoken},
    }).error(function (data) {
        console.error(data)
    }).done(function (data) {
        $(document).data("barcode_uid", data.uid)
        table_data = JSON.parse(data.data)
        let row = $("<tr>")
        for (t in table_data) {
            let head = $("<th/>", {
                html: t
            })
            $(row).append(head)
        }
        $("#barcode_table").find("thead").append(row)
        for (t in table_data) {
            d = table_data[t]
            let row = $("<tr>")
            for (cell in d) {
                let head = $("<td/>", {
                    html: d[cell]
                })
                $(row).append(head)
            }
            $("#barcode_table").find("tbody").append(row)
        }

    })
}