function deleteSkill(skillId) {
    $.ajax({
        url: `/jobseeker/delete_skill/${skillId}`,
        method: "DELETE",
        success: function () {
            console.log("SUCCESS");
            window.location = "/jobseeker/skills";
        },
        error: function () {
            console.log("ERROR");
            window.location.reload();
        }
    });
}

function changeProficiency(skillId, proficiency) {
    $.ajax({
        url: `/jobseeker/change_proficiency/${skillId}?proficiency=${proficiency}`,
        method: "PUT",
        success: function () {
            console.log("SUCCESS");
        },
        error: function () {
            alert("Oops, unable to modify skill.");
            console.log("ERROR");
        }
    });
}
