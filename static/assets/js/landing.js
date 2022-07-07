$(document).ready(function () {
    // Relates Manifests template wizard


    $(document).on("click", "#modalMultiStep", function () {
        $("#modalContent").modal("show")
        // Number of organisms
        var select = "";
        for (i = 1; i <= 100; i++) {
            select += "<option val=" + i + ">" + i + "</option>";
        }
        $("#numberOfSamples").html(select);

        var nStep = 5;
        var firstTab = $(".tab-pane:first-child").attr("id");
        var prevTab = $(".tab-pane.active")
            .prev()
            .attr("id");
        var nextTab = $(".tab-pane.active")
            .next()
            .attr("id");
        var lastTab = $(".tab-pane:last-child").attr("id");

        $(".progress-bar").text("Step 1 of " + nStep);
        $(".back, .first").hide();

        $(".next").click(function () {
            var nextId = $(".tab-pane.active")
                .next()
                .attr("id");
            // alert(nextId + ' ? ' + lastTab);
            $('[href="#' + nextId + '"]').tab("show");

            $(".back, .first").css("display", "unset");
            if (nextId == lastTab) {
                $(".next").hide();
                // show submit button
            }

            return false;
        });

        $(".back").click(function () {
            var backId = $(".tab-pane.active")
                .prev()
                .attr("id");
            // alert(backId);
            $('[href="#' + backId + '"]').tab("show");

            $(".next").css("display", "unset");
            if (backId === "step1") {
                $(".back, .first").css("display", "none");
            }

            return false;
        });

        $(".nav-tabs li:first-child").click(function () {
            $(".back, .first").css("display", "none");
            $(".next").css("display", "unset");
        });

        $(".nav-tabs li:not(:first-child)").click(function () {
            $(".back, .first").css("display", "unset");
        });

        $(".nav-tabs li:last-child").click(function () {
            $(".next").css("display", "none");
        });

        $(".nav-tabs li:not(:last-child)").click(function () {
            $(".next").css("display", "unset");
        });

        $('a[data-toggle="tab"]').on("shown.bs.tab", function (e) {
            var step = $(e.target).data("step");
            var percent = parseInt(step) / nStep * 100;

            $(".progress-bar").css({width: percent + "%"});
            $(".progress-bar").text("Step " + step + " of " + nStep);
        });

        $(".first").click(function () {
            $('[href="#' + firstTab + '"]').tab("show");
            $(".back, .first").css("display", "none");
            $(".next").css("display", "unset");
        });
    });


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