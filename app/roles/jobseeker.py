from flask import Blueprint, current_app, jsonify, render_template, request
from flask.wrappers import Response
from flask_login import current_user

from app.decorators import jobseeker_login_required
from app import db

import logging

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

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(skills_query, current_user.id)

        # (skill_id, skill_name, proficiency) tuples
        result = cursor.fetchall()

        return render_jobseeker_page("skills.html", skills=result)


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
