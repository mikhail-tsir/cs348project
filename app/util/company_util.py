from app import db
from flask import render_template
from flask_login import current_user


def get_company_description(company_id):
    query = """SELECT name, description
    FROM company
    WHERE id = %s;
    """

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, company_id)
        return cursor.fetchall()[0]


def render_company_page(filename, **kwargs):
    return render_template(filename, company_name=current_user.user.name, **kwargs)
