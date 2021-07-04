from flask import Blueprint, render_template, request

from app.util.auth_util import generic_login, generic_signup

company_auth = Blueprint("company_auth", __name__)


@company_auth.route("/login")
def login():
    return render_template("login.html", user_type_nice="Company")


@company_auth.route("/login", methods=["POST"])
def login_post():
    return generic_login("company")


@company_auth.route("/signup")
def signup():
    return render_template("company-signup.html")


@company_auth.route("/signup", methods=["POST"])
def signup_post():
    return generic_signup("company")
