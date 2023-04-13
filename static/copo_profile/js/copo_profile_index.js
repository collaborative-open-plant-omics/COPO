$(document).ready(function () {
    //****************************** Event handlers block *************************//
    const component = "profile";
    const copoProfileIndexURL = "/copo/";
    const copoAcceptRejectURL = "/copo/accept_reject_sample"
    const copoSamplesURL = "/copo/copo_samples/"
    const copoENAReadManifestValidateURL = "/copo/ena_read_manifest_validate/"
    const copoENAAssemblyURL = "/copo/ena_assembly/"
    const copoVisualsURL = "/copo/copo_profile_visualise/";
    const tableLoader = $('<div class="copo-i-loader"></div>');
    const componentMeta = get_profile_component_meta(component);
    const tableID = componentMeta.tableID

    let page = 1;
    let block_request = false;
    let end_pagination = false;
    let grid_count = $('#grid-count');
    let grid_total = $('#grid-total');

    csrftoken = $.cookie('csrftoken');

    // Store the title displayed when a user hovers the ellipsis/profile options icon
    $(document).data("profileOptionsTitle", $('.row-ellipsis').attr('title'))

    // Add new profile button
    $(document).on("click", ".new-component-template", function () {
        initiate_profile_form_call(component);
    });

    // Display 'Accept/reject' button for sample managers
    for (let g in groups) {
        if (groups[g].includes("sample_managers")) {
            $("#accept_reject_shortcut").show()
            break;
        }
    }

    //display empty profile message for potential first time users
    set_empty_profile_component_message(profiles_total);

    // No profile records exist
    if (profiles.length === 0) {
        $("#bottom-panel").hide();
        return false;
    }
    // Profile records exist
    // Initialise the popover 'View profile options' for each profile record
    let popover = $('#ellipsisID[data-toggle="popover"]').popover({}).on('show.bs.popover', function (e) {
        // Set content of the popover
        const $content = $('<div></div>');
        const $editButton = $('<button id="editProfileBtn" class="btn btn-sm btn-success" title="Edit record"><i class="fa fa-pencil-square-o"></i>&nbsp;Edit</button>');
        const $deleteButton = $('<button id="deleteProfileBtn" class="btn btn-sm btn-danger" title="Delete record"><i class="fa fa-trash-o"></i>&nbsp;Delete</button>');

        $deleteButton.css('margin-left', '15px');

        $content.append($editButton);
        $content.append($deleteButton);

        // Apply the content to the popover
        popover.attr('data-content', $content.html());
    }).click(function (e) {
        $(this).popover('toggle');
        $('#ellipsisID[data-toggle="popover"]').not(this).popover('hide');
        e.stopPropagation();
    }).on('show.bs.popover', function (e) {
        $('.row-ellipsis').attr('title', '') // Hide 'View profile options' title from appearing in the popover on hover
    }).on('shown.bs.popover', function (e) {
        let profile_id = $(e.currentTarget).closest(".ellipsisDiv").attr("id");

        set_selected_profile_record($(e.currentTarget), tableID); // Highlight selected grid

        $('#editProfileBtn').click(function (event) {
            editProfileRecord(profile_id);
        });

        $('#deleteProfileBtn').click(function (event) {
            deleteProfileRecord(profile_id);
        });

        $('#popoverCloseBtn').click(function (event) {
            $('#ellipsisID[data-toggle="popover"]').popover('hide')
        });
    }).on('hide.bs.popover', function () {
        unselect_profile_record_on_dismiss(tableID);
    });


    $("#sortProfilesBtn")[0].selectedIndex = 0 // Set first option of sort menu

    grid_count.text(profiles.length); // Number of profile records visible
    grid_total.text(profiles_total); //  Total number of profile records for the user

    appendRecordComponents($('div.grid'))
    filter_action_menu();
    update_counts(copoVisualsURL, csrftoken, component);

    $('#sortProfilesBtn').on('change', function () {
        const option_selected = this.value;
        sort_profile_records(option_selected)

    });

    $(document).data("sortByDescendingOrder", true)

    $(document).on("click", "#accept_reject_shortcut", function () {
        document.location = copoAcceptRejectURL
    })

    $(document).on("click", ".expanding_menu > div", function (e) {
        const el = $(e.currentTarget);
        el.closest('.grid').removeClass("grid-selected")
        el.closest('.panel-heading').next('.grid-panel-body').removeClass("grid-panel-body-selected")
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

    // Toggle the visibility of the button to
    // sort in ascending order or descending order
    $(document).on("click", "#sortIconID", function (e) {
        let option = $("#sortProfilesBtn").val()

        $(this).toggleClass("sort-down fa fa-sort-down")
        $(this).toggleClass("sort-up fa fa-sort-up")

        if ($('i.sort-down').length) {
            $(document).data("sortByDescendingOrder", true)
            sort_profile_records(option)
        } else {
            $(document).data("sortByDescendingOrder", false)
            sort_profile_records(option)
        }

        e.preventDefault();
    });

    // Hide the profile options popover, display 'View profile options' on hover of the profile
    // options ellipsis icon and unhighlight focus on desired profile grid
    $(document).on("click", `#${tableID}`, function () {
        $('#ellipsisID[data-toggle="popover"]').popover('hide');
        $('.row-ellipsis').attr('title', $(document).data("profileOptionsTitle"))
        unselect_profile_record_on_dismiss(tableID);
    });

    $(document).on("click", ".copo-main", function () {
        $('#ellipsisID[data-toggle="popover"]').popover('hide');
        $('.row-ellipsis').attr('title', $(document).data("profileOptionsTitle"))
        unselect_profile_record_on_dismiss(tableID);
    });

    $(document).on("click", ".copo-sidebar", function () {
        $('#ellipsisID[data-toggle="popover"]').popover('hide');
        $('.row-ellipsis').attr('title', $(document).data("profileOptionsTitle"))
        unselect_profile_record_on_dismiss(tableID);
    });

    // Trigger infinite scroll once user scrolls downwards to display more profile records that exist
    $(window).scroll(function () {
        const margin = $(document).height() - $(window).height() - 200;

        // Scroll downwards
        if ($(window).scrollTop() > margin && end_pagination === false && block_request === false) {
            block_request = true;
            page += 1;

            $("#component_table_loader").append(tableLoader); // Show loading .gif

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

                    let content = $(data.content)

                    appendRecordComponents(content) // Adds 'Actions' and 'Components' buttons

                    // Appends the html template from the 'copo_profile_record.html' to the 'copo_profiels_table' div
                    $(`#${tableID}`).append(content);

                    // Initialise functions for the profile grids beyond the 8 records that are shown by default
                    refresh_profile_tool_tips(); // Refreshes/reloades/reinitialises all popover and dropdown functions
                    initialise_loaded_records(copoVisualsURL, csrftoken, component, tableID, copoSamplesURL, copoENAReadManifestValidateURL, copoENAAssemblyURL)

                    // Increment the number of profile records displayed
                    grid_count.text($('.grid').length)

                    tableLoader.remove(); // Remove loading .gif
                },
                error: function () {
                    alert("Couldn't retrieve profiles!");
                }
            })
        }
    });

    // Show a button which once a user hovers, it'll indicate that the
    // user can scroll downwards to view more profile records that were created
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
            // Show 'scroll up' button
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
        // $('.webui-popover').css("display", "none") // Hides tooltip which was still showing
    });

    // On web page reload/refresh, sort profile records by default sort option and method
    window.onload = () => {
        let option = $("#sortProfilesBtn").val()
        sort_profile_records(option)
    };

    // Programmatically scroll down the web page a little if a user decides to
    // click the button which indicates on hover to scroll down to view more profiles
    navigateToBottomOfPageBtn.click(function () {
        $('html, body').animate({
            scrollTop: document.body.scrollHeight + 30
        }, "slow");
        // $('.webui-popover').css("display", "none") // Hides tooltip which was still showing
        navigateToBottomOfPageBtn.removeClass('show') // Hide 'scroll down' button

    });

}); // End document ready

//****************************** Functions block ******************************//
function appendRecordComponents(grids) {
    // loop through each grid
    grids.each(function () {
        let record_id = $(this).closest('.grid').find('.row-title span').attr('id');

        // Add component buttons to the menu for each profile record
        let menu = $(this).closest('.grid').find('#expanding_menu')
        let component_buttons;
        $(menu).attr("id", "menu_" + record_id)
        component_buttons = append_component_buttons(record_id)
        $(menu).find(".comp").append(component_buttons)
    });

}

function editProfileRecord(profileRecordID) {
    const component = "profile";
    let copoFormsURL = "/copo/copo_profile_forms/";
    let csrftoken = $.cookie('csrftoken');

    $('#ellipsisID[data-toggle="popover"]').popover('hide'); // Hides the popover

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
            json2HtmlProfileForm(data);
        },
        error: function () {
            alert("Couldn't build profile form!");
        }
    });
}

function deleteProfileRecord(profileRecordID) {
    const component = "profile";
    const copoDeleteProfile = "/copo/delete_profile/";
    let csrftoken = $.cookie('csrftoken');

    $('#ellipsisID[data-toggle="popover"]').popover('hide'); // Hides the popover

    $.ajax({
        url: copoDeleteProfile,
        type: "POST",
        headers: {'X-CSRFToken': csrftoken},
        data: {
            'task': 'validate_and_delete',
            'component': component,
            'target_id': profileRecordID,
        }
    }).done(function () {
        BootstrapDialog.show({
            title: "Profile deleted",
            message: "Profile selected has been deleted. Web page will reload in 3 seconds.",
            cssClass: "copo-modal1",
            closable: true,
            animate: true,
            type: BootstrapDialog.TYPE_INFO
        });

        document.getElementById(profileRecordID).closest(".copo-records-panel").style.display = 'none';

        // Refresh web page to have change reflected after 3 seconds
        setTimeout(function () {
            window.location.reload();
        }, 3000);
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

function set_selected_profile_record(element, tableID) {
    const selected_grids = $(`#${tableID} div[class$='grid grid-selected']`);
    const selected_panels = $(".panel div[class$='panel-body grid-panel-body-selected']");

    // Check if any grid and panel-body are marked as 'selected',
    // if at least one exists, unselect it and select the current selected grid and panel-body
    if (selected_grids.length !== 0) {
        selected_grids.each(function (index, item) {
            item.classList.remove("grid-selected")
        })
    }

    if (selected_panels.length !== 0) {
        selected_panels.each(function (index, item) {
            item.classList.remove("grid-panel-body-selected");
        })
    }

    // Set grid and panel-body as selected
    $(element).closest('.grid').toggleClass("grid-selected")
    $(element).closest('.panel-heading').next('.grid-panel-body').toggleClass("grid-panel-body-selected")
}

function unselect_profile_record_on_dismiss(tableID) {
    const selected_grids = $(`#${tableID} div[class$='grid grid-selected']`);
    const selected_panels = $(".panel div[class$='panel-body grid-panel-body-selected']");

    // Check if any grid and panel-body are marked as 'selected',
    // if at least one exists, unselect it and select the current selected grid and panel-body
    if (selected_grids.length !== 0) {
        selected_grids.each(function (index, item) {
            item.classList.remove("grid-selected")
        })
    }

    if (selected_panels.length !== 0) {
        selected_panels.each(function (index, item) {
            item.classList.remove("grid-panel-body-selected");
        })
    }


}

function sort_profile_records(option) {
    // Determine the query selector
    let selector = element => new Date(element.querySelector('.grid-panel-body div:nth-child(2)').innerText).getTime(); // 'date_created' selector
    let isValueNumeric = false

    switch (option) {
        case "date_created":
            selector = element => new Date(element.querySelector('.grid-panel-body div:nth-child(2)').innerText).getTime();
            isValueNumeric = true;
            break;
        case "title":
            // Remove parentheses if present from title
            selector = element => element.querySelector('.row-title span').innerText.replace(/\s*\(.*?\)\s*/g, '')
            break;
        case "type":
            selector = element => element.querySelector('.copo-records-panel').getAttribute('profile_type');
            break;
        default:
            isValueNumeric = true;
            selector = element => new Date(element.querySelector('.grid-panel-body div:nth-child(2)').innerText).getTime();// 'date_created' selector
    }

    // Choose the order method
    const descendingOrder = $(document).data("sortByDescendingOrder");
    const isNumeric = isValueNumeric;

    // Select all (profile grid) elements
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

function append_component_buttons(record_id) {
    //components row
    const components = get_copo_profile_components();
    const componentsDIV = $('<div/>', {
        class: "item"
    });

    components.forEach(function (item) {
        //  skip profile entry metadata
        if (item.component === "profile") {
            return false;
        }

        let component_link = '#';

        try {
            component_link = $("#" + item.component + "_url").val().replace("999", record_id);
        } catch (err) {
            console.log(item.title);
        }

        // Create button html
        let pcomponent_count_span = $('<span></span>')
            .attr("class", "pcomponent-count")
            .attr("id", record_id + "_" + item.countsKey)
            .html('<i class="fa fa-spinner fa-pulse" style="font-size: 10px;"></i>')

        let pcomponent_count_div = $('<div></div>')
            .attr("class", `tiny ui basic pcomponent-color left pointing label ${item.color}`)
            .html(pcomponent_count_span);

        let pcomponent_name_div = $('<div></div>')
            .attr("class", `tiny ui button pcomponent-color ${item.color}`)
            .append('<i class="pcomponent-icon ' + item.iconClass + '"></i>')
            .append('<span class="pcomponent-name" style="padding-left: 3px;">' + item.title + '</span>');

        let buttonHTML = $('<a></a>')
            .attr("title", "Navigate to " + item.title)
            .attr("href", component_link)
            .attr("class", "tiny ui labeled button pcomponent-button")
            .attr("tabindex", "0")
            .css("margin", "3px")
            .append(pcomponent_name_div)
            .append(pcomponent_count_div);

        componentsDIV.append(buttonHTML);

    });

    return componentsDIV;
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

function initialise_loaded_records(copoVisualsURL, csrftoken, component, tableID, copoSamplesURL, copoENAReadManifestValidateURL, copoENAAssemblyURL) {
    filter_action_menu();
    update_counts(copoVisualsURL, csrftoken, component);

    $(".item a").click(function (e) {
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

    $(".expanding_menu > div").click(function (e) {
        const el = $(e.currentTarget);
        el.closest('.grid').removeClass("grid-selected")
        el.closest('.panel-heading').next('.grid-panel-body').removeClass("grid-panel-body-selected")
    })

    // Initialise the popover 'View profile options' for each profile record
    let popover = $('#ellipsisID[data-toggle="popover"]').popover({}).on('show.bs.popover', function (e) {
        // Set content of the popover
        const $content = $('<div></div>');
        const $editButton = $('<button id="editProfileBtn" class="btn btn-sm btn-success" title="Edit record"><i class="fa fa-pencil-square-o"></i>&nbsp;Edit</button>');
        const $deleteButton = $('<button id="deleteProfileBtn" class="btn btn-sm btn-danger" title="Delete record"><i class="fa fa-trash-o"></i>&nbsp;Delete</button>');

        $deleteButton.css('margin-left', '15px');

        $content.append($editButton);
        $content.append($deleteButton);

        // Apply the content to the popover
        popover.attr('data-content', $content.html());
    }).click(function (e) {
        $(this).popover('toggle');
        $('#ellipsisID').not(this).popover('hide');
        e.stopPropagation();
    }).on('show.bs.popover', function (e) {

        $('.row-ellipsis').attr('title', '') // Hide 'View profile options' title from appearing in the popover on hover
    }).on('shown.bs.popover', function (e) {
        let profile_id = $(e.currentTarget).closest(".ellipsisDiv").attr("id");

        set_selected_profile_record($(e.currentTarget), tableID); // Highlight selected grid

        $('#editProfileBtn').click(function (event) {
            editProfileRecord(profile_id);
        });

        $('#deleteProfileBtn').click(function (event) {
            deleteProfileRecord(profile_id);
        });

        $('#popoverCloseBtn').click(function (event) {
            $('#ellipsisID[data-toggle="popover"]').popover('hide')
        });
    }).on('hide.bs.popover', function () {
        unselect_profile_record_on_dismiss(tableID);
    });
}