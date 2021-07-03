from . import generate_company_account, generate_job_seeker_account, add_account_to_db, all_skills
from itertools import chain
from time import sleep
import os

import pymysql
from pymysql.constants import CLIENT

password = os.environ["MYSQL_ROOT_PASSWORD"]
database = os.environ["MYSQL_DATABASE"]

retry_count = 5

while True:
    try:
        with pymysql.connect(host="db", user="root", password=password, database=database, client_flag=CLIENT.MULTI_STATEMENTS) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """DELETE FROM job_skill_requirements WHERE 1 = 1;
                    DELETE FROM job_seeker_skill WHERE 1 = 1;
                    DELETE FROM application WHERE 1 = 1;
                    DELETE FROM skill WHERE 1 = 1;
                    DELETE FROM job WHERE 1 = 1;
                    DELETE FROM job_seeker WHERE 1 = 1;
                    DELETE FROM company WHERE 1 = 1;
                    DELETE FROM account WHERE 1 = 1;
                    """
                )
                cursor.executemany("INSERT INTO skill (sname) VALUES (%s)", all_skills)

                for account in chain((generate_company_account() for _ in range(500)), (generate_job_seeker_account() for _ in range(800))):
                    add_account_to_db(account, cursor)
            connection.commit()
    except pymysql.err.OperationalError as e:
        if retry_count < 0:
            raise e
        
        sleep(5)
        retry_count -= 1
