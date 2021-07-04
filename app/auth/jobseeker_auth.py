from flask import Blueprint, render_template, redirect, request, url_for

from app.util.auth_util import generic_login, generic_signup

jobseeker_auth = Blueprint("jobseeker_auth", __name__)


@jobseeker_auth.route("/login")
def login():
    return render_template("login.html", user_type_nice="Job Seeker")


@jobseeker_auth.route("/signup")
def signup():
    return render_template("jobseeker-signup.html")


@jobseeker_auth.route("/login", methods=["POST"])
def login_post():
    return generic_login("jobseeker")


@jobseeker_auth.route("/signup", methods=["POST"])
def signup_post():
    return generic_signup("jobseeker", request.form)
