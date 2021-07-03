from . import generate_company_account, generate_job_seeker_account, add_account_to_db, all_skills
from itertools import chain
import os
import random

import pymysql
from pymysql.constants import CLIENT

password = os.environ["MYSQL_ROOT_PASSWORD"]
database = os.environ["MYSQL_DATABASE"]

random.seed("f158d13d-1069-4282-b8d2-9826cc729338")

with pymysql.connect(host="db", user="root", password=password, database=database, client_flag=CLIENT.MULTI_STATEMENTS) as connection:
    with connection.cursor() as cursor:
        cursor.executemany("INSERT INTO skill (sname) VALUES (%s)", all_skills)

        for account in chain((generate_company_account() for _ in range(500)), (generate_job_seeker_account() for _ in range(800))):
            add_account_to_db(account, cursor)
    connection.commit()
