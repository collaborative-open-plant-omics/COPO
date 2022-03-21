$(document).ready(function () {
        var uid = document.location.href
        uid = uid.split("/")
        uid = uid[uid.length - 1]
        var wsprotocol = 'ws://';
        var s3socket

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
            if (d.action === "info") {
                // show something on the info div
                // check info div is visible
                if (!$("#" + d.html_id).is(":visible")) {
                    $("#" + d.html_id).fadeIn("50")
                }
                $("#" + d.html_id).removeClass("alert-danger").addClass("alert-info")
                $("#" + d.html_id).html(d.message)
                $("#spinner").fadeOut()
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
        })

        $(document).on("click", "#process_urls_button", function (evt) {
            // get list of files output from ls -F1
            var data = $("#url_text_area").val()
            file_names = JSON.stringify(data.split("\n"))
            var csrftoken = $.cookie('csrftoken');
            $("#url_upload_controls").fadeOut()
            // pass to get pre-signed urls
            $.ajax({
                url: "/copo/process_urls",
                headers: {'X-CSRFToken': csrftoken},
                method: "POST",
                data: {data: file_names},
                dataType: "json"
            }).done(function (d) {
                var out = "<kbd> nohup "
                // display each url in <kbd> tag
                $(d).each(function (idx, obj) {
                    out = out + "curl --progress-bar -v -T '" + obj.name + "' '" + obj.url + "' | cat;"
                })
                out = out + "</kbd>"
                $("#command_area").html(out)
                $("#command_panel").show()
            }).fail(function (d) {
                console.log(d)
            })

        })

    }
)
