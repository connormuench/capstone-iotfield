// This is a manifest file that'll be compiled into application.js, which will include all the files
// listed below.
//
// Any JavaScript/Coffee file within this directory, lib/assets/javascripts, or any plugin's
// vendor/assets/javascripts directory can be referenced here using a relative path.
//
// It's not advisable to add code directly here, but if you do, it'll appear at the bottom of the
// compiled file. JavaScript code in this file should be added after the last require_* statement.
//
// Read Sprockets README (https://github.com/rails/sprockets#sprockets-directives) for details
// about supported directives.
//
//= require jquery3
//= require rails-ujs

//= require popper
//= require bootstrap-sprockets
//= require moment
//= require tempusdominus-bootstrap-4.js

//= require gijgo/core.min
//= require gijgo/checkbox.min
//= require gijgo/tree.min

//= require Chart.bundle
//= require chartkick
//= require_tree .

// Function to populate the sitewide search box dropdown
function autocompleteSearch(textbox) {
    var jTextbox = $(textbox);
    var query = jTextbox.val();
    var dropdownMenu = jTextbox.siblings(".dropdown-menu");

    if (query != "") {
        // Send a GET request to the server to get the items matching the current query
        $.get(jTextbox.closest("form").attr("action") + ".json", 
            {q: query}, 
            function(data) {    // Callback to execute when the response is received
                dropdownMenu.children().remove();
                // Iterate through the provided categories
                Object.keys(data).forEach(function(key) {
                    if (data[key].length > 0) {
                        // Add a header for the category
                        dropdownMenu.append($("<h6>")
                            .attr("class", "dropdown-header")
                            .text(key.replace("_", " ").replace(/(?:^|\s)\w/g, function(match) {
                                return match.toUpperCase();
                            })));
                        // Add a dropdown item for each item in the category
                        data[key].forEach(function(item) {
                            value = item.name;
                            indexOfQuery = value.indexOf(query);
                            dropdownMenu.append($("<a>")
                                .attr("class", "dropdown-item")
                                .attr("href", item.url)
                                .html(value.replace(new RegExp(query, "i"), function(match) {
                                    return "<b>" + match + "</b>";
                                })));
                        });
                    }
                });
                // Show the dropdown if there are any results, make sure it's hidden otherwise
                if (dropdownMenu.children().length > 0) {
                    showSearchDropdown();
                } else {
                    hideSearchDropdown();
                }
            });
    } else {
        // Remove all dropdown items and hide the dropdown if the query is empty
        dropdownMenu.children().remove();
        hideSearchDropdown();
    }
}

// Fires when the page loads
$(document).ready(function() {
    // Set a min button width for .manip-button
    var maxwidth = 10;

    // See if there's any buttons larger and set all buttons to the same width
    $(".manip-button").each(function() {
        if ($(this).width() > maxwidth) {
            maxwidth = $(this).width();
        }
    });
    $(".manip-button").width(maxwidth);

    // Fires when the search box is clicked
    $("#searchBox").on("click", function(event) {
        // Prevent the default dropdown functionality when the text box is clicked, since it's buggy with text boxes
        event.stopPropagation();
    });

    // Fires when the text box gets focus
    $("#searchBox").on("focus", function(e) {
        showSearchDropdown();
    });

    // Fires when the text box loses focus
    $("#searchBox").on("blur", function(e) {
        // Check that the user didn't click on one of the dropdown items, since blur() fires before click()
        if ($("#searchDropdown").has(e.relatedTarget).length == 0) {
            hideSearchDropdown();
        }
    });

    // Initialize tooltips
    $('[data-toggle="tooltip"]').tooltip();
})

// Function to show the search dropdown
function showSearchDropdown() {
    var dropdown = $("#searchDropdown");
    if ($("#searchBox").val() != "" && !dropdown.hasClass("show")) {
        dropdown.addClass("show").find(".dropdown-menu").addClass("show");
    }
}

// Function to hide the search dropdown
function hideSearchDropdown() {
    var dropdown = $("#searchDropdown");
    if (dropdown.hasClass("show")) {
        dropdown.removeClass("show").find(".dropdown-menu").removeClass("show");
    }
}


// Function to reset the form and toggle the form fields to read-only attributes
function discardChanges(form) {
    form.trigger("reset");
    $(".form-toggle").toggle();
    $(".delete-on-discard").remove();
}

// Function to toggle the attributes to become editable form fields
function editAttributes() {
    $(".form-toggle").toggle();
}
