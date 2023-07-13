$(document).ready(function () {
        var uid = document.location.href
        uid = uid.split("/")
        uid = uid[uid.length - 1]
        var wsprotocol = 'ws://';
        var s3socket
        $('#copy_urls_button').fadeOut()
        $('#process_urls_button').fadeIn()

        if (window.location.protocol === "https:") {
            wsprotocol = 'wss://';
        }
        var wsurl = wsprotocol + window.location.host + '/ws/s3_status/' + uid

        s3socket = new ReconnectingWebSocket(wsurl);

        s3socket.onclose = function (e) {
            console.log("s3socket closing ", e)
        }
        s3socket.onopen = function (e) {
            console.log("s3socket opened ", e)
        }
        s3socket.onmessage = function (e) {
            d = JSON.parse(e.data)
            if (!d && $("#" + d.html_id).is(":visible")) {
                $("#" + d.html_id).fadeOut("50")
            } else if (d && d.message && !$("#" + d.html_id).is(":visible")) {
                $("#" + d.html_id).fadeIn("50")
            }
            $("#" + d.html_id).html(d.message)
            if (d.action === "info") {
                // show something on the info div
                // check info div is visible
                $("#" + d.html_id).removeClass("alert-danger").addClass("alert-info")
                $("#spinner").fadeOut()
            } else if (d.action === "error") {
                // check info div is visible
                $("#" + d.html_id).removeClass("alert-info").addClass("alert-danger")
                $("#spinner").fadeOut()
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
                $("#tabs").fadeIn()
                $("#ena_finish_button").fadeIn()
            }
        }
        window.addEventListener("beforeunload", function (event) {
            s3socket.close()
        });

        $(document).on("click", "#presigned_urls_modal_button", function (evt) {
            evt.preventDefault()
            $("#url_upload_controls").show()
            $('#presigned_url_modal')
                .modal('show')
            ;
            $("#command_area").html("")
            $('#copy_urls_button').fadeOut()
            $('#process_urls_button').fadeIn()
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

        $(document).on("click", "#copy_urls_button", function (evt) {
            //  $("#command_area").select()
            navigator.clipboard.writeText($("#command_area").text());
        })


    }
)


function upload_spreadsheet(file = file) {
    $("#upload_label").fadeOut("fast")
    $("#ss_upload_spinner").fadeIn("fast")
    $("#warning_info").fadeOut("fast")
    $("#warning_info2").fadeOut("fast")
    $("#presigned_urls_modal_button").prop('disabled', true);
    var csrftoken = $.cookie('csrftoken');
    form = new FormData()
    form.append("file", file)
    var percent = $(".percent")
    jQuery.ajax({
        url: "/copo/parse_ena_spreadsheet/",
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
        $("#ss_upload_spinner").fadeOut("fast")
        $("#presigned_urls_modal_button").prop('disabled', false);
        $("#upload_label").fadeIn()
        console.error(data)
        BootstrapDialog.show({
            title: 'Error',
            message: "Error " + data.status + ": " + data.responseText,
            type: BootstrapDialog.TYPE_DANGER
        });
    }).done(function (data) {
        $("#ss_upload_spinner").fadeOut("fast")
        $("#presigned_urls_modal_button").prop('disabled', false);
        $("#upload_label").fadeIn()

    })
}

$(document).on("click", "#ena_finish_button", function (event) {
    event.preventDefault()
    $.ajax({
        url: "/copo/save_ena_records"
    }).done(function (d) {
        window.location.href = "/copo/copo_submissions/" + $("#profile_id").val() + "/view"
    })
})