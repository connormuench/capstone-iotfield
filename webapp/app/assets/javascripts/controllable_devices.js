$(document).ready(function() {
    $(".expression-button").on("shown.bs.dropdown", function() {
        $(this).find("input.form-control").focus();
    });
})
