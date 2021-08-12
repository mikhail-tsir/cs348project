from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal, TypeAlias

import random

import pymysql
import pymysql.cursors

from werkzeug.security import generate_password_hash

@dataclass
class Account:
    email: str
    password: str
    type: Company | JobSeeker

@dataclass
class Company:
    name: str
    description: str
    website: str
    jobs: list[Job]

@dataclass
class Proficiency:
    skill: Skill
    proficiency: Literal[1, 2, 3]

@dataclass
class JobSeeker:
    first_name: str
    last_name: str
    phone: str
    proficiencies: list[Proficiency]

Skill: TypeAlias = str

@dataclass
class SkillRequirement:
    skill: Skill
    proficiency: Literal[1, 2, 3]

@dataclass
class Job:
    name: str
    description: str
    deadline: datetime
    location: str
    requirements: list[SkillRequirement]


ProgrammerType: TypeAlias = Literal["frontend", "backend", "embedded", "mobile"]
programmer_types: list[ProgrammerType] = ["frontend", "backend", "embedded", "mobile"]
skills: dict[ProgrammerType, set[Skill]] = {
    "frontend": {"HTML5", "Typescript", "Bootstrap"},
    "backend": {"Python", "Java", "Kotlin", "Go", "REST", "HTTP", "SQL"},
    "embedded": {"C", "C++", "Rust"},
    "mobile": {"Kotlin", "Swift"},
}

all_skills = skills["frontend"] | skills["backend"] | skills["embedded"] | skills["mobile"]

locations = {"Ottawa", "Edmonton", "Victoria", "Winnipeg", "Toronto", "Quebec City", "Montreal", "Waterloo"}

job_names = ["QA Position", "QA Opening", "Junior Developer Position", "Entry level position", "Senior developer (>5 years)", "Senior Developer Position", "Full stack developer opening", "Mobile app dev"]
job_descriptions = [
    "Looking for a developer that takes the time to write high quality code", 
    "We offer an environment for fast growth and high skill variety",
    "We practice test driven development; we expect employees to write extensive testing.",
    "Looking for developer who is willing to learn on the job",
]

def generate_job() -> Job:
    relevant_skills = list(all_skills)
    random.shuffle(relevant_skills)
    requirements = [SkillRequirement(skill, random.choice([1,2,3])) for skill in relevant_skills[:6]]
    deadline = datetime.now() + timedelta(days=random.randrange(0,10), hours=random.randrange(0, 24), minutes=random.randrange(0, 60))
    return Job(
        name=random.choice(job_names),
        description=random.choice(job_descriptions),
        deadline=deadline,
        location=random.choice(list(locations)),
        requirements=requirements,
    )

def generate_name() -> str:
    consonants = [*"bcdfghjklmnpqrstvwxyz", "sh", "th", "ch", "gh", "dr", "tw", "zh", "fh"]
    vowels = [*"aeiouy", "au", "ou", "ai"]
    
    selectingVowels = random.choices([True, False], weights=[2, 1])[0]
    name = ""
    for _ in range(random.randrange(2, 5)):
        if selectingVowels:
            name += random.choice(vowels)
            selectingVowels = False
        else:
            name += random.choice(consonants)
            selectingVowels = True
    return name.capitalize()

seen_company_names = set[str]()
def generate_company() -> Company:
    while (name := f"""{generate_name()}{random.choice([" Corp", " Inc", ""])}""") in seen_company_names:
        pass
    seen_company_names.add(name)
    
    return Company(
        name=name,
        description=random.choice(["We do things", "Time to make a difference™", "Only the best for our shareholders"]),
        website=f"https://www.{name.replace(' ', '-')}.com",
        jobs=[generate_job() for _ in range(random.randrange(1, 8))],
    )

def generate_phone() -> str:
    def generate_random_digits(digits: int):
        return random.randrange(10**(digits - 1), 10**digits)
    return f"({generate_random_digits(3)}) {generate_random_digits(3)}-{generate_random_digits(4)}"

def generate_job_seeker() -> JobSeeker:
    skills = list(all_skills)
    random.shuffle(skills)
    proficiencies = [Proficiency(skill=skill, proficiency=random.choice([1,2,3])) for skill in skills[:5]]
    return JobSeeker(first_name=generate_name(), last_name=generate_name(), phone=generate_phone(), proficiencies=proficiencies)

def generate_company_account() -> Account:
    company = generate_company()
    email = f"{generate_name()}@{company.name.split()[0].lower()}.com"
    return Account(email=email, password="password", type=company)

seen_emails = set[str]()
def generate_job_seeker_account() -> Account:
    job_seeker = generate_job_seeker()
    while (email := f"{job_seeker.first_name}.{job_seeker.last_name}@gmail.com") in seen_emails:
        job_seeker = generate_job_seeker()
    seen_emails.add(email)

    return Account(email=email, password="password", type=job_seeker)

def get_skill_ids(cursor: pymysql.cursors.Cursor) -> dict[Skill, int]:
    cursor.execute("SELECT * FROM skill")
    return {name: id for id, name in cursor.fetchall()}

def add_account_to_db(account: Account, /, cursor: pymysql.cursors.Cursor):
    skills = get_skill_ids(cursor)
    cursor.execute("INSERT INTO account (email, password) VALUES (%s, %s)", (account.email, generate_password_hash(account.password)))
    account_id = cursor.lastrowid
    match account.type:
        case Company(name, description, website, jobs):
            cursor.execute("INSERT INTO company (id, name, website, description) VALUES (%s, %s, %s, %s)", (account_id, name, website, description))
            for job in jobs:
                cursor.execute("INSERT INTO job (company_id, jname, description, location, apply_deadline) VALUES (%s, %s, %s, %s, %s)", (account_id, job.name, job.description, job.location, job.deadline))
                job_id = cursor.lastrowid
                cursor.executemany("INSERT INTO job_skill_requirements VALUES (%s, %s, %s)", ((job_id, skills[requirement.skill], requirement.proficiency) for requirement in job.requirements))
        case JobSeeker(first_name, last_name, phone, proficiencies):
            cursor.execute("INSERT INTO job_seeker (id, fname, lname, phone) VALUES (%s, %s, %s, %s)", (account_id, first_name, last_name, phone))
            cursor.executemany("INSERT INTO job_seeker_skill VALUES (%s, %s, %s)", ((skills[proficiency.skill], account_id, proficiency.proficiency) for proficiency in proficiencies))

def random_row(*, trusted_table_str: str, cursor: pymysql.cursors.Cursor):
    cursor.execute(f"SELECT COUNT(*) FROM {trusted_table_str}") 
    num_rows: int = cursor.fetchone()[0]
    selection = random.randrange(num_rows)
    cursor.execute(f"SELECT * FROM {trusted_table_str} LIMIT 1 OFFSET %s", (selection,))
    return cursor.fetchone()

Application: TypeAlias = tuple[int, int]
existing_applications = set[Application]()
def create_random_job_application(cursor: pymysql.cursors.Cursor):
    def get_application() -> Application:
        return random_row(trusted_table_str="job_seeker", cursor=cursor)[0], random_row(trusted_table_str="job", cursor=cursor)[0]
    while (application := get_application()) in existing_applications:
        pass
    existing_applications.add(application)
    
    cursor.execute("INSERT INTO application (job_seeker_id, job_id) VALUES (%s, %s)", application)
