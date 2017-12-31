var facId;

function ready() {
    // Set a min width
    var maxwidth = 10;

    // See if there's anything larger and set all buttons to the same width
    $(".manip-button").each(function() {
        if ($(this).width() > maxwidth) {
            maxwidth = $(this).width();
        }
    });
    $(".manip-button").width(maxwidth);

    $("input:radio[name=pointTypes]").on("change", function() {
        $("#addPointForm").attr("action", $(this).data("url"));
        $("#controllableDeviceSection").slideToggle();
    });

    $("#addPointModal").on("show.bs.modal", function (event) {
        var button = $(event.relatedTarget); // Button that triggered the modal
        if (facId != button.data("facility-id")) {
            facId = button.data("facility-id"); // Extract info from data-* attributes
            var modal = $(this);
            $("#sensorOption").attr("data-url", "facilities/" + facId + "/sensors/");
            $("#controllableDeviceOption").attr("data-url", "facilities/" + facId + "/controllable_devices/");
            $("#addPointForm").attr("action", "facilities/" + facId + "/sensors/").trigger("reset");
            $("#rule-rows").children().remove();
        }
    });

    $('[data-toggle="popover"]').popover();
}

$(document).ready(ready);

function addRuleRow() {
    var row = $("#rule-rows").append($("<tr>")
        .append($("<td>")
            .attr("class", "text-center align-middle")
            .append($("<div>")
                .attr("class", "form-check my-auto")
                .append($("<label>")
                    .attr("class", "custom-control custom-checkbox my-auto mx-auto is-active-checkbox")
                    .append($("<input>")
                        .attr("type", "hidden")
                        .attr("name", "rules_attributes[][is_active]")
                        .attr("value", "0"))
                    .append($("<input>")
                        .attr("class", "custom-control-input")
                        .attr("type", "checkbox")
                        .attr("name", "rules_attributes[][is_active]"))
                    .append($("<span>").attr("class", "custom-control-indicator")))))
        .append($("<td>")
            .append($("<div>")
                .attr("class", "input-group")
                .append($("<input>")
                    .attr("class", "form-control")
                    .attr("type", "text")
                    .attr("name", "rules_attributes[][expression]"))
                .append($("<div>")
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
                    .append($("<div>")
                        .attr("class", "dropdown-menu dropdown-menu-right pointDropdown")
                        .append($("<span>")
                            .attr("class", "dropdown-item")
                            .append($("<input>")
                                .attr("type", "text")
                                .attr("class", "form-control mx-auto")
                                .attr("onkeyup", "updateList(this)")
                                .attr("style", "width: 100%;")))))))
        .append($("<td>")
            .append($("<input>")
                .attr("class", "form-control")
                .attr("type", "text")
                .attr("name", "rules_attributes[][action]")))
        .append($("<td>")
            .attr("class", "text-center align-middle")
            .append($("<button>")
                .attr("class", "btn btn-sm btn-danger")
                .attr("onclick", "deleteRuleRow(this)")
                .attr("type", "button")
                .append($("<span>")
                    .attr("class", "ion-trash-b")))));

    var dropdown = $("#rule-rows").children("tr").last().find(".pointDropdown");
    $("#rules-table").data("points")[facId].forEach(function (value) {
        dropdown.append($("<a>")
            .attr("class", "dropdown-item")
            .attr("href", "#")
            .attr("onclick", "return facilityClicked(this)")
            .text(value));
    });
}

function submitted() {
    $(".is-active-checkbox").each(function() {
        if ($(this).find("input:checkbox")[0].checked) {
            $(this).find("input:hidden").attr("disabled", true);
        }
    });
    return true;
}

function deleteRuleRow(deleteButton) {
    deleteButton.closest("tr").remove();
}

function updateList(textField) {
    $(textField.closest(".dropdown-item")).siblings().each(function() {
        $(this).remove();
    });
    $("#rules-table").data("points")[facId].forEach(function (value) {
        var lowerVal = value.toLowerCase();
        var textFieldVal = $(textField).val();
        var indexOfQuery = lowerVal.indexOf(textFieldVal);
        if (textFieldVal == "" || indexOfQuery != -1) {
            var dropdown = $(textField.closest("tr")).find(".pointDropdown");
            dropdown.append($("<a>")
                .attr("class", "dropdown-item")
                .attr("href", "#")
                .attr("onclick", "return facilityClicked(this)")
                .html(value.replace(new RegExp(textFieldVal, "i"), function(match) {
                    return "<b>" + match + "</b>";
                })));
        }
    });
}

function facilityClicked(element) {
    textboxVal = $(element.closest("input.form-control")).val();
    textboxVal = typeof(textboxVal) === "undefined" ? "" : textboxVal;
    expressionTextbox = $($(element.closest(".input-group-btn")).siblings("input.form-control"))
    expressionTextbox.val(textboxVal + $(element).text());
    expressionTextbox.focus();
    return false;
}

function editFacility() {
    $(".form-toggle").toggle();
}

function discardChanges() {
    $('#editFacilityForm').trigger("reset");
    $(".form-toggle").toggle();   
}
