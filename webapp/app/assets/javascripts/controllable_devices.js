$(document).ready(function() {
    facId = $("#rule-rows").data("facility-id");
    $(".expression-button").on("shown.bs.dropdown", function() {
        $(this).find("input.form-control").focus();
    });
});

function setDevice() {
    let textbox = $("#commandField");
    $.get()
}
