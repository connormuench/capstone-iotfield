$(document).ready(function() {
    facId = $("#rule-rows").data("facility-id");
    $(".expression-button").on("shown.bs.dropdown", function() {
        $(this).find("input.form-control").focus();
    });

    $(".device-mode").on("click", function(e) {
        let jButton = $(this).find("input:radio");
        if (!confirm("Are you sure you want to switch to " + jButton.attr("value") + " mode?")) {
            jButton.prop("checked", false);
            jButton.closest("label").removeClass("active");
            jButton.closest("label").siblings("label").find("input:radio").prop("checked", true);
            console.log(jButton.closest("label"));
            jButton.closest("label").siblings("label").addClass("active");
            e.stopPropagation();
            e.preventDefault();
            return;
        }
        $.post(jButton.closest("div.btn-group").data("target-url"), {mode: jButton.attr("value")});
        $("#commandSection").slideToggle(200);
    });
});

function setDevice(button) {
    if (!confirm("Are you sure you wish to control this device?"))
        return;
    let textbox = $("#commandField");
    let jButton = $(button);
    console.log(jButton.data("target-url"));
    $.post(jButton.data("target-url"), {command: textbox.val()});
}
