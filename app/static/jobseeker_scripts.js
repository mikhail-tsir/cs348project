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

// Event listener for file upload (display filename and submit form)
document.addEventListener('DOMContentLoaded', () => {
    let fileInputs = document.querySelectorAll('.file.has-name');
    for (let fileInput of fileInputs) {
        let input = fileInput.querySelector('.file-input');
        input.addEventListener('change', () => {
            // Submit the form to upload resume right away
            document.getElementById('upload-resume').submit();
        });
    }
});


// function applyJob(jobId) {
//     $.ajax({
//         url: `/jobseeker/apply/${jobId}`,
//         method: "POST",
//         success: function () {
//             console.log("SUCCESS");
//             document.getElementById("apply-btn").value = "Withdraw Application";
//         }
//     });
// }