from flask_login import current_user
from app import db


def get_job_skills(job_id, cursor):
    skills_query = """
    SELECT skill.sname, job_skill_requirements.min_proficiency
    FROM job_skill_requirements
    INNER JOIN skill
    ON job_skill_requirements.skill_id = skill.id
    AND job_skill_requirements.job_id = %s;
    """

    cursor.execute(skills_query, job_id)
    return {pair[0]: pair[1] for pair in cursor.fetchall()}


def display_job_dicts(data, cursor):
    job_dicts = []

    for row in data:
        job_id = row[0]
        skills_dict = get_job_skills(job_id, cursor)
        job_dicts.append(
            {
                "id": job_id,
                "title": row[1],
                "company": row[3],
                "company_id": row[4],
                "location": "Ottawa, ON",
                "description": row[2],
                "min_skill_proficiencies": skills_dict,
            }
        )

    return job_dicts


def get_recommended_jobs():
    # TODO get rid of limit and paginate results
    query = """SELECT temp.id, temp.jname, temp.description, company.name, company.id, temp.score
    FROM (
        SELECT job.*, relevance.score
        FROM relevance
        INNER JOIN job
        ON relevance.job_id = job.id
        AND relevance.job_seeker_id = %s
        AND job.apply_deadline >= CURRENT_TIMESTAMP
    ) AS temp
    INNER JOIN company
        ON company.id = temp.company_id
    ORDER BY score DESC
    LIMIT 10;"""

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, current_user.id)
        return display_job_dicts(cursor.fetchall(), cursor)


def get_applications():
    query = """SELECT job.id, job.jname, job.description, company.name, company.id
    FROM job
    INNER JOIN application
    ON job.id = application.job_id
    INNER JOIN company
    ON company.id = job.company_id
    WHERE application.job_seeker_id = %s;
    """

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, current_user.id)
        return display_job_dicts(cursor.fetchall(), cursor)


def get_jobs_by_company(company_id):
    # TODO get rid of limit and paginate results
    query = """SELECT job.id, job.jname, job.description, company.name, company.id
    FROM job
    INNER JOIN company
    ON job.company_id = company.id
    WHERE company.id = %s
    LIMIT 10;
    """

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, company_id)
        return display_job_dicts(cursor.fetchall(), cursor)
