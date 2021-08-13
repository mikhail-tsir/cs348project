from flask import Blueprint, request, flash, redirect, send_file, url_for, Response, current_app
from flask.json import jsonify
from flask_login.utils import login_required
from flask_login import current_user

from app.decorators import company_login_required, authorize_company
from app.models import Company, JobSeeker

from app.util.jobseeker_util import render_jobseeker_page, get_jobseeker_skills
from app.util.company_util import get_company_description, render_company_page
from app.util.job_util import get_jobs_by_company, get_job_skills
from app.util.form_util import validate_form

from app import db

import tempfile

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
    _, description, website = get_company_description(current_user.id)
    return render_company_page("company-profile.html", description=description, website=website)


@company.route("/change_description", methods=["POST"])
@company_login_required
def about_post():
    if not validate_form(request, ["description", "website"]):
        flash("Required fields must not be empty")
        return Response(status=204)
    
    description = request.form.get("description")
    website = request.form.get("website")

    query = """UPDATE company
    SET description = %s,
    website = %s
    WHERE id = %s;
    """

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (description, website, current_user.id))
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

        job_query = """SELECT jname, company.id, job.description, location, apply_deadline
        FROM job
        INNER JOIN company
        ON job.company_id = company.id
        WHERE job.id = %s;
        """

        cursor.execute(job_query, job_id)
        (
            job_name,
            company_id,
            job_description,
            location,
            apply_deadline,
        ) = cursor.fetchone()

        # current_app.logger.info("job_name " + job_name)
        # current_app.logger.info("job_description " + job_description)
        # current_app.logger.info("apply_deadline " + str(apply_deadline))

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

        current_app.logger.info("Job skills:")
        current_app.logger.info(str(result))

        cursor.execute(all_skills_query, job_id)
        all_skills = cursor.fetchall()

        conn.commit()

        return render_company_page(
            "company-posting.html",
            job_title=job_name,
            company_id=company_id,
            description=job_description,
            app_deadline=apply_deadline.strftime("%Y-%m-%d"),
            location=location,
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
    SET min_proficiency = %s
    WHERE skill_id = %s
    AND job_id = %s;
    """

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (proficiency, skill_id, job_id))
        conn.commit()
        flash("Changes saved", "info")
        return jsonify(success=True)


@company.route("/add_skill/<int:job_id>", methods=["POST"])
@company_login_required
@authorize_company
def add_skill(job_id):
    skill_id = request.args.get("skill_id")

    query = """INSERT INTO job_skill_requirements (job_id, skill_id, min_proficiency)
    VALUES (%s, %s, 1);
    """

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (job_id, skill_id))
        conn.commit()
        flash("Changes saved")
        return redirect(url_for("company.view_job", job_id=job_id))


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
        conn.commit()
        return redirect(url_for("company.view_job", job_id=job_id))


@company.route("/add_job", methods=["POST"])
@company_login_required
def add_posting():
    query = """INSERT INTO job (jname, company_id, description, location, apply_deadline)
    VALUES (%s, %s, %s, %s, %s);
    """

    if not validate_form(request, ["job-title", "description", "deadline", "location"]):
        flash("Required fields must not be empty.")
        return Response(status=204)

    title = request.form.get("job-title")
    description = request.form.get("description")
    apply_deadline = request.form.get("deadline")
    location = request.form.get("location")

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (title, current_user.id, description, location, apply_deadline))
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

    if not validate_form(request, ["job-title", "description", "deadline"]):
        flash("Required form fields must not be empty")
        return Response(status=204)

    title = request.form.get("job-title")
    description = request.form.get("description")
    apply_deadline = request.form.get("deadline")

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (title, description, apply_deadline, job_id))
        conn.commit()
        flash("Changes saved", "info")
        return redirect(url_for("company.view_job", job_id=job_id))


@company.route("/applicants/<int:job_id>")
@company_login_required
@authorize_company
def view_applicants(job_id):
    query = """SELECT job_seeker.id, job_seeker.fname, job_seeker.lname, account.email, job_seeker.phone
    FROM relevance 
    INNER JOIN job_seeker
        ON relevance.job_seeker_id = job_seeker.id
    INNER JOIN application
        ON application.job_seeker_id = job_seeker.id
    INNER JOIN account
        ON account.id = job_seeker.id
    WHERE application.job_id = %s
    ORDER BY relevance.score DESC;
    """

    job_query = """SELECT job.jname
    FROM job
    WHERE id = %s;
    """

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, job_id)
        # (id, fname, lname) tuples
        result = cursor.fetchall()

        # TODO is this valid python?
        # { id : (fname, lname, skills_dict) }
        applicants = {r[0] : (r[1], r[2], get_jobseeker_skills(r[0]), r[3], r[4]) for r in result}

        cursor.execute(job_query, job_id)
        result = cursor.fetchone()

        return render_company_page("applicants.html", applicants=applicants, job_title=result[0], job_id=job_id)


@company.route("/delete_posting/<int:job_id>", methods=["DELETE"])
@company_login_required
@authorize_company
def delete_posting(job_id):
    query = """DELETE FROM job
    WHERE job_id = %s;
    """

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, job_id)
        conn.commit()
        return redirect(url_for("company.homepage"))


@company.route("/download_resume/<int:jobseeker_id>")
@company_login_required
def download_resume(jobseeker_id):
    query = """SELECT fname, lname, cv FROM job_seeker WHERE id = %s;"""

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, jobseeker_id)
        result = cursor.fetchone()
        file_bytes = result[2]

        if not file_bytes:
            # file does not exist
            flash("This user has not uploaded a resume.")
            return Response(status=204)

        with tempfile.NamedTemporaryFile() as f, open(f.name, "wb") as temp_file:
            temp_file.write(file_bytes)
            filename = f"{result[0]}_{result[1]}.pdf"
            return send_file(f.name, as_attachment=True, attachment_filename=filename)
