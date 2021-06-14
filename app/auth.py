from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user, login_required, logout_user
from pymysql.err import MySQLError
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from app.models.job_seeker import JobSeeker

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    return render_template("jobseeker-login.html")


@auth.route("/signup")
def signup():
    return render_template("jobseeker-signup.html")


@auth.route("/login", methods=["POST"])
def login_post():
    email, password = request.form.get("email"), request.form.get("password")

    with db.connect() as conn:
        try:
            cursor = conn.cursor()
            # check if user exists
            cursor.execute("SELECT * FROM job_seeker_account WHERE email = %s;", email)
            result = cursor.fetchone()

            if not result:
                flash("This email address isn't registered.")
                return redirect(url_for("auth.login"))

            if not check_password_hash(result[3], password):
                flash(f"Invalid credentials.")
                return redirect(url_for("auth.login"))

            job_seeker = JobSeeker(*result)
            login_user(job_seeker)

            return redirect(url_for("main.homepage"))

        except MySQLError as e:
            # print(e)
            flash(
                "Oops, there was an issue processing the login request. Please try again."
            )
            return redirect(url_for("auth.login"))


@auth.route("/signup", methods=["POST"])
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
            return redirect(url_for("auth.signup"))

        # check if passwords match
        if pw != confirm_pw:
            flash("Passwords don't match")
            return redirect(url_for("auth.signup"))

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
                INSERT INTO job_seeker (fname, lname, phone, account_id)
                VALUES (%s, %s, %s, %s);
                """,
                (fname, lname, phone, account_id),
            )

            conn.commit()
        except MySQLError as e:
            print(e)
            conn.rollback()
            flash("Oops! There was an issue with sign up. Please try again")
            return redirect(url_for("auth.signup"))

    return redirect(url_for("auth.login"))


# TODO logout should be a POST request
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
