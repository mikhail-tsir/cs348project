from flask import Blueprint, render_template
from flask_login import current_user

from app.decorators import jobseeker_login_required
from app import db

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
        skills=get_skills(current_user.id)
    )
