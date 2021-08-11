from flask import Blueprint, request, flash, redirect, url_for, Response
from flask.json import jsonify
from flask_login.utils import login_required
from flask_login import current_user

from app.decorators import company_login_required
from app.models import Company, JobSeeker

from app.util.jobseeker_util import render_jobseeker_page
from app.util.company_util import get_company_description, render_company_page
from app.util.job_util import get_jobs_by_company, get_job_skills

from app import db

company = Blueprint("company", __name__)


@company.route("/homepage")
@company_login_required
def homepage():
    job_dicts = get_jobs_by_company(current_user.id)
    return render_company_page("company-homepage.html", job_previews=job_dicts)


@company.route("/<int:company_id>/jobs")
@login_required
def jobs(company_id):
    job_dicts = get_jobs_by_company(company_id)
    company_name = job_dicts[0]["company"]

    if type(current_user.user) == Company:
        return redirect(url_for('homepage'))

    return render_jobseeker_page(
        "job-previews.html", title=company_name, job_previews=job_dicts
    )


@company.route("/about")
@company_login_required
def about_page():
    _, description = get_company_description(current_user.id)
    return render_company_page("company-profile.html", description=description)


@company.route("/change_description", methods=["POST"])
@company_login_required
def about_post():
    description = request.form.get("description")

    query = """UPDATE company
    SET description = %s
    WHERE id = %s;
    """

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (description, current_user.id))
        conn.commit()
        flash("Description successfully updated", "info")
        return redirect(url_for("company.about_page"))


@company.route("/job/<int:job_id>")
@company_login_required
def view_job(job_id):
    # make sure job belongs to current company
    query = """SELECT company_id FROM job
    WHERE id = %s;
    """

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, job_id)
        result = cursor.fetchone()
        if len(result) == 0:
            return Response(404)
        
        if result[0] != current_user.id:
            return Response(401)
        
        job_query = """SELECT jname, company.name, company.id, job.description, apply_deadline
        FROM job
        INNER JOIN company
        ON job.company_id = company.id
        WHERE job.id = %s;
        """

        cursor.execute(job_query, job_id)
        (job_name, company_name, company_id, job_description, apply_deadline) = cursor.fetchone()

        skills_dict = get_job_skills(job_id, cursor)

        return render_company_page(
            "company-posting.html",
            job_name=job_name,
            company_name=company_name,
            company_id=company_id,
            job_description=job_description,
            apply_deadline=apply_deadline,
            skills_dict=skills_dict,
            existing_posting=True
        )
