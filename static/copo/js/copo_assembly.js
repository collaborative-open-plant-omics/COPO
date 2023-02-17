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
    var wsurl = wsprotocol + window.location.host + '/ws/assembly_status/' + uid

    s3socket = new WebSocket(wsurl);

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
        }
        else if (d && d.message && !$("#" + d.html_id).is(":visible")) {
            $("#" + d.html_id).fadeIn("50")
        }          
        $("#" + d.html_id).html(d.message)
        if (d.action === "info") {
            // show something on the info div
            // check info div is visible
            $("#" + d.html_id).removeClass("alert-danger").addClass("alert-info")
            $("#" + d.html_id).html(d.message)
            //$("#spinner").fadeOut()
        } else if (d.action === "error") {
            // check info div is visible
            $("#" + d.html_id).removeClass("alert-info").addClass("alert-danger")
            $("#" + d.html_id).html(d.message)
            //$("#spinner").fadeOut()
        } 
    }
    window.addEventListener("beforeunload", function (event) {
        s3socket.close()
    });
    }
)

function upload_assembly_files() {
    var csrftoken = $.cookie('csrftoken');
    var profile_id = $("#profile_id").val();
    var fieldset = $("#assembly_form input, textarea, select")
    const form = new FormData();
    var count = 0
    var files = []
    $(fieldset).each(function (idx, el) {
        if (el.type == "file") {
            form.append(el.name, el.files[0])
        } else {
            form.append(el.name, el.value)
        }
    })
    $("#assembly_form input, textarea, select").prop("disabled", true)


    form.append("profile_id", profile_id)
    jQuery.ajax({
        url: '/copo/ena_assembly/' + profile_id,
        data: form,
        files: files,
        cache: false,
        contentType: false,
        processData: false,
        type: 'POST', // For jQuery < 1.9
        headers:
            {
                "X-CSRFToken": csrftoken
            },
    }).error(function (data) {
        $("#assembly_form input, textarea, select").prop("disabled", false)
        $("#id_study").prop("disabled", true)
        $("#loading_span").fadeOut()
        console.error(data)
        BootstrapDialog.show({
            title: 'Error',
            message: "Error " + data.responseText
        });
    }).done(function (data) {
        $("#submit_assembly_button").fadeOut()
        $("#assembly_form").hide()
        $("#loading_span").hide()
        //$("input").fadeOut()
        //$("select").fadeOut()
        //$("textarea").fadeOut()
        //
        console.log(data)
    })
}


function doPost() {
    var evt = window.event
    evt.preventDefault()
 
    upload_assembly_files()
   // $("#submit_assembly_button").fadeOut()
   // $("#loading_span").fadeIn()
   // $('#assembly_form').submit()
   // var fieldset = $("#assembly_form input, textarea, select").prop("disabled", true)
}



