// Global variable to store the current facility ID
var facId;

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

    // Change the action of #addPointForm and toggle the controllable device section of the modal
    // when the Sensor/Controllable Device toggle is triggered
    $("input:radio[name=pointTypes]").on("change", function() {
        $("#addPointForm").attr("action", $(this).data("url"));
        $("#controllableDeviceSection").slideToggle();
        $("#availableSensorsSection").toggle();
        $("#availableControllableDevicesSection").toggle();
        toggleDisabled($("#availableSensors"));
        toggleDisabled($("#availableControllableDevices"));
    });

    // Event fired when #addPointModal is shown
    $("#addPointModal").on("show.bs.modal", function (event) {
        var button = $(event.relatedTarget); // Button that triggered the modal
        if (facId != button.data("facility-id")) {
            facId = button.data("facility-id");
            var modal = $(this);

            // Set the "data-url" attribute of the Sensor/Controllable Device toggles and the action
            // of the form to correspond  to the selected facility
            $("#sensorOption").attr("data-url", "/facilities/" + facId + "/sensors/");
            $("#controllableDeviceOption").attr("data-url", "/facilities/" + facId + "/controllable_devices/");
            $("#addPointForm").attr("action", "/facilities/" + facId + "/sensors/").trigger("reset");

            // Reset the automation rule rows
            $("#rule-rows").children().remove();
        }
        $.get("/facilities/" + facId + "/addable",
            function(data) {
                console.log(data);
                var sensorSelect = $("#availableSensors");
                var controllableDeviceSelect = $("#availableControllableDevices");
                sensorSelect.children().remove();
                controllableDeviceSelect.children().remove();
                if ("sensor" in data) {
                    data.sensor.forEach(function(element) {
                        var text = element.id.toString();
                        if ("name" in element) {
                            text += " | " + element.name
                        }
                        sensorSelect.append($("<option>", {
                            value: element.id,
                            text: text
                        }));
                    });
                }
                if ("controllable_device" in data) {
                    data.controllable_device.forEach(function(element) {
                        var text = element.id.toString();
                        if ("name" in element) {
                            text += " | " + element.name
                        }
                        controllableDeviceSelect.append($("<option>", {
                            value: element.id,
                            text: text
                        }));
                    });
                }
            });
    });

    $("#addFacilityModal").on("show.bs.modal", function (event) {
        $.get("/facilities/addable",
            function(data) {
                var select = $("#availablePis");
                select.children().remove();
                if ("facilities" in data) {
                    data.facilities.forEach(function(element) {
                        var text = element.id.toString();
                        if ("name" in element) {
                            text += " | " + element.name;
                        }
                        select.append($("<option>", {
                            value: element.id,
                            text: text
                        }));
                    });
                }
            });
    });

    // Initialize popovers
    $("[data-toggle='popover']").popover();
});

// Adds a row to the automation rules section of #addPointModal
function addRuleRow() {
    var row = $("#rule-rows").append($("<tr>")
        .append($("<td>")
            .attr("class", "text-center align-middle")
            .append($("<div>")
                .attr("class", "form-check my-auto")
                .append($("<label>")
                    .attr("class", "custom-control custom-checkbox my-auto mx-auto is-active-checkbox")
                    .append($("<input>")    // Hidden input field to placehold the unchecked state of the checkbox
                        .attr("type", "hidden")
                        .attr("name", "rules_attributes[][is_active]")
                        .attr("value", "0"))
                    .append($("<input>")    // is_active checkbox
                        .attr("class", "custom-control-input")
                        .attr("type", "checkbox")
                        .attr("name", "rules_attributes[][is_active]"))
                    .append($("<span>").attr("class", "custom-control-indicator")))))
        .append($("<td>")
            .append($("<div>")      // Expression input group
                .attr("class", "input-group")
                .append($("<input>")    // Expression text box
                    .attr("class", "form-control")
                    .attr("type", "text")
                    .attr("name", "rules_attributes[][expression]"))
                .append($("<div>")      // Sensor autocomplete button
                    .attr("class", "input-group-btn")
                    .on("shown.bs.dropdown", function() {
                        $(this).find("input.form-control").focus();
                    })
                    .append($("<button>")
                        .attr("type", "button")
                        .attr("class", "btn btn-secondary dropdown-toggle")
                        .attr("data-toggle", "dropdown")
                        .append($("<span>")
                            .attr("class", "ion-radio-waves")))
                    .append($("<div>")      // Autocomplete dropdown
                        .attr("class", "dropdown-menu dropdown-menu-right pointDropdown")
                        .append($("<span>")
                            .attr("class", "dropdown-item")
                            .append($("<input>")    // Autocomplete text box
                                .attr("type", "text")
                                .attr("class", "form-control mx-auto")
                                .attr("onkeyup", "updateList(this)")
                                .attr("style", "width: 100%;")))))))
        .append($("<td>")
            .append($("<input>")    // Action text box
                .attr("class", "form-control")
                .attr("type", "text")
                .attr("name", "rules_attributes[][action]")))
        .append($("<td>")
            .attr("class", "text-center align-middle")
            .append($("<button>")   // Delete rule button
                .attr("class", "btn btn-sm btn-danger")
                .attr("onclick", "deleteRuleRow(this)")
                .attr("type", "button")
                .append($("<span>")
                    .attr("class", "ion-trash-b")))));

    // Populate the dropdown
    var dropdown = $("#rule-rows").children("tr").last().find(".pointDropdown");
    $("#rules-table").data("points")[facId].forEach(function (value) {
        dropdown.append($("<a>")
            .attr("class", "dropdown-item")
            .attr("href", "#")
            .attr("onclick", "return sensorClicked(this)")
            .text(value));
    });
}

// Function to execute immediately before form submission
function submitted() {
    // Disable any hidden field if its corresponding checkbox is checked
    $(".is-active-checkbox").each(function() {
        if ($(this).find("input:checkbox")[0].checked) {
            $(this).find("input:hidden").attr("disabled", true);
        }
    });
    return true;
}

// Function to delete an associated rule row
// deleteButton: the button that was clicked
function deleteRuleRow(deleteButton) {
    deleteButton.closest("tr").remove();
}

// Function to update the dropdown list of sensors for building an expression
// textField: the active text field
function updateList(textField) {
    // Remove all existing items in the dropdown
    $(textField.closest(".dropdown-item")).siblings().each(function() {
        $(this).remove();
    });

    // Filter points in the facility based on the query
    $("#rules-table").data("points")[facId].forEach(function (value) {
        var lowerVal = value.toLowerCase();
        var textFieldVal = $(textField).val();
        var indexOfQuery = lowerVal.indexOf(textFieldVal);
        // Add the point to the dropdown and mark up its name if it matches the query
        if (textFieldVal == "" || indexOfQuery != -1) {
            var dropdown = $(textField.closest("tr")).find(".pointDropdown");
            dropdown.append($("<a>")
                .attr("class", "dropdown-item")
                .attr("href", "#")
                .attr("onclick", "return facilityClicked(this)")
                .html(value.replace(new RegExp(textFieldVal, "i"), function(match) {
                    return "<b>" + match + "</b>";      // Bold the query
                })));
        }
    });
}

// Function to add the selected sensor's ID to the expression
function sensorClicked(element) {
    textboxVal = $(element.closest("input.form-control")).val();
    textboxVal = typeof(textboxVal) === "undefined" ? "" : textboxVal;
    expressionTextbox = $($(element.closest(".input-group-btn")).siblings("input.form-control"))
    expressionTextbox.val(textboxVal + $(element).text());
    expressionTextbox.focus();
    return false;
}

// Function to toggle the facility's attributes to become editable form fields
function editFacility() {
    $(".form-toggle").toggle();
}

// Function to reset the facility's form and toggle the form fields to read-only attributes
function discardChanges() {
    $('#editFacilityForm').trigger("reset");
    $(".form-toggle").toggle();   
}

function toggleDisabled(element) {
    if (element.is("[disabled]")) {
        element.removeAttr("disabled");
    } else {
        element.attr("disabled", "true");
    }
}

function disableElement(element) {
    if (!element.is("[disabled]")) {
        element.attr("disabled", "true");
    }
}

function enableElement(element) {
    if (element.is("[disabled]")) {
        element.removeAttr("disabled");
    }
}
