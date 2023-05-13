$(document).ready(function () {
    $(document).on("click", ".card", function () {
        window.location = "/copo/stats#"
    })

    // $('.ui.dropdown').dropdown();
    const image = getRandomInt(images.length);
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
        }).fail(function (data) {
        console.log(data)
    })
    setActiveNavItem() // Set current web page as active nav bar item in top navbar
});

function getRandomInt(max) {
    return Math.floor(Math.random() * Math.floor(max));
}

function setActiveNavItem() {
    const activePage = window.location.href;

    $('.nav li a').filter(function () {
        let linkPage = `${this.href}/`;
        // home page i.e. COPO front page URL will end with '//' so it needs to be ommitted
        linkPage = linkPage.endsWith('//') ? this.href : linkPage;

        if (activePage === linkPage) {
            $(this).parent().addClass("active");
            $(this).parent().append('<span class="sr-only">(current)</span>')
        }
    });
}
