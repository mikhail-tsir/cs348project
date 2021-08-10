import os
import logging
import tempfile

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask.wrappers import Response
from flask_login import current_user
from werkzeug.utils import secure_filename

from app.decorators import jobseeker_login_required
from app import db
from app.util.resume_file_util import (
    has_resume,
    get_resume_filename,
    allowed_file,
    upload_file,
)
from app.util.job_util import (
    get_applications,
    get_job_skills,
    get_recommended_jobs,
)
from app.util.jobseeker_util import get_jobseeker_skills, render_jobseeker_page


jobseeker = Blueprint("jobseeker", __name__)


@jobseeker.route("/homepage")
@jobseeker_login_required
def homepage():
    job_dicts = get_recommended_jobs()
    return render_jobseeker_page(
        "jobseeker-homepage.html",
        job_previews=job_dicts,
        skills=get_jobseeker_skills(current_user.id),
    )


@jobseeker.route("/applications")
@jobseeker_login_required
def applications():
    job_dicts = get_applications()
    return render_jobseeker_page("my-applications.html", job_previews=job_dicts)


@jobseeker.route("/job/<int:job_id>")
@jobseeker_login_required
def view_job(job_id):
    exists_query = """SELECT 1 FROM application
    WHERE job_seeker_id = %s
    AND job_id = %s;
    """

    job_data_query = """SELECT jname, company.name, company.id, job.description, apply_deadline
    FROM job
    INNER JOIN company
    ON job.company_id = company.id
    WHERE job.id = %s;
    """

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(exists_query, (current_user.id, job_id))
        result = cursor.fetchall()
        already_applied = len(result) > 0

        skills_dict = get_job_skills(job_id, cursor)
        cursor.execute(job_data_query, job_id)
        result = cursor.fetchall()[0]

        return render_jobseeker_page(
            "job-details.html",
            job_id=job_id,
            job_title=result[0],
            company_name=result[1],
            company_id=result[2],
            job_location="Ottawa, ON",  # TODO add location column
            job_description=result[3],
            app_deadline=result[4],
            applied=already_applied,
            skills=skills_dict,
        )


@jobseeker.route("/apply/<int:job_id>", methods=["POST"])
@jobseeker_login_required
def apply(job_id):
    query = """INSERT INTO application (job_seeker_id, job_id)
    VALUES (%s, %s);
    """

    with db.connect() as conn, conn.cursor() as cursor:
        try:
            cursor.execute(query, (current_user.id, job_id))
            conn.commit()
            flash("Thank you for submitting your application!", "info")
        except:
            flash("There was an issue submitting your application.")

        return redirect(url_for(".view_job", job_id=job_id))


@jobseeker.route("/withdraw/<int:job_id>", methods=["POST"])
@jobseeker_login_required
def withdraw(job_id):
    query = """DELETE FROM application
    WHERE job_seeker_id = %s
    AND job_id = %s;
    """

    with db.connect() as conn, conn.cursor() as cursor:
        try:
            cursor.execute(query, (current_user.id, job_id))
            cursor.execute("SELECT ROW_COUNT();")
            conn.commit()
            result = cursor.fetchall()[0]
            if result[0] == 0:
                flash("You have not applied to this job.")
            else:
                flash("Successfully withdrawn application", "info")
        except Exception as e:
            current_app.logger.info(e)
            flash("Something went wrong trying to withdraw your application.")

        return redirect(url_for(".view_job", job_id=job_id))


@jobseeker.route("/skills")
@jobseeker_login_required
def skills_page():
    # get current user's skills
    skills_query = """SELECT skill.id, skill.sname, job_seeker_skill.proficiency
    FROM job_seeker_skill
    INNER JOIN skill
    ON job_seeker_skill.skill_id = skill.id
    WHERE job_seeker_skill.job_seeker_id = %s;
    """

    all_skills_query = """SELECT id, sname
    FROM skill
    WHERE id NOT IN (
        SELECT skill_id
        FROM job_seeker_skill
        WHERE job_seeker_id = %s
    );
    """

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(skills_query, current_user.id)

        # (skill_id, skill_name, proficiency) tuples
        result = cursor.fetchall()

        cursor.execute(all_skills_query, current_user.id)
        all_skills = cursor.fetchall()
        conn.commit()

        resume_filename = get_resume_filename() if has_resume() else None

        return render_jobseeker_page(
            "skills.html",
            skills=result,
            all_skills=all_skills,
            resume_filename=resume_filename,
        )


@jobseeker.route("/delete_skill/<int:skill_id>", methods=["DELETE"])
@jobseeker_login_required
def delete_skill(skill_id):
    query = """DELETE FROM job_seeker_skill
    WHERE skill_id = %s
    AND job_seeker_id = %s;
    """

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (skill_id, current_user.id))
        conn.commit()
        return jsonify(success=True)


@jobseeker.route("/change_proficiency/<int:skill_id>", methods=["PUT"])
@jobseeker_login_required
def change_proficiency(skill_id):
    new_prof = int(request.args.get("proficiency"))
    query = """UPDATE job_seeker_skill
    SET proficiency = %s
    WHERE job_seeker_id = %s
    AND skill_id = %s;
    """

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (new_prof, current_user.id, skill_id))
        conn.commit()
        return jsonify(success=True)


@jobseeker.route("/add_skill", methods=["POST"])
@jobseeker_login_required
def add_skill():
    try:
        query = """
        INSERT INTO job_seeker_skill (job_seeker_id, skill_id, proficiency)
        VALUES (%s, %s, 1);
        """

        skill_id = int(request.form.get("add-skill"))

        with db.connect() as conn, conn.cursor() as cursor:
            cursor.execute(query, (current_user.id, skill_id))
            conn.commit()
    except:
        flash("Oops, there was an error adding your skill. Try again.")

    return redirect(url_for(".skills_page"))


@jobseeker.route("/upload_resume", methods=["POST"])
@jobseeker_login_required
def upload_resume():
    if "resume" not in request.files:
        flash("Oops, there doesn't seem to be a file there.")
        current_app.logger.info("could not find file in request")
        return redirect(url_for(".skills_page"))

    resume = request.files["resume"]

    if not resume or not resume.filename:
        flash("Oops, there doesn't seem to be a file there.")
        current_app.logger.info("Either file or filename is None")
        return redirect(url_for(".skills_page"))

    if allowed_file(resume.filename):
        filename = secure_filename(resume.filename)
        location = os.path.join("/tmp", filename)
        resume.save(location)
        upload_file(location)
    else:
        flash("This file type is not allowed. We only support .pdf files.")

    return redirect(url_for(".skills_page"))


@jobseeker.route("/download_resume")
@jobseeker_login_required
def download_resume():
    query = """SELECT cv FROM job_seeker WHERE id = %s;"""

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (current_user.id))
        result = cursor.fetchone()
        file_bytes = result[0]

        if not file_bytes:
            # file does not exist
            return redirect(url_for(".skills_page")), 404

        with tempfile.NamedTemporaryFile() as f, open(f.name, "wb") as temp_file:
            temp_file.write(file_bytes)
            filename = get_resume_filename()
            return send_file(f.name, as_attachment=True, attachment_filename=filename)
