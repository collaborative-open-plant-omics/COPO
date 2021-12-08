$(document).ready(function () {

    console.log('wart')

    AutoComplete({
        EmptyMessage: "No item found",
        Url: "/copo/ajax_search_ontology/",
    }, "#xyz");

    var conf = {
        delimiter: "",	// auto-detect
        newline: "",	// auto-detect
        header: false,
        dynamicTyping: false,
        preview: 0,
        encoding: "",
        worker: false,
        comments: false,
        step: undefined,
        complete: do_json_stuff,
        error: undefined,
        download: false,
        skipEmptyLines: false,
        chunk: undefined,
        fastMode: undefined,
        beforeFirstChunk: undefined,
        withCredentials: undefined
    }

    $('input[type=file]').parse({
        config: conf,
        before: function (file, inputElem) {
            // executed before parsing each file begins;
            // what you return here controls the flow

        },
        error: function (err, file, inputElem, reason) {
            // executed if an error occurs while loading the file,
            // or if before callback aborted for some reason
        },
        complete: function (data) {
            // executed after all files are complete
            //$('#t1 th').annotator().annotator('setupPlugins', {}, {
            //    Auth: false,
            //    Permissions: false
            //})
            var content = $('#t1 th').annotator()
            content.annotator('addPlugin', 'StoreLogger')
        }
    });

    function do_json_stuff(data) {

        var cols = []
        d = data.data.slice(1, data.data.length)
        cols = data.data[0]
        c = []
        for (var x = 0; x < cols.length; x++) {
            c.push({'title': cols[x]})
        }
        $('#t1').DataTable({
            "data": d,
            "columns": c
        })
    }


})
