from . import generate_company_account, generate_job_seeker_account, add_account_to_db, all_skills
from itertools import chain
import os

import pymysql

password = os.environ["MYSQL_ROOT_PASSWORD"]
database = os.environ["MYSQL_DATABASE"]

with pymysql.connect(host='db', user='root', password=password, database=database) as connection:
    with connection.cursor() as cursor:
        cursor.executemany("INSERT INTO skill (sname) VALUES (%s)", all_skills)

        for account in chain((generate_company_account() for _ in range(500)), (generate_job_seeker_account() for _ in range(800))):
            add_account_to_db(account, cursor)
    connection.commit()
