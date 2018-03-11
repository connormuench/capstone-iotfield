// Global variable to store the current facility ID
var facId;

// Fires when the page loads
$(document).ready(function() {
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

        // Retrieve the points that are addable for the current facility
        $.get("/facilities/" + facId + "/addable",
            function(data) {
                // Clear the select options before adding the current options
                var sensorSelect = $("#availableSensors");
                var controllableDeviceSelect = $("#availableControllableDevices");
                sensorSelect.children().remove();
                controllableDeviceSelect.children().remove();

                // Add the returned sensors to the sensor select
                if ("sensor" in data) {
                    Object.keys(data.sensor).forEach(function(key) {
                        var text = key.toString();
                        if (data.sensor[key] !== "") {
                            text += " | " + data.sensor[key];
                        }
                        sensorSelect.append($("<option>", {
                            value: key,
                            text: text
                        }));
                    });
                }

                // Add the returned controllable devices to the controllable device select
                if ("controllable_device" in data) {
                    Object.keys(data.controllable_device).forEach(function(key) {
                        var text = key.toString();
                        if (data.controllable_device[key] !== "") {
                            text += " | " + data.controllable_device[key];
                        }
                        controllableDeviceSelect.append($("<option>", {
                            value: key,
                            text: text
                        }));
                    });
                }
            });
    });

    // Event fired when #addFacilityModal is shown
    $("#addFacilityModal").on("show.bs.modal", function (event) {
        // Retrieve the available facilities from the web server
        $.get("/facilities/addable",
            function(data) {
                // Clear the select options before adding the current options
                var select = $("#availablePis");
                select.children().remove();
                // Add the returned facilities to the facility select
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
        .attr("class", "delete-on-discard")
        .append($("<td>")
            .attr("class", "text-center align-middle")
            .append($("<div>")
                .attr("class", "is-active-checkbox")
                .append($("<input>")    // Hidden input field to placehold the unchecked state of the checkbox
                    .attr("type", "hidden")
                    .attr("name", "rules_attributes[][is_active]")
                    .attr("value", "0"))
                .append($("<input>")    // is_active checkbox
                    .attr("class", "my-auto mx-auto")
                    .attr("type", "checkbox")
                    .attr("name", "rules_attributes[][is_active]"))))
        .append($("<td>")
            .append($("<div>")      // Expression input group
                .attr("class", "input-group")
                .append($("<input>")    // Expression text box
                    .attr("class", "form-control")
                    .attr("type", "text")
                    .attr("name", "rules_attributes[][expression]"))
                .append($("<div>")      // Sensor autocomplete button
                    .attr("class", "input-group-btn expression-button")
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
                .attr("onclick", "return sensorClicked(this)")
                .html(value.replace(new RegExp(textFieldVal, "i"), function(match) {
                    return "<b>" + match + "</b>";      // Bold the query
                })));
        }
    });
}

// Function to add the selected sensor's ID to the expression
function sensorClicked(element) {
    let expressionTextbox = $($(element.closest(".input-group-btn")).siblings("input.form-control"));
    textboxVal = expressionTextbox.val();
    textboxVal = typeof(textboxVal) === "undefined" ? "" : textboxVal;
    expressionTextbox.val(textboxVal + $(element).text());
    expressionTextbox.focus();
    return false;
}

// Function to toggle the disabled state of the specified JQuery element
function toggleDisabled(element) {
    if (element.is("[disabled]")) {
        element.removeAttr("disabled");
    } else {
        element.attr("disabled", "true");
    }
}

// Function to disable the specified JQuery element
function disableElement(element) {
    if (!element.is("[disabled]")) {
        element.attr("disabled", "true");
    }
}

// Function to enable the specified JQuery element
function enableElement(element) {
    if (element.is("[disabled]")) {
        element.removeAttr("disabled");
    }
}
