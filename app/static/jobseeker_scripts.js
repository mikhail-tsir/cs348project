function deleteSkill(skillId) {
    $.ajax({
        url: `/jobseeker/delete_skill/${skillId}`,
        method: "DELETE",
        success: function() {
            console.log("SUCCESS");
            window.location = "/jobseeker/skills";
        },
        error: function() {
            console.log("ERROR");
            window.location.reload();
        }
    });
}
