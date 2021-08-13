function addSkill(jobId, skillId) {
    console.log("adding skill");
    $.ajax({
        url: `/company/add_skill/${jobId}?skill_id=${skillId}`,
        method: "POST",
        succuess: function() {
            console.log("SUCCESS");
            window.location = `/company/job/${jobId}`;
        },
        error: function() {
            console.log("ERROR");
            // window.location.reload();
        }
    });
}

function deleteSkill(skillId, jobId) {
    $.ajax({
        url: `/company/delete_skill/${jobId}?skill_id=${skillId}`,
        method: "DELETE",
        success: function () {
            console.log("SUCCESS");
            window.location = `/company/job/${jobId}`;
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

function deletePosting(jobId) {
    $.ajax({
        url: `/company/delete_posting/${jobId}`,
        methos: "DELETE",
        success: function () {
            console.log("SUCCESS");
        },
        error: function () {
            alert("Oops, unable to delete posting :(");
        }
    });
}


function generateSelectOptions(proficiency) {
    return `
        <option ${proficiency == 1 ? "selected" : ""} value=1>Basic</option>
        <option ${prpficiency == 2 ? "selected" : ""} value=2>Working</option>
        <option ${proficiency == 3 ? "selected" : ""} value=3>Advanced</option>
    `;
}


function skillRow(skillId, skillName, proficiency) {
    return `
        <tr>
            <td><span class="tag is-info is-large">${skillName}</span></td>
            <td>
                <div class="select" name="${skillId}">
                    <select name="${skillId}" onChange="changeProficiencyTemp(${skillId}, this.value);">
                        ${generateSelectOptions(proficiency)}
                    </select>
                </div>
            </td>
            <td>
                <button class="delete is-medium" onClick="deleteSkillTemp(${skillId});"></button>
            </td>
        </tr>
    `;
}


// let allSkills = {};
// let skillsDict = {};


// function getAllSkills() {
//     if (allSkills.length == 0) {
//         $.ajax({
//             url: "/base/all_skills",
//             method: "GET",
//             success: function(data) {
//                 for (var tuple in data) {
//                     allSkills[tuple[0]] = tuple[1];
//                 }
//             },
//             error: function () {
//                 alert("Error fetching skills");
//             }
//         });
//     }
// }


// window.addEventListener('DOMContentLoaded', function () {
//     getAllSkills();
//     skillsDict = {};

//     let dropdown = document.getElementById('add-skill')
//     if (dropdown) {
//         allSkills.map(
//             tuple => dropdown.innerHTML += `<option id="skill-option" value=${tuple[0]}>${tuple[1]}</option>\n`
//         );
//     }
// });

// function renderSkills() {
//     table = document.getElementById("skills-table-body");
//     table.innerHTML = '';

//     for (var skillId in skillsDict) {
//         document.getElementById("skills-table-body").innerHTML += skillRow(skillId, skillsDict[skillId][0], skillsDict[skillId][1])
//     }
// }


// function addSkillTemp(skillId) {
//     skillsDict[skillId] = allSkills[skillId.toString()];
// }