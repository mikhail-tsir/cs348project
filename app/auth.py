from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user, login_required, logout_user
from pymysql.err import MySQLError
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from app.models import JobSeeker, Company, Account
from app.util.auth_util import generic_login

jobseeker = Blueprint("jobseeker", __name__)


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
    fname, lname, email, pw, confirm_pw, phone = (
        request.form.get("fname"),
        request.form.get("lname"),
        request.form.get("email"),
        request.form.get("password"),
        request.form.get("confirm_password"),
        request.form.get("phone"),
    )

    with db.connect() as conn:
        conn.autocommit = False
        cursor = conn.cursor()
        # check if user already exists
        cursor.execute("SELECT * FROM account WHERE email = %s", email)
        result = cursor.fetchall()

        if result:
            flash("User already exists")
            return redirect(url_for("jobseeker.signup"))

        # check if passwords match
        if pw != confirm_pw:
            flash("Passwords don't match")
            return redirect(url_for("jobseeker.signup"))

        hashed_pw = generate_password_hash(pw)

        try:
            # insert account info first
            cursor.execute(
                """
                INSERT INTO account (email, password)
                VALUES (%s, %s);
                """,
                (email, hashed_pw),
            )

            # get id of newly inserted user
            cursor.execute(
                """
                SELECT id FROM account
                WHERE email = %s;
                """,
                email,
            )

            result = cursor.fetchone()
            account_id = result[0] if result else -1

            cursor.execute(
                """
                INSERT INTO job_seeker (fname, lname, phone, id)
                VALUES (%s, %s, %s, %s);
                """,
                (fname, lname, phone, account_id),
            )

            conn.commit()
        except MySQLError as e:
            print(e)
            conn.rollback()
            flash("Oops! There was an issue with sign up. Please try again")
            raise e
            return redirect(url_for("jobseeker.signup"))

    return redirect(url_for("jobseeker.login"))


# TODO logout should be a POST request
@jobseeker.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("base.index"))
