/**
 * Created by fshaw on 08/09/2017.
 */
$(document).ready(function () {
        var csrftoken = $.cookie('csrftoken');
        $(document).on('click', '#import-button', function (el) {
            text = $('#accessions-text-area').val()
            $.ajax({
                url: '/copo/import_ena_accession/',
                type: 'post',
                headers: {'X-CSRFToken': csrftoken},
                data: {'accessions': text},
                dataType: 'json',
            }).done(function (data) {
                console.log(data)
            })
        })
    }
)