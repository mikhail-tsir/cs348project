from flask import render_template, Blueprint, redirect, url_for
from flask_login import login_required, logout_user

base = Blueprint("base", __name__)


@base.route("/")
def index():
    return render_template("index.html")


# TODO logout should be a POST request
@base.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("base.index"))