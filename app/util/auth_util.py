from flask import flash, redirect, request, url_for
from flask_login import login_user
from pymysql.err import MySQLError
from typing import Tuple
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models import Account, JobSeeker, Company


def create_user_model(user_type: str, attributes: Tuple):
    if user_type == "jobseeker":
        (id, fname, lname, email, password) = attributes
        return Account(id, email, password, JobSeeker(fname, lname))
    
    (id, name, email, password) = attributes
    return Account(id, email, password, Company(name))


def generic_login(user_type):
    email, password = request.form.get("email"), request.form.get("password")

    with db.connect() as conn:
        try:
            cursor = conn.cursor()
            # check if user exists
            user_view_name = "job_seeker_account" if user_type == "jobseeker" else "company_account"
            cursor.execute(f"SELECT * FROM {user_view_name} WHERE email = %s;", email)
            result = cursor.fetchone()

            if not result:
                flash("This email address isn't registered.")
                return redirect(url_for(".login"))
            
            if not check_password_hash(result[-1], password):
                flash("Invalid Credentials.")
                return redirect(url_for(".login"))

            user = create_user_model(user_type, result)
            login_user(user)

            return redirect(url_for(f"{user_type}.homepage"))

        except MySQLError:
            flash(
                "Oops, there was an issue processing the login request. Please try again."
            )
            return redirect(url_for(f".login"))


def insert_new_user(user_type, form, cursor):
    hashed_pw = generate_password_hash(form.get("password"))

    # insert account info first
    cursor.execute(
        """
        INSERT INTO account (email, password)
        VALUES (%s, %s);
        """,
        (form.get("email"), hashed_pw),
    )

    # get id of newly inserted user
    cursor.execute(
        """
        SELECT id FROM account
        WHERE email = %s;
        """,
        form["email"],
    )

    result = cursor.fetchone()
    account_id = result[0] if result else -1

    # for jobseeker accounts
    if user_type == "jobseeker":
        cursor.execute(
            """
            INSERT INTO job_seeker (fname, lname, phone, id)
            VALUES (%s, %s, %s, %s);
            """,
            (form["fname"], form["lname"], form["phone"], account_id),
        )
        return
    
    # for company accounts
    cursor.execute(
        """
        INSERT INTO company (name, description)
        VALUES (%s, %s);
        """,
        (form["name"], form["description"])
    )



def generic_signup(user_type, form):
    password, confirm_password = (
        form.get("password"),
        form.get("confirm_password"),
    )

    with db.connect() as conn, conn.cursor() as cursor:
        # check if user already exists
        cursor.execute("SELECT * FROM account WHERE email = %s", form.get("email"))
        result = cursor.fetchall()

        if result:
            flash("User already exists")
            return redirect(url_for(".signup"))

        # check if passwords match
        if password != confirm_password:
            flash("Passwords don't match")
            return redirect(url_for(".signup"))

        MIN_PASSWORD_LENGTH = 4
        
        # validate password
        # TODO better validation
        if len(password) < MIN_PASSWORD_LENGTH:
            flash(f"Password is not secure enough (must be at least {MIN_PASSWORD_LENGTH} characters).")
            return redirect(url_for(".signup"))

        try:
            insert_new_user(user_type, form, cursor)
            conn.commit()
        except MySQLError as e:
            print(e)
            conn.rollback()
            flash("Oops! There was an issue with sign up. Please try again")
            return redirect(url_for(".signup"))

    return redirect(url_for(".login"))
