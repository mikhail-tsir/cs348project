from flask import Blueprint, render_template
from flask_login import current_user

from app.decorators import jobseeker_login_required

jobseeker = Blueprint("jobseeker", __name__)

@jobseeker.route("/homepage")
@jobseeker_login_required
def homepage():
    return render_template(
        "jobseeker-homepage.html",
        fname=current_user.user.fname,
        lname=current_user.user.lname,
    )
