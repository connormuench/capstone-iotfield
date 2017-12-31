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
// require turbolinks
//= require_tree .

//= require popper
//= require bootstrap-sprockets

function autocompleteSearch(textbox) {
    var jTextbox = $(textbox);
    var query = jTextbox.val();
    var dropdownMenu = jTextbox.siblings(".dropdown-menu");
    if (query != "") {
        $.get(jTextbox.closest("form").attr("action") + ".json", 
            {q: query}, 
            function(data) {
                dropdownMenu.children().remove();
                Object.keys(data).forEach(function(key) {
                    if (data[key].length > 0) {
                        dropdownMenu.append($("<h6>")
                            .attr("class", "dropdown-header")
                            .text(key.replace("_", " ").replace(/(?:^|\s)\w/g, function(match) {
                                return match.toUpperCase();
                            })));
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
                if (dropdownMenu.children().length > 0) {
                    showSearchDropdown();
                } else {
                    hideSearchDropdown();
                }
            });
    } else {
        dropdownMenu.children().remove();
        hideSearchDropdown();
    }
}

$(document).ready(function() {
    $("#searchBox").on("click", function(event) {
        event.stopPropagation();
    });

    $("#searchBox").on("focus", function(e) {
        showSearchDropdown();
    });

    $("#searchBox").on("blur", function(e) {
        if (!$("#searchDropdown").has(e.relatedTarget)) {
            hideSearchDropdown(e);
        }
    });

    $('[data-toggle="tooltip"]').tooltip();
})

function showSearchDropdown() {
    var dropdown = $("#searchDropdown");
    if ($("#searchBox").val() != "" && !dropdown.hasClass("show")) {
        dropdown.addClass("show").find(".dropdown-menu").addClass("show");
    }
}

function hideSearchDropdown() {
    var dropdown = $("#searchDropdown");
    if (dropdown.hasClass("show")) {
        dropdown.removeClass("show").find(".dropdown-menu").removeClass("show");
    }
}
