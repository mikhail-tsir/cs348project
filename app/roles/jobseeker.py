from operator import ge
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


jobseeker = Blueprint("jobseeker", __name__)


def get_skills(jobseeker_id):
    query = """SELECT skill.sname, proficiency
    FROM job_seeker_skill
    INNER JOIN skill
    ON skill_id = id
    AND job_seeker_id = %s;
    """

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (jobseeker_id,))

        return {pair[0]: pair[1] for pair in cursor.fetchall()}


def display_job_dicts(jobseeker_id):
    # TODO get rid of limit and paginate results
    query = """SELECT temp.id, temp.jname, temp.description, company.name, temp.score
    FROM (
        SELECT job.*, relevance.score
        FROM relevance
        INNER JOIN job
        ON relevance.job_id = job.id
        AND relevance.job_seeker_id = %s
        AND job.apply_deadline <= CURRENT_TIMESTAMP
    ) AS temp
    INNER JOIN company
        ON company.id = temp.company_id
    ORDER BY score DESC
    LIMIT 10;"""

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (jobseeker_id,))

        # id, jname, description, company.name, relevance_score
        result = cursor.fetchall()

        job_dicts = []

        for row in result:
            job_id = row[0]
            skills_query = """
            SELECT skill.sname, job_skill_requirements.min_proficiency
            FROM job_skill_requirements
            INNER JOIN skill
            ON job_skill_requirements.skill_id = skill.id
            AND job_skill_requirements.job_id = %s;
            """

            cursor.execute(skills_query, (job_id,))
            skills_dict = {pair[0]: pair[1] for pair in cursor.fetchall()}

            job_dicts.append(
                {   
                    "id": job_id,
                    "title": row[1],
                    "company": row[3],
                    "location": "Ottawa, ON",
                    "description": row[2],
                    "relevance": row[4],
                    "min_skill_proficiencies": skills_dict,
                }
            )

        return job_dicts


@jobseeker.route("/homepage")
@jobseeker_login_required
def homepage():
    job_dicts = display_job_dicts(current_user.id)
    return render_template(
        "jobseeker-homepage.html",
        fname=current_user.user.fname,
        lname=current_user.user.lname,
        job_previews=job_dicts,
        skills=get_skills(current_user.id),
    )


def render_jobseeker_page(filename, **kwargs):
    return render_template(
        filename, fname=current_user.user.fname, lname=current_user.user.lname, **kwargs
    )


@jobseeker.route("/job/<int:job_id>")
@jobseeker_login_required
def view_job(job_id):
    return render_jobseeker_page("job-details.html")


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
        # cursor.execute("SELECT * FROM job_seeker_skill WHERE skill_id = %s AND job_seeker_id = %s", (skill_id, current_user.id))
        # result = cursor.fetchall()
        # current_app.logger.info(result)
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
