from flask import Blueprint, request, flash, redirect, url_for, Response, current_app
from flask.json import jsonify
from flask_login.utils import login_required
from flask_login import current_user

from app.decorators import company_login_required, authorize_company
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
        return redirect(url_for("homepage"))

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
@authorize_company
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
        (
            job_name,
            _,
            company_id,
            job_description,
            apply_deadline,
        ) = cursor.fetchone()

        current_app.logger.info("job_name " + job_name)
        current_app.logger.info("job_description " + job_description)
        current_app.logger.info("apply_deadline " + str(apply_deadline))

        # skills_dict = get_job_skills(job_id, cursor)

        skills_query = """SELECT skill.id, skill.sname, job_skill_requirements.min_proficiency
        FROM job_skill_requirements
        INNER JOIN skill
        ON job_skill_requirements.skill_id = skill.id
        WHERE job_skill_requirements.job_id = %s;
        """

        all_skills_query = """SELECT id, sname
        FROM skill
        WHERE id NOT IN (
            SELECT skill_id
            FROM job_skill_requirements
            WHERE job_id = %s
        );
        """

        cursor.execute(skills_query, job_id)
        result = cursor.fetchall()

        cursor.execute(all_skills_query, job_id)
        all_skills = cursor.fetchall()

        conn.commit()

        return render_company_page(
            "company-posting.html",
            job_title=job_name,
            company_id=company_id,
            description=job_description,
            app_deadline=apply_deadline.strftime("%Y-%m-%d"),
            skills=result,
            all_skills=all_skills,
            existing_posting=True,
            job_id=job_id
        )


@company.route("/add_job")
@company_login_required
def add_job():
    return render_company_page(
        "company-posting.html",
        existing_posting=False
    )


@company.route("/change_proficiency/<int:job_id>", methods=["PUT"])
@company_login_required
@authorize_company
def update_job_skills(job_id):
    skill_id = int(request.args.get("skill_id"))
    proficiency = int(request.args.get("proficiency"))

    query = """UPDATE job_skill_requirements
    SET proficiency = %s
    WHERE skill_id = %s
    AND job_id = %s;
    """

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (proficiency, skill_id, job_id))
        flash("Changes saved", "info")
        return jsonify(success=True)


@company.route("/delete_skill/<int:job_id>", methods=["DELETE"])
@company_login_required
@authorize_company
def delete_skill(job_id):
    skill_id = request.args.get("skill_id")

    query = """DELETE FROM job_skill_requirements
    WHERE job_id = %s
    AND skill_id =%s;
    """

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (job_id, skill_id))
        return jsonify(success=True)


# TODO add location
@company.route("/add_job", methods=["POST"])
@company_login_required
def add_posting():
    query = """INSERT INTO job (jname, company_id, description, apply_deadline)
    VALUES (%s, %s, %s, %s);
    """

    title = request.form.get("job-title")
    description = request.form.get("description")
    apply_deadline = request.form.get("deadline")

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (title, current_user.id, description, apply_deadline))
        conn.commit()
        flash("Job successfully added", "info")
        return redirect(url_for("company.homepage"))


@company.route("/update_job/<int:job_id>", methods=["POST"])
@company_login_required
@authorize_company
def update_posting(job_id):
    query = """UPDATE job SET
    jname = %s,
    description = %s,
    apply_deadline = %s
    WHERE id = %s;
    """

    title = request.form.get("job-title")
    description = request.form.get("description")
    apply_deadline = request.form.get("deadline")

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (title, description, apply_deadline, job_id))
        conn.commit()
        flash("Changes saved", "info")
        return redirect(url_for("company.view_job", job_id=job_id))
