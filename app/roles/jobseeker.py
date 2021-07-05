from flask import Blueprint, render_template
from flask_login import current_user

from app.decorators import jobseeker_login_required
from app import db

jobseeker = Blueprint("jobseeker", __name__)


def display_job_dicts(jobseeker_id):
    # TODO get rid of limit and paginate results
    query = """SELECT temp.id, temp.jname, company.description, company.name
    FROM (
        SELECT job.*
        FROM relevance
        INNER JOIN job
        ON relevance.job_id = job.id
        AND relevance.job_seeker_id = %s
        AND job.apply_deadline <= CURRENT_TIMESTAMP
        ORDER BY relevance.score DESC
    ) AS temp
    INNER JOIN company
        ON company.id = temp.company_id
    LIMIT 10;"""

    # query = """SELECT *
    # FROM job_seeker_account
    # LIMIT 10;"""

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query)

        # id, jname, company_id, description, apply_deadline, company.name
        result = cursor.fetchall()

        # return result

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
                    "company": row[5],
                    "location": "Ottawa, ON",
                    "description": row[3],
                    "min_skill_proficiencies": skills_dict,
                }
            )

        return job_dicts


@jobseeker.route("/homepage")
@jobseeker_login_required
def homepage():
    # jobs_dict = {
    #     "title": "Backend Software Engineer",
    #     "company": "TechnoCorp",
    #     "location": "Ottawa, ON",
    #     "description": "We are looking for a talented Backend engineer to work on our public API.\nCome join us!",
    #     "min_skill_proficiencies": {"Relational Databases": 3, "C++": 1},
    # }
    job_dicts = display_job_dicts(current_user.id)
    return render_template(
        "jobseeker-homepage.html",
        fname=current_user.user.fname,
        lname=current_user.user.lname,
        job_previews=job_dicts,
    )

    # return str(display_job_dicts(current_user.id))
