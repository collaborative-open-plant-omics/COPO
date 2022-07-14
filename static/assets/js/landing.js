$(document).ready(function () {
    // Manifest webpage
    // Trigger manifest wizard modal
    $(document).on("click", "#show_manifest_wzd_button", function (e) {
        $("#modal-wizard").modal("show");
    });
    // Number of organisms/samples/rows step
    var select = "";
    for (let i = 1; i <= 100; i++) {
        select += "<option val=" + i + ">" + i + "</option>";
    }
    $("#numberOfSamples").html(select);

    // Generate a dropdown menu for common field values
    $("#commonvalue").selectpicker();
    // Hides the modal and clear the data within the modal
    // after the "ok" button is clicked in the popup dialog
    $(document).on("click", ".okbtn", function (e) {
        $('#manifestType').val([]);
        $('#numberOfSamples').val([1]);
        $('#commonvalue').val([]);
        $("#modal-wizard").modal("hide");
    });

    // Other code
    $(document).on("click", ".card", function () {
        window.location = "/copo/stats#"
    })

    $('.ui.dropdown').dropdown();
    var image = getRandomInt(images.length)
    $('body').css("background-image", "url(" + images[image] + ")")

    try {
        var color = getRandomInt(content_classes.length)
        $("#main_banner").addClass(content_classes[color])
    } catch (err) {

    }

    // $.getJSON("api/stats/numbers")
    //     .done(function (data) {
    //         $("#num_samples").html(data.samples)
    //         $("#num_profiles").html(data.profiles)
    //         $("#num_users").html(data.users)
    //         $("#num_uploads").html(data.datafiles)
    //     }).error(function (data) {
    //     console.log(data)
    // })

});

function getRandomInt(max) {
    return Math.floor(Math.random() * Math.floor(max));
}