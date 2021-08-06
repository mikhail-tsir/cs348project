from app import db
from flask import current_app, flash
from flask_login import current_user

import logging


MAX_FILE_SIZE = 65535  # max number of bytes for mysql BLOB type


def has_resume():
    query = """SELECT 1
    FROM job_seeker
    WHERE id = %s
    AND cv IS NULL
    """

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, current_user.id)
        result = cursor.fetchall()
        return len(result) == 0


def get_resume_filename():
    if not current_user.is_authenticated:
        return None

    return f"{current_user.user.fname}_{current_user.user.lname}.pdf"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() == "pdf"


def upload_file(filename):
    with open(filename, "rb") as file:
        blob = file.read()

        if len(blob) >= MAX_FILE_SIZE:
            flash("Your file is too big. Please upload a smaller file.")
            return

        # insert resume as blob in db
        with db.connect() as conn, conn.cursor() as cursor:
            query = """UPDATE job_seeker
            SET cv = %s
            WHERE id = %s;
            """

            try:
                cursor.execute(query, (blob, current_user.id))
                conn.commit()
            except Exception as e:
                current_app.logger.info(e)
                flash("Oops, there was an error uploading your file. Try again.")
