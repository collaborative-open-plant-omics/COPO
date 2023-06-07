/**
 * felix.shaw@tgac.ac.uk - 27/10/15.
 */
$(document).ready(function () {
    apply_color();

    $('body').on('change', apply_color())

});


function apply_color() {
    const loc = window.location.href;
    if (loc.indexOf("publication") > -1) {
        // act on publications page
        $('header').addClass('pubs_color')
    } else if (loc.indexOf("samples") > -1) {
        $('header').addClass('samples_color')
    } else if (loc.indexOf("accessions") > -1) {
        $('header').addClass('$accessions_color')
    } else if (loc.indexOf("submissions") > -1) {
        $('header').addClass('submissions_color')
    } else if (loc.indexOf("people") > -1) {
        $('header').addClass('people_color')
    } else if (loc.indexOf("data") > -1) {
        // act on data page
        $('header').addClass('data_color');
        $('.copo-panel-title').addClass('data_color');
    }
}