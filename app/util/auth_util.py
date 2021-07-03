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


def generic_login(user_type, body_func):
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
                return redirect(url_for(f"{user_type}.login"))
            
            if not check_password_hash(result[-1], password):
                flash("Invalid Credentials.")
                return redirect(url_for(f"{user_type}.login"))

            user = create_user_model(user_type)
            login_user(user)

            return redirect(url_for(f"{user_type}.homepage"))

        except MySQLError as e:
            flash(
                "Oops, there was an issue processing the login request. Please try again."
            )
            return redirect(url_for(f"{user_type}.login"))
