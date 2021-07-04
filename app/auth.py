from app.decorators import jobseeker_login_required
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required, logout_user

from app.blueprints import jobseeker, company
from app.models import JobSeeker, Company, Account
from app.util.auth_util import generic_login, generic_signup


@jobseeker.route("/login")
def login():
    return render_template("jobseeker-login.html")


@jobseeker.route("/signup")
def signup():
    return render_template("jobseeker-signup.html")


@jobseeker.route("/login", methods=["POST"])
def login_post():
    return generic_login("jobseeker")


@jobseeker.route("/signup", methods=["POST"])
def signup_post():
    return generic_signup("jobseeker", request.form)


@jobseeker.route("/homepage")
@jobseeker_login_required
def homepage():
    return render_template(
        "jobseeker-homepage.html", fname=current_user.user.fname, lname=current_user.user.lname
    )


# TODO logout should be a POST request
@jobseeker.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("base.index"))
