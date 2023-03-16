$(document).ready(function () {
    //****************************** Event handlers block *************************//
    // Get data to display
    const component = "profile";
    const componentMeta = get_component_meta(component);
    const copoFormsURL = "/copo/copo_forms/";
    const copoVisualsURL = "/copo/copo_visualize/";
    const copoDeleteProfile = "/copo/delete_profile/";
    const copoProfileIndexURL = "/copo/";
    const copoAcceptRejectURL = "/copo/accept_reject_sample"
    const copoSamplesURL = "/copo/copo_samples/"
    const copoENAReadManifestValidateURL = "/copo/ena_read_manifest_validate/"
    const copoENAAssemblyURL = "/copo/ena_assembly/"
    const tableLoader = $('<div class="copo-i-loader"></div>');
    let body = $('body')
    let page = 1;
    let block_request = false;
    let end_pagination = false;
    let grid_count = $('#grid-count');
    let grid_total = $('#grid-total');

    csrftoken = $.cookie('csrftoken');

    // Load work profiles
    // If there are no profiles, display an empty profile message else show loader
    if (profiles.length === 0) {
        console.log('No records to show')
    } else {
        $("#component_table_loader").append(tableLoader);
        tableLoader.remove();
    }

    // Groups
    for (let g in groups) {
        if (groups[g].includes("sample_managers")) {
            $("#accept_reject_shortcut").show()
            break;
        }
    }

    $('a').webuiPopover({closeable: true}); // Initialises the popover option for each profile record

    $("#sortProfilesBtn")[0].selectedIndex = 0 // Set first option of sort menu

    set_empty_component_message(profiles_total); // Display an empty profile message for potential first time users

    grid_count.text(profiles.length); // Number of profile records visible
    grid_total.text(profiles_total); //  Total number of profile records for the user
    filter_action_menu();

    // Trigger refresh of profiles list
    body.on('refreshtable', function () {
        tableLoader.remove();
        filter_action_menu();
    });

    $(document).data("sortByDescendingOrder", true)

    $(document).on("click", "#accept_reject_shortcut", function () {
        document.location = copoAcceptRejectURL
    })

    $(document).on("click", ".expanding_menu > div", function (e) {
        const el = $(e.currentTarget);
        el.closest("tr").removeClass("selected")
    })

    $(document).on("click", ".item a", function (e) {
        let url;
        const el = $(e.currentTarget);
        if (el.hasClass("action")) {
            const action_type = el.data("action_type");
            let id = el.closest(".expanding_menu").attr("id");
            id = id.split("_")[1]
            if (action_type === "dtol" || action_type === "erga") {
                url = copoSamplesURL + id + "/view"
            } else if (action_type === "reads") {
                url = copoENAReadManifestValidateURL + id
            } else if (action_type === "assembly") {
                url = copoENAAssemblyURL + id
            }
            document.location = url
        }
    })

    // Toggle the visibility of the button to sort in
    // ascending order and descending order
    $(document).on("click", "#sortIconID", function (e) {
        $(this).toggleClass("sort-down fa fa-sort-down")
        $(this).toggleClass("sort-up fa fa-sort-up")

        if ($('i.sort-down').length) {
            $(document).data("sortByDescendingOrder", true)
        } else {
            $(document).data("sortByDescendingOrder", false)
        }

        e.preventDefault();
    });

    $('#sortProfilesBtn').on('change', function (e) {
        const option_selected = this.value;
        sortProfiles(option_selected)

    });

    $(document).on("click", "#copo_profiles_table", unselect_profile_record_on_dimiss)

    $(document).on("click", ".copo-main", unselect_profile_record_on_dimiss)

    $(document).on("click", ".copo-sidebar", unselect_profile_record_on_dimiss)

    // Add new profile button
    $(document).on("click", ".new-component-template", function () {
        initiate_form_call(component);
    });

    // Show the option to edit/delete a profile record
    // once the vertical ellipsis is clicked

    // Profiles - Trigger infinite scroll once user scrolls downwards and display more profile records
    $(window).scroll(function () {
        const margin = $(document).height() - $(window).height() - 200;
        // Scroll downwards
        if ($(window).scrollTop() > margin && end_pagination === false && block_request === false) {
            block_request = true;
            page += 1;

            $.ajax({
                type: 'GET',
                url: copoProfileIndexURL,
                data: {
                    "page": page
                },
                success: function (data) {
                    if (data.end_pagination === true) {
                        end_pagination = true;
                    } else {
                        block_request = false;
                    }
                    // Appends the html template from the 'copo_profile_record.html' to the 'copo_profiels_table' div
                    $('#copo_profiles_table').append(data.content);

                    // Increment the number profile records displayed
                    grid_count.text($('.grid').length)
                    // tableLoader.remove();
                },
                error: function () {
                    alert("Couldn't retrieve profiles!");
                }
            })
        }

    });

    // Scroll to the bottom of the web page on button clicked
    let navigateToBottomOfPageBtn = $('#navigateToBottom');

    grid_count.text() < grid_total.text() && $(window).scrollTop() < 100
        ? navigateToBottomOfPageBtn.addClass('show')
        : navigateToBottomOfPageBtn.removeClass('show')


    // Navigate to the top of the web page on button clicked
    let navigateToTopOfPageBtn = $('#navigateToTop');

    $(window).on('scroll', function () {
        if ($(window).scrollTop() > 100) {
            // Hide the 'scroll down' button
            if (navigateToBottomOfPageBtn.hasClass('show')) navigateToBottomOfPageBtn.removeClass('show');
            navigateToTopOfPageBtn.addClass('show');
        } else {
            navigateToTopOfPageBtn.removeClass('show');
        }
    });

    navigateToTopOfPageBtn.on('click', function (e) {
        e.preventDefault();
        $('html, body').animate({
            scrollTop: 0
        }, '300');
    });
}); // End document ready

//****************************** Functions Block ******************************//
function editProfileRecord(profileRecordID) {
    $('a').webuiPopover('hide'); // Hides the popover
    const component = "profile";
    const copoFormsURL = "/copo/copo_forms/";
    let csrftoken = $.cookie('csrftoken');

    $.ajax({
        url: copoFormsURL,
        type: "POST",
        headers: {'X-CSRFToken': csrftoken},
        data: {
            'task': 'form',
            'component': component,
            'target_id': profileRecordID
        },
        success: function (data) {
            json2HtmlForm(data);
        },
        error: function () {
            alert("Couldn't build profile form!");
        }
    });
}

function deleteProfileRecord(profileRecordID) {
    $('a').webuiPopover('hide'); // Hides the popover
    const component = "profile";
    const copoDeleteProfile = "/copo/delete_profile/";
    let csrftoken = $.cookie('csrftoken');

    $.ajax({
        url: copoDeleteProfile,
        type: "POST",
        headers: {'X-CSRFToken': csrftoken},
        data: {
            'task': 'validate_and_delete',
            'componenent': component,
            'target_id': profileRecordID,
        }
    }).done(function () {
        BootstrapDialog.show({
            title: "Profile deleted",
            message: "Profile selected has been deleted.",
            cssClass: "copo-modal1",
            closable: true,
            animate: true,
            type: BootstrapDialog.TYPE_INFO
        });

        document.getElementById(profileRecordID).closest(".copo-records-panel").style.display = 'none';
    }).error(function (data_response) {
        BootstrapDialog.show({
            title: "Profile deletion - error",
            message: "Profile couldn't be removed. Only profiles that have no datafiles or " +
                "samples associated can be deleted.",
            cssClass: "copo-modal1",
            closable: true,
            animate: true,
            type: BootstrapDialog.TYPE_DANGER
        });
        if (!data_response.responseJSON["undeleted"].includes(profileRecordID)) {
            document.getElementById(profileRecordID).closest(".copo-records-panel").style.display = 'none';
        }

        console.log(data_response)
    });

}

function set_selected_profile_record(element) {
    console.log('I am clicked')
    const selected_grids = $("#copo_profiles_table div[class$='grid grid-selected']");
    const selected_panels = $(".panel div[class$='panel-body panel-body-selected']");

    // Check if any grid and panel-body are marked as 'selected',
    // if at least one exists, unselect it and select the current selected grid and panel-body

    if (selected_grids.length !== 0) {
        console.log("selected grid exists")
        selected_grids.each(function (index, item) {
            console.log(item)
            item.classList.remove("grid-selected")

        })
    }

    if (selected_panels.length !== 0) {
        console.log("selected panel exists")
        selected_panels.each(function (index, item) {
            item.classList.remove("panel-body-selected");

        })
    }

    // Set grid and panel-body as selected
    $(element).closest('.grid').toggleClass("grid-selected")
    $(element).closest('.panel-heading').next('.panel-body').toggleClass("panel-body-selected")


    // set_selected_rows(dt); // Highlight selected grid
}

function unselect_profile_record_on_dimiss() {
    const selected_grids = $("#copo_profiles_table div[class$='grid grid-selected']");
    const selected_panels = $(".panel div[class$='panel-body panel-body-selected']");

    // Check if any grid and panel-body are marked as 'selected',
    // if at least one exists, unselect it and select the current selected grid and panel-body

    if (selected_grids.length !== 0) {
        console.log("selected grid exists")
        selected_grids.each(function (index, item) {
            item.classList.remove("grid-selected")

        })
    }
    if (selected_panels.length !== 0) {
        console.log("selected panel exists")
        selected_panels.each(function (index, item) {
            item.classList.remove("panel-body-selected");

        })
    }
}

function sortProfiles(option) {
    console.log('Value selected', option)
    console.log('Sorting by descending order?', $(document).data("sortByDescendingOrder"))

    // Determine the selector
    let selector = document.querySelector('.panel-body div:nth-child(2)').innerText; // date_created selector
    switch (option) {
        case "date_created":
            selector = document.querySelector('.panel-body div:nth-child(2)').innerText;
            break;
        case "title":
            selector = document.querySelector('.row-title span').innerText;
            selector.replace(/\s*\(.*?\)\s*/g, '') // Remove parentheses if present
            break;
        case "type":
            selector = element => element.querySelector('.copo-records-panel').getAttribute('profile_type');
            break;
        default:
            selector = document.querySelector('.panel-body div:nth-child(2)').innerText;// date_created selector
    }


    // Choose the order method
    const descendingOrder = $(document).data("sortByDescendingOrder"); // ascendingOrder ? [elementA, elementB] : [elementB, elementA];
    const isNumeric = false;

    // Select all elements
    const elements = [...document.querySelectorAll('.grid')];

    // Find parent node
    const parentElement = elements[0].parentNode;

    // Sort the elements
    const collator = new Intl.Collator(undefined, {numeric: isNumeric, sensitivity: 'base'});

    elements
        .sort((elementA, elementB) => {
            const [firstElement, secondElement] = descendingOrder ? [elementB, elementA] : [elementA, elementB];
            const textOfFirstElement = selector(firstElement);
            const textOfSecondElement = selector(secondElement);
            return collator.compare(textOfFirstElement, textOfSecondElement)
        })
        .forEach(element => parentElement.appendChild(element));

}

function do_render_profile_counts(data) {
    if (data.profiles_counts) {
        const stats = data.profiles_counts;

        for (let i = 0; i < stats.length; ++i) {
            const stats_id = stats[i].profile_id + "_";
            if (stats[i].counts) {
                for (let k in stats[i].counts) {
                    if (stats[i].counts.hasOwnProperty(k)) {
                        const count_id = stats_id + k;
                        $("#" + count_id).html(stats[i].counts[k]);
                    }
                }
            }
        }
    }
}

function update_counts(copoVisualsURL, csrftoken, component) {
    $.ajax({
        url: copoVisualsURL,
        type: "POST",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            'task': 'profiles_counts',
            'component': component
        },
        success: function (data) {
            do_render_profile_counts(data);
        },
        error: function () {
            alert("Couldn't retrieve profiles information!");
        }
    });
}

function filter_action_menu() {
    $(".copo-records-panel").each(function (idx, el) {
        const t = $(el).attr("profile_type");
        if (t.includes("ERGA")) {
            $(el).find("a[anchor_type='reads']").hide()
            $(el).find("a[anchor_type='assembly']").hide()
            $(el).find("a[anchor_type='dtol_option']").hide()
        } else if (t.includes("DTOL") || t.includes("ASG")) {
            $(el).find("a[anchor_type='reads']").hide()
            $(el).find("a[anchor_type='assembly']").hide()
            $(el).find("a[anchor_type='erga_option']").hide()
        } else if (t.includes("Stand-alone")) {
            $(el).find("a[anchor_type='dtol_option']").hide()
            $(el).find("a[anchor_type='erga_option']").hide()
        }
    })
}

// function do_record_task(event, component, copoDeleteProfile, copoFormsURL) {
//     let csrftoken;
//     const task = event.task.toLowerCase(); //action to be performed e.g., 'Edit', 'Delete'
//     const tableID = event.tableID; //get target table
//
//     //retrieve target records and execute task
//     const table = $('#' + tableID).DataTable();
//     const records = []; //
//     $.map(table.rows('.selected').data(), function (item) {
//         records.push(item);
//     });
//
//     //add task
//     if (task === "add") {
//         initiate_form_call(component);
//
//         return false;
//     }
//
//
//     //edit task
//     if (task === "edit") {
//         csrftoken = $.cookie('csrftoken');
//         $.ajax({
//             url: copoFormsURL,
//             type: "POST",
//             headers: {'X-CSRFToken': csrftoken},
//             data: {
//                 'task': 'form',
//                 'component': component,
//                 'target_id': records[0].record_id // only allowing row action for edit, hence first record taken as target
//             },
//             success: function (data) {
//                 json2HtmlForm(data);
//             },
//             error: function () {
//                 alert("Couldn't build profile form!");
//             }
//         });
//     }
//
//     //delete task
//     if (task === "validate_and_delete") {
//         csrftoken = $.cookie('csrftoken');
//         $.ajax({
//             url: copoDeleteProfile,
//             type: "POST",
//             headers: {'X-CSRFToken': csrftoken},
//             data: {
//                 'task': 'validate_and_delete',
//                 'componenent': component,
//                 'target_id': records, //maybe i need to make a list of all record_id in records
//             }
//         }).done(function () {
//             BootstrapDialog.show({
//                 title: "Profile/s deleted",
//                 message: "All profile/s selected have been deleted.",
//                 cssClass: "copo-modal1",
//                 closable: true,
//                 animate: true,
//                 type: BootstrapDialog.TYPE_INFO
//             });
//             for (let i = 0; i < records.length; i++) {
//                 document.getElementById(records[i]["record_id"]).closest(".copo-records-panel").style.display = 'none';
//             }
//         }).error(function (data_response) {
//             BootstrapDialog.show({
//                 title: "Profile deletion - error",
//                 message: "One or more profiles couldn't be removed. Only profiles that have no datafiles or " +
//                     "samples associated can be deleted.",
//                 cssClass: "copo-modal1",
//                 closable: true,
//                 animate: true,
//                 type: BootstrapDialog.TYPE_DANGER
//             });
//             for (let i = 0; i < records.length; i++) {
//                 if (!data_response.responseJSON["undeleted"].includes(records[i]["record_id"])) {
//                     document.getElementById(records[i]["record_id"]).closest(".copo-records-panel").style.display = 'none';
//                 }
//             }
//             console.log(data_response)
//         });
//     }
//
//     //table.rows().deselect(); //deselect all rows
//
//     //handle button actions
//     // if (ids.length > 0) {
//     //     if (task == "edit") {
//     //         $.ajax({
//     //             url: copoFormsURL,
//     //             type: "POST",
//     //             headers: {'X-CSRFToken': csrftoken},
//     //             data: {
//     //                 'task': 'form',
//     //                 'component': component,
//     //                 'target_id': ids[0] //only allowing row action for edit, hence first record taken as target
//     //             },
//     //             success: function (data) {
//     //                 json2HtmlForm(data);
//     //             },
//     //             error: function () {
//     //                 alert("Couldn't build publication form!");
//     //             }
//     //         });
//     //     } else if (task == "delete") { //handles delete, allows multiple row delete
//     //         var deleteParams = {component: component, target_ids: ids};
//     //         do_component_delete_confirmation(deleteParams);
//     //     }
//     // }
// }
//
