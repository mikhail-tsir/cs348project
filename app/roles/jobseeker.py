from flask import Blueprint, render_template
from flask_login import current_user

from app.decorators import jobseeker_login_required

jobseeker = Blueprint("jobseeker", __name__)


@jobseeker.route("/homepage")
@jobseeker_login_required
def homepage():
    jobs_dict = {
        "title": "Backend Software Engineer",
        "company": "TechnoCorp",
        "location": "Ottawa, ON",
        "description": "We are looking for a talented Backend engineer to work on our public API.\nCome join us!",
        "min_skill_proficiencies": {"Relational Databases": 3, "C++": 1},
    }
    return render_template(
        "jobseeker-homepage.html",
        fname=current_user.user.fname,
        lname=current_user.user.lname,
        job_previews=[jobs_dict],
    )
