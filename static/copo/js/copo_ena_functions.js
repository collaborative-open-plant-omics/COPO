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
        console.log(d)
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
        var data = $("#url_text_area").val()
        data = data.split("\n")
        $("#url_upload_controls").fadeOut()

        console.log(data)
        $("#command_panel").show()
    })
})
