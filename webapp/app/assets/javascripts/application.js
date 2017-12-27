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
//= require turbolinks
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
                console.log(data);
                dropdownMenu.children().remove();
                Object.keys(data).forEach(function(key) {
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
                });
            });
    } else {
        dropdownMenu.children().remove();
    }
}

$(document).on("turbolinks:load", function() {
    $("#searchBox").on("click", function(event) {
        event.preventDefault();
        event.stopPropagation();
    });

    $("#searchBox").focus(function(event) {
        $("#searchDropdown").addClass("show").find(".dropdown-menu").addClass("show");
    });

    $("#searchBox").focusout(function(event) {
        console.log("done");
        $("#searchDropdown").removeClass("show").find(".dropdown-menu").removeClass("show");

    });
})
