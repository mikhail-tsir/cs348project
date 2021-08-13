from flask import flash, redirect, request, url_for, Response
from flask_login import login_user
from pymysql.err import MySQLError
from typing import Tuple
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models import Account, JobSeeker, Company

from app.util.form_util import validate_form

import re


def create_user_model(user_type: str, attributes: Tuple):
    if user_type == "jobseeker":
        (id, fname, lname, email, password) = attributes
        return Account(id, email, password, JobSeeker(fname, lname))

    (id, name, email, password) = attributes
    return Account(id, email, password, Company(name))


def generic_login(user_type):
    if not validate_form(request, ["email", "password"]):
        flash("Required form fields must not be empty.")
        return redirect(url_for(".login"))
    
    email, password = request.form.get("email").lower(), request.form.get("password")

    with db.connect() as conn:
        try:
            cursor = conn.cursor()
            # check if user exists
            user_view_name = (
                "job_seeker_account" if user_type == "jobseeker" else "company_account"
            )
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
            return redirect(url_for(".login"))


def insert_new_user(user_type, cursor, conn):
    if not validate_form(request, ["email", "password"]):
        flash("Required form fields must not be empty.")
        return redirect(url_for(".signup"))
        
    hashed_pw = generate_password_hash(request.form.get("password"))

    # insert account info first
    cursor.execute(
        """
        INSERT INTO account (email, password)
        VALUES (%s, %s);
        """,
        (request.form.get("email").lower(), hashed_pw),
    )

    conn.commit()

    # get id of newly inserted user
    cursor.execute(
        """
        SELECT id FROM account
        WHERE email = %s;
        """,
        request.form.get("email").lower(),
    )

    result = cursor.fetchone()
    account_id = result[0] if result else -1

    # for jobseeker accounts
    if user_type == "jobseeker":
        if not validate_form(request, ["fname", "lname", "phone"]):
            flash("Required form fields must not be empty.")
            return redirect(url_for(".signup"))
        
        if not re.fullmatch(r"\d{10}", request.form["phone"]):
            flash("Invalid phone")
            return redirect(url_for(".signup"))

        cursor.execute(
            """
            INSERT INTO job_seeker (fname, lname, phone, id)
            VALUES (%s, %s, %s, %s);
            """,
            (
                request.form["fname"],
                request.form["lname"],
                request.form["phone"],
                account_id,
            ),
        )
        conn.commit()
        return

    # for company accounts
    if not validate_form(request, ["name", "description", "website"]):
        flash("Required form fields must not be empty.")
        return redirect(url_for(".signup"))

    cursor.execute(
        """
        INSERT INTO company (name, description, website, id)
        VALUES (%s, %s, %s, %s);
        """,
        (request.form["name"], request.form["description"], request.form["website"], account_id),
    )
    conn.commit()


def generic_signup(user_type):
    if not validate_form(request, ["password", "confirm_password", "email"]):
        flash("Required form fields must not be empty.")
        return redirect(url_for(".signup"))

    password, confirm_password = (
        request.form.get("password"),
        request.form.get("confirm_password"),
    )

    with db.connect() as conn, conn.cursor() as cursor:
        # check if user already exists
        cursor.execute(
            "SELECT * FROM account WHERE email = %s", (request.form.get("email"),)
        )
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
        if len(password) < MIN_PASSWORD_LENGTH:
            flash(
                f"Password is not secure enough (must be at least {MIN_PASSWORD_LENGTH} characters)."
            )
            return redirect(url_for(".signup"))
        
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(email_regex, request.form["email"]):
            flash("Invalid email.")
            return redirect(url_for(".signup"))

        try:
            insert_new_user(user_type, cursor, conn)
            conn.commit()
        except MySQLError as e:
            # print(e)
            raise e
            conn.rollback()
            flash("Oops! There was an issue with sign up. Please try again")
            return redirect(url_for(".signup"))

    return redirect(url_for(".login"))
