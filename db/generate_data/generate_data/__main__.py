from . import generate_company_account, generate_job_seeker_account, add_account_to_db, all_skills, create_random_job_application
import os
import random
import time

import pymysql

from tqdm import tqdm

password = os.environ["MYSQL_ROOT_PASSWORD"]
database = os.environ["MYSQL_DATABASE"]

random.seed("f158d13d-1069-4282-b8d2-9826cc729338")

def establish_connection():
    tries = 5
    for try_ in range(tries):
        print("Connecting to database")
        try:
            return pymysql.connect(host="db", user="root", password=password, database=database)
        except pymysql.err.OperationalError:
            print("Failed to connect")
            if try_ in range(tries - 1):
                print("Waiting to retry")
                time.sleep(5)
    raise RuntimeError("Failed to connect to database")

with establish_connection() as connection:
    with connection.cursor() as cursor:
        cursor.executemany("INSERT INTO skill (sname) VALUES (%s)", ((skill,) for skill in all_skills))

        for _ in tqdm(range(500), desc="Generating companies"):
            add_account_to_db(generate_company_account(), cursor)
            connection.commit()
        
        for _ in tqdm(range(1000), desc="Generating job seekers"):
            add_account_to_db(generate_job_seeker_account(), cursor)
            connection.commit()
        
        for _ in tqdm(range(600), desc="Generating job applications"):
            create_random_job_application(cursor)
            connection.commit()
