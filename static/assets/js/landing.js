$(document).ready(function () {


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

    $.getJSON("api/stats/numbers")
        .done(function (data) {
            $("#num_samples").html(data.samples)
            $("#num_profiles").html(data.profiles)
            $("#num_users").html(data.users)
            $("#num_uploads").html(data.datafiles)
        }).error(function (data) {
        console.log(data)
    })

})

function getRandomInt(max) {
    return Math.floor(Math.random() * Math.floor(max));
}