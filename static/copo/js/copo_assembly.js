function upload_assembly_files() {
    var csrftoken = $.cookie('csrftoken');
    var profile_id = $("#profile_id").val();
    const html_form = document.getElementById('assembly_form');
    var fieldset = $("#assembly_form").find("input, select, textarea")
    const form = new FormData();
    for (f in fieldset) {
        field = fieldset[f]
        form.append(field.name, field.value)
    }

    var count = 0

    form.append("profile_id", profile_id)
    jQuery.ajax({
        url: '/copo/assembly_files/',
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


function doPost(evt) {
    evt.preventDefault()

    $("#submit_assembly_button").attr('disabled', 'disabled')
    $("input").attr("disabled", "disabled")
    $("select").attr("disabled", "disabled")
    $("textarea").attr("disabled", "disabled")
    $("#loading_span").fadeIn()
    upload_assembly_files()


}



