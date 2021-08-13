from flask import render_template, Blueprint, redirect, url_for, current_app
from flask.json import jsonify
from flask_login import login_required, logout_user

base = Blueprint("base", __name__)

from app import db


@base.route("/")
def index():
    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT email FROM company_account LIMIT 5;")
        result = str(cursor.fetchall())
        current_app.logger.info(result)
        
    return render_template("index.html")



@base.route("/all_skills")
def all_skills():
    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT * FROM skill;")
        result = cursor.fetchall()
        return jsonify(result)


@base.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("base.index"))
