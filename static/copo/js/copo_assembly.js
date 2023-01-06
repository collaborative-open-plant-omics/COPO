function upload_assembly_files(file) {
    var csrftoken = $.cookie('csrftoken');
    var profile_id = $("#profile_id").val();
    form = new FormData();
    var count = 0
    for (f in file) {
        form.append(count.toString(), file[f])
        count++
    }
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