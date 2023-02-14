function upload_assembly_files() {
    var csrftoken = $.cookie('csrftoken');
    var profile_id = $("#profile_id").val();
    const html_form = document.getElementById('assembly_form');
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
        $("#loading_span").fadeOut()
        $('.ena_assembly_form').prop('disabled', false);
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
 
    
    $("#submit_assembly_button").fadeOut()

    $("#loading_span").fadeIn()
    $('#assembly_form').submit()
    var fieldset = $("#assembly_form input, textarea, select").prop("disabled", true)
}



