from flask.json import jsonify
from flask import render_template, redirect, url_for, request, flash, Blueprint
from flask_login import login_required, current_user
from . import db

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/homepage")
@login_required
def homepage():
    return render_template(
        "jobseeker-homepage.html", fname=current_user.fname, lname=current_user.lname
    )
