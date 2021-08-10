from flask import render_template
from flask_login import current_user


def get_jobseeker_skills(jobseeker_id):
    query = """SELECT skill.sname, proficiency
    FROM job_seeker_skill
    INNER JOIN skill
    ON skill_id = id
    AND job_seeker_id = %s;
    """

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(query, (jobseeker_id,))

        return {pair[0]: pair[1] for pair in cursor.fetchall()}


def render_jobseeker_page(filename, **kwargs):
    return render_template(
        filename, fname=current_user.user.fname, lname=current_user.user.lname, **kwargs
    )
