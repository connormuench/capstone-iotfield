$(document).ready(function() {
    $('#userPermissionsModal').on('show.bs.modal', function(event) {
        var button = $(event.relatedTarget);
        var facilities = button.data('facility-access-levels'); 
        var modal = $(this);
        console.log(modal.find(".btn-group"));
        modal.find(".btn-group").each(function(i, element) {
            console.log($(element).find(".level-none"));
            let radioButton = $(element).find(".level-none");
            radioButton.prop("checked", true);
            radioButton.closest("label").addClass("active");
            $(element).find(".level-monitor").closest("label").removeClass("active");
            $(element).find(".level-controller").closest("label").removeClass("active");
        });
        Object.keys(facilities).forEach(function(facility) {
            let facilityGroup = modal.find("#facility" + facility);
            facilityGroup.find("label").removeClass("active");
            let rbutton = facilityGroup.find(".level-" + facilities[facility].toLowerCase())
            rbutton.prop("checked", true);
            rbutton.closest("label").addClass("active");

        });
    });
});




function permissionSearch(textbox) {
    let jTextbox = $(textbox);
    jTextbox.siblings(".admin-panel-column").find(".user-name").each(function(i, element) {
        let jElement = $(element);
        if (jElement.text().indexOf(jTextbox.val().trim()) != -1) {
            jElement.closest(".card").show();
        } else {
            jElement.closest(".card").hide();
        }
    });
}