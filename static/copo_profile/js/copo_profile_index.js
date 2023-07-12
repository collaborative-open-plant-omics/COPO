$(document).ready(function () {
    //****************************** Event handlers block *************************//
    const component = "profile";
    const copoProfileIndexURL = "/copo/";
    const copoAcceptRejectURL = "/copo/accept_reject_sample"
    const copoAccessionsDashboardURL = "/copo/dashboard/accessions"
    const copoTolDashboardURL = "/copo/dashboard/tol"
    const copoSamplesURL = "/copo/copo_samples/"
    const copoENAReadManifestValidateURL = "/copo/copo_reads/"
    const copoENAAssemblyURL = "/copo/copo_assembly/"
    const copoENAAnnotationURL = "/copo/copo_seq_annotation/"
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

    // Show web page buttons according to the group that the users are associated with
    if (groups.length === 0) {
        $("#copo_accessions_dashboard_shortcut").show() // Show 'Accessions tol_dashboard' button for all users
        $("#copo_tol_dashboard_shortcut").show() // Show 'Tree of life tol_dashboard' button for all users
    } else {
        for (let g in groups) {
            // Display 'Accept/reject' button for sample managers
            if (groups[g].includes("sample_managers")) {
                $("#accept_reject_shortcut").show()
                break;
            }
            $("#copo_accessions_dashboard_shortcut").show() // Show 'Accessions tol_dashboard' button for all users
            $("#copo_tol_dashboard_shortcut").show() // Show 'Tree of life tol_dashboard' button for all users
        }
    }

    //display empty profile message for potential first time users
    set_empty_profile_component_message(profiles_total);

    // No profile records exist
    if (profiles.length === 0) {
        $("#bottom-panel").hide();
        $(".profiles-legend").hide();
        $(".other-projects-accessions-filter-checkboxes").hide();
        return false;
    }

    // Profile records exist
    // Initialise the popover 'View profile options' for each profile record
    let popover = $('#ellipsisID[data-toggle="popover"]').popover({
        sanitize: false
    }).click(function (e) {
        $(this).popover('toggle');
        $('#ellipsisID[data-toggle="popover"]').not(this).popover('hide');
        e.stopPropagation();
    }).on('show.bs.popover', function (e) {
        $('.row-ellipsis').attr('title', '') // Hide 'View profile options' title from appearing in the popover on hover
    }).on('show.bs.popover', function (e) {
        // Set content of the popover
        const $content = $('<div></div>');
        const $editButton = $('<button id="editProfileBtn" class="btn btn-sm btn-success" title="Edit record"><i class="fa fa-pencil-square-o"></i>&nbsp;Edit</button>');
        const $deleteButton = $('<button id="deleteProfileBtn" class="btn btn-sm btn-danger" title="Delete record"><i class="fa fa-trash-o"></i>&nbsp;Delete</button>');

        $deleteButton.css('margin-left', '15px');
        $content.append($editButton);
        $content.append($deleteButton);

        // Apply the content to the popover
        popover.attr('data-content', $content.html());
    }).on('shown.bs.popover', function (e) {
        $('.row-ellipsis').attr('title', '') // Hide 'View profile options' title from appearing in the popover on hover
    });

    $("#sortProfilesBtn")[0].selectedIndex = 0 // Set first option of sort menu

    grid_count.text(profiles.length); // Number of profile records visible
    grid_total.text(profiles_total); //  Total number of profile records for the user

    let div_grid = $('div.grid')

    appendRecordComponents(div_grid)
    filter_action_menu();
    update_counts(copoVisualsURL, csrftoken, component);

    set_profile_grid_heading(div_grid) // Set profile grid heading

    // Adjust margin-bottom for associated types when profile description appears on 2 lines
    set_associated_types_marginBottom()

    set_mediaQueries() // Set media queries for profile records

    $('#sortProfilesBtn').on('change', function () {
        const option_selected = this.value;
        sort_profile_records(option_selected)

    });

    $(document).data("sortByDescendingOrder", true)

    $(document).on("click", "#accept_reject_shortcut", function () {
        document.location = copoAcceptRejectURL
    })

    $(document).on("click", "#copo_tol_dashboard_shortcut", function (evt) {
        document.location = copoTolDashboardURL
    })

    $(document).on("click", "#copo_accessions_dashboard_shortcut", function (evt) {
        document.location = copoAccessionsDashboardURL
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
            } /*else if (action_type === "reads") {
                url = copoENAReadManifestValidateURL + id + "/view"
            } else if (action_type === "assembly") {
                url = copoENAAssemblyURL + id + "/view"
            } else if (action_type === "annotation") {
                url = copoENAAnnotationURL + id + "/view"
            }*/ else {
                url = "/copo/copo_" + action_type + "/" + id + "/view"
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
    });

    $(document).on("click", ".copo-main", function () {
        $('#ellipsisID[data-toggle="popover"]').popover('hide');
        $('.row-ellipsis').attr('title', $(document).data("profileOptionsTitle"))
    });

    $(document).on("click", ".copo-sidebar", function () {
        $('#ellipsisID[data-toggle="popover"]').popover('hide');
        $('.row-ellipsis').attr('title', $(document).data("profileOptionsTitle"))
    });

    $(document).on("click", "#editProfileBtn", function (e) {
        let profile_id = $(e.currentTarget).closest(".ellipsisDiv").attr("id");
        editProfileRecord(profile_id);
    });

    $(document).on("click", "#deleteProfileBtn", function (e) {
        let profile_id = $(e.currentTarget).closest(".ellipsisDiv").attr("id");
        deleteProfileRecord(profile_id);
    });

    $(document).on("click", "#popoverCloseBtn", function () {
        $('#ellipsisID[data-toggle="popover"]').popover('hide')
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
                    initialise_loaded_records(copoVisualsURL, csrftoken, component, tableID, copoSamplesURL, copoENAReadManifestValidateURL, copoENAAssemblyURL, copoENAAnnotationURL); // Initialise functions for the profile grids beyond the 8 records that are shown by default

                    set_profile_grid_heading(content) // Set profile grid heading
                    // Adjust margin-bottom for associated types when profile description appears on 2 lines
                    set_associated_types_marginBottom()

                    set_mediaQueries() // Set media queries for profile records
                    grid_count.text($('.grid').length) // Increment the number of profile records displayed
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
        navigateToBottomOfPageBtn.removeClass('show') // Hide 'scroll down' button
    });

}); // End document ready

//****************************** Functions block ******************************//
function appendRecordComponents(grids) {
    // loop through each grid
    grids.each(function () {
        let record_id = $(this).closest('.grid').find('.row-title span').attr('id');
        let profile_type = $(this).closest('.grid').find('.copo-records-panel').attr('profile_type');
        if (profile_type) {
            profile_type = profile_type.toLowerCase().trim();
        }
        // Add component buttons to the menu for each profile record
        let menu = $(this).closest('.grid').find('#expanding_menu')
        let component_buttons;
        $(menu).attr("id", "menu_" + record_id)
        component_buttons = append_component_buttons(record_id, profile_type)
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

    // Show a modal dialog to confirm if a user would like to delete the profile
    BootstrapDialog.show({

        title: "Delete Profile",
        message: "<b>Are you sure that you would like this profile to be deleted?</b>" +
            "</br></br>You<strong> would not</strong> be able to retrieve the profile after it has been deleted.",
        cssClass: "copo-modal1",
        closable: false,
        animate: true,
        type: BootstrapDialog.TYPE_WARNING,
        buttons: [
            {
                label: "Cancel",
                cssClass: "tiny ui basic button",
                action: function (dialogRef) {
                    dialogRef.close();
                }
            },
            {
                label: "Confirm",
                cssClass: "tiny ui basic button dialog_confirm",
                action: function (dialogRef) {
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
                        // Delete the profile
                        BootstrapDialog.show({
                            title: "Profile deleted",
                            message: "Profile has been deleted. Web page will reload in 3 seconds.",
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
                        const message = "Profile couldn't be removed. Only profiles that have no datafiles or" +
                            " samples associated can be deleted.";
                        let $content = '<div>';

                        $content += '<div style="margin-bottom: 10px; padding-bottom: 15px; font-weight: bold">' + message + '</div>';
                        $content += '<p style="margin-top:10px">Please contact '
                        $content += '<a style="text-decoration: underline;" href="mailto:EI.COPO@earlham.ac.uk">EI.COPO@earlham.ac.uk</a> '
                        $content += 'if you would like this profile to be deleted.</p>';
                        $content += '</div>';

                        BootstrapDialog.show({
                            title: "Profile deletion - error",
                            message: $content,
                            cssClass: "copo-modal1",
                            closable: true,
                            animate: true,
                            type: BootstrapDialog.TYPE_DANGER
                        });
                    });
                }
            }
        ]
    })
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

function display_profiles_legend(legend_data) {
    $.each(legend_data, function (index, element) {
        let type = element.profileType;
        let acronym = element.profileTypeAcronym;
        let colour = element.profileTypeColour;

        // Create profile type legend item
        let $legendItem = '<li class="profiles-legend-group-item">'
        $legendItem += '<i class= "fa fa-info-circle profiles-legend-info-icon" title= "' + type + '"> </i>'
        $legendItem += '<span class="fa fa-circle profiles-legend-circle" style="color:' + colour + '"></span>'
        $legendItem += acronym
        $legendItem += '</li>'

        $(".profiles-legend").find('.profiles-legend-group').append($legendItem)
    });
}

function set_copo_sidebar_info_padding() {
    if ($('#page_alert_panel').text().trim() === "") {
        $('.copo-sidebar-tabs').find('#profilesLegendDivID').css('padding-top', '100px');
    } else {
        $('#profilesLegendDivID').css('padding-top', '0');
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

function append_component_buttons(record_id, profile_type) {
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

        if (!item.hasOwnProperty("profile_component") || (profile_type === "stand-alone" && !item.profile_component.includes("stand-alone")) || (profile_type !== "stand-alone" && item.profile_component.includes("stand-alone"))) {
            return false;
        }

        let component_link = '#';

        try {
            component_link = $("#" + item.component + "_url").val().replace("999", record_id);
        } catch (err) {
            console.log(item.title);
        }

        // Create button html
        let pcomponent_count_span = $("<span></span>")
        if (item.countsKey) {
            pcomponent_count_span = $('<span></span>')
                .attr("class", "pcomponent-count")
                .attr("id", record_id + "_" + item.countsKey)
                .html('<i class="fa fa-spinner fa-pulse" style="font-size: 10px;"></i>')
        }

        let pcomponent_count_div = $('<div></div>')

        // Do not show the count for "accessions" component and "files" component
        if (item.component !== "accessions" && item.component !== "files") {
            pcomponent_count_div.attr("class", `tiny ui basic pcomponent-color left pointing label ${item.color}`)
                .html(pcomponent_count_span);
        }

        let pcomponent_name_div = $('<div></div>')
            .attr("class", `tiny ui button pcomponent-color ${item.color}`)
            .append('<i class="pcomponent-icon ' + item.iconClass + '"></i>')
            .append('<span class="pcomponent-name" style="padding-left: 3px;">' + item.title + '</span>');

        // Add border radius to "accessions" component and "files" component
        if (item.component === "accessions" || item.component === "files") {
            pcomponent_name_div.css("border-radius", ".28571429rem")
        }

        let buttonHTML = $('<a></a>')
            .attr("title", "Navigate to " + item.title)
            .attr("href", component_link)
            .attr("class", "tiny ui labeled button pcomponent-button")
            .attr("tabindex", "0")
            .css("margin", "3px 15px 3px 3px") // Set the component buttons to the same width // css("margin", "3px")
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
            $(el).find("a[profile_component='stand-alone']").hide()
            $(el).find("a[profile_component='dtol']").hide()
        } else if (t.includes("DTOL") || t.includes("ASG")) {
            $(el).find("a[profile_component='stand-alone']").hide()
            $(el).find("a[profile_component='erga']").hide()
        } else if (t.includes("Stand-alone")) {
            $(el).find("a[profile_component='dtol']").hide()
            $(el).find("a[profile_component='erga']").hide()
        }
    })
}

function set_mediaQueries() {
    // Add responsiveness to profile grids once web page screen size is changed
    const screenSize_lst = [
        window.matchMedia("(max-width: 1908px)"),
        window.matchMedia("(max-width: 1901px)"),
        window.matchMedia("(max-width: 1893px)"),
        window.matchMedia("(max-width: 1818px)"),
        window.matchMedia("(max-width: 1564px)")
    ]

    // Attach listener function on state changes
    $.each(screenSize_lst, function (index, element) {
        element.addEventListener('change', (e) => {
            set_associated_types_marginBottom()
        });
    });
}

function set_profile_grid_heading(grids) {
    let profiles_legend_lst = []

    grids.each(function () {
        $(this).find(".copo-records-panel").each(function (idx, el) {
            const profile_type = $(el).attr("profile_type");
            let colour;
            let acronym;
            let legend_data;
            let current_profile_legendData = $(".profiles-legend-group-item").text()

            if (profile_type.includes("DTOL_ENV")) {
                acronym = "DTOL-ENV"
                colour = "#fb7d0d"
                $(el).find(".panel-heading").find(".row-title span").append('<small>(DTOL-ENV)</small>');
                $(el).find(".panel-heading").css('background-color', colour)
            } else if (profile_type.includes("DTOL")) {
                acronym = "DTOL"
                colour = "#16ab39"
                $(el).find(".panel-heading").find(".row-title span").append('<small>(DTOL)</small>');
                $(el).find(".panel-heading").css("background-color", colour)
            } else if (profile_type.includes("ASG")) {
                acronym = "ASG"
                colour = "#5829bb"
                $(el).find(".panel-heading").find(".row-title span").append('<small>(ASG)</small>');
                $(el).find(".panel-heading").css("background-color", colour)
            } else if (profile_type.includes("ERGA")) {
                acronym = "ERGA"
                colour = "#E61A8D"
                $(el).find(".panel-heading").find(".row-title span").append('<small>(ERGA)</small>');
                $(el).find(".panel-heading").css("background-color", colour)
            } else if (profile_type.includes("Stand-alone")) {
                acronym = "Standalone"
                colour = "#009c95"
                $(el).find(".panel-heading").find(".row-title span").append('<small>(Standalone)</small>');
                $(el).find(".panel-heading").css("background-color", colour)
            } else {
                acronym = "Shared"
                colour = "#f26202"
                $(el).find(".panel-heading").find(".row-title span").append('<small>(Shared With Me)</small>');
                $(el).find(".panel-heading").css("background-color", colour)
            }

            // Add profile type legend data if it is not already in the list/displayed
            legend_data = {'profileType': profile_type, 'profileTypeAcronym': acronym, 'profileTypeColour': colour}

            if (!profiles_legend_lst.map(x => x.profileType).includes(profile_type) && !current_profile_legendData.includes(acronym)) {
                profiles_legend_lst.push(legend_data)
            }
        });
    });

    display_profiles_legend(profiles_legend_lst)
    set_copo_sidebar_info_padding()
}

function set_associated_types_marginBottom() {
    // Set the margin bottom once a profile description is displayed on two lines
    // NB: If line height is 21 or 24, then, profile description is displayed on one line
    // NB: If line height is 42 or 48 then, profile description is displayed on two lines

    $("div.profileDescription").each(function () {
        if ($(this).height() === 42 || $(this).height() === 48) {
            // No associated types
            if ($(this).hasClass('no_associatedTypes_marginBottom')) {
                $(this).removeClass('no_associatedTypes_marginBottom')
                    .addClass('no_associatedTypes_marginBottom_2LineDescriptionText')
            } else {
                // Associated types
                let associated_type_div_value = $(this).next().next();
                if ($(this).hasClass('associatedTypes_marginBottom')) {
                    if (associated_type_div_value.hasClass('one_associatedType_marginBottom')) {
                        associated_type_div_value
                            .removeClass('one_associatedType_marginBottom')
                            .addClass('one_associatedType_marginBottom_2LineDescriptionText')
                    } else if (associated_type_div_value.hasClass('two_associatedTypes_marginBottom')) {
                        associated_type_div_value
                            .removeClass('two_associatedTypes_marginBottom')
                            .addClass('two_associatedTypes_marginBottom_2LineDescriptionText')
                    } else if (associated_type_div_value.hasClass('three_associatedTypes_marginBottom')) {
                        associated_type_div_value
                            .removeClass('three_associatedTypes_marginBottom')
                            .addClass('three_associatedTypes_marginBottom_2LineDescriptionText')
                    } else if (associated_type_div_value.hasClass('several_associatedType_marginBottom')) {
                        associated_type_div_value
                            .removeClass('several_associatedType_marginBottom')
                            .addClass('several_associatedTypes_marginBottom_2LineDescriptionText')
                    }
                }
            }
        }
    });
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
            } /* else if (action_type === "reads") {
                url = copoENAReadManifestValidateURL + id
            } else if (action_type === "assembly") {
                url = copoENAAssemblyURL + id
            } else if (action_type === "seq_annotation") {
                url = copoENAAnnotationURL + id
            } */ else {
                url = "/copo/copo_" + action_type + "/" + id + "/view"
            }
            document.location = url
        }
    })

    $(".expanding_menu > div").click(function (e) {
        const el = $(e.currentTarget);
        el.closest('.grid').removeClass("grid-selected")
        el.closest('.panel-heading').next('.grid-panel-body').removeClass("grid-panel-body-selected")
    })

    $('#editProfileBtn').click(function (e) {
        let profile_id = $(e.currentTarget).closest(".ellipsisDiv").attr("id");
        editProfileRecord(profile_id);
    });

    $('#deleteProfileBtn').click(function (e) {
        let profile_id = $(e.currentTarget).closest(".ellipsisDiv").attr("id");
        deleteProfileRecord(profile_id);
    });

    $('#popoverCloseBtn').click(function () {
        $('#ellipsisID[data-toggle="popover"]').popover('hide')
    });

    // Initialise the popover 'View profile options' for each profile record
    let popover = $('#ellipsisID[data-toggle="popover"]').popover({
        sanitize: false
    }).click(function (e) {
        $(this).popover('toggle');
        $('#ellipsisID').not(this).popover('hide');
        e.stopPropagation();
    }).on('show.bs.popover', function (e) {
        // Set content of the popover
        const $content = $('<div></div>');
        const $editButton = $('<button id="editProfileBtn" class="btn btn-sm btn-success" title="Edit record"><i class="fa fa-pencil-square-o"></i>&nbsp;Edit</button>');
        const $deleteButton = $('<button id="deleteProfileBtn" class="btn btn-sm btn-danger" title="Delete record"><i class="fa fa-trash-o"></i>&nbsp;Delete</button>');

        $deleteButton.css('margin-left', '15px');
        $content.append($editButton);
        $content.append($deleteButton);

        // Apply the content to the popover
        popover.attr('data-content', $content.html());

    }).on('shown.bs.popover', function (e) {
        $('.row-ellipsis').attr('title', '') // Hide 'View profile options' title from appearing in the popover on hover
    });
}