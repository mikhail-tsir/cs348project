from flask import render_template, Blueprint, redirect, url_for
from flask_login import login_required, logout_user

base = Blueprint("base", __name__)


@base.route("/")
def index():
    # for henry: comment this out
    return render_template("index.html")

    # uncomment this:

    # from app import db
    # with db.connect() as conn, conn.cursor() as cursor:
    #     queries = [
    #         """
    #         CONTENTS OF QUERY 1
    #         """,
    #         ...,
    #         """
    #         CONTENTS OF QUERY N
    #         """
    #     ]

    #     res = ""
    #     for query in queries:
    #         cursor.execute(query)
    #         for row in cursor.fetchall():
    #             res += str(row) + "\n"
    #         res += "\n"
        
    #     return res

    # now run the app and when you navigate to the front page, the output of the query should be there


# TODO logout should be a POST request
@base.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("base.index"))