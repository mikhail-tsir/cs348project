function deleteSkill(skillId, jobId) {
    $.ajax({
        url: `/company/delete_skill?job_id=${jobId}&skill_id=${skillId}`,
        method: "DELETE",
        success: function () {
            console.log("SUCCESS");
            window.location = `/company/view_job/${jobId}`;
        },
        error: function () {
            console.log("ERROR");
            window.location.reload();
        }
    });
}

function changeProficiency(skillId, proficiency, jobId) {
    $.ajax({
        url: `/company/change_proficiency/${jobId}?skill_id=${skillId}&proficiency=${proficiency}`,
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
