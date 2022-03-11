$(document).ready(function () {

    var wsprotocol = 'ws://';
    var s3socket
    window.addEventListener("beforeunload", function (event) {
        s3socket.close()
    });

    if (window.location.protocol === "https:") {
        wsprotocol = 'wss://';
    }
    s3socket = new ReconnectingWebSocket(
        wsprotocol + window.location.host +
        '/ws/sample_status/' + profileId);


    $(document).on("click", "#presigned_urls_modal_button", function (evt) {
        evt.preventDefault()
        $("#url_upload_controls").show()
        $('#presigned_url_modal')
            .modal('show')
        ;
    })

    $(document).on("click", "#process_urls_button", function (evt) {
        $("#url_upload_controls").fadeOut()
        $("#command_panel").show()
    })
})
