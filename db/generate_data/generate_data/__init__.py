from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal, TypeAlias
from functools import reduce

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
    requirements: list[SkillRequirement]


ProgrammerType: TypeAlias = Literal["frontend", "backend", "embedded", "mobile"]
programmer_types: list[ProgrammerType] = ["frontend", "backend", "embedded", "mobile"]
skills: dict[ProgrammerType, set[Skill]] = {
    "frontend": {"HTML5", "Typescript", "Bootstrap"},
    "backend": {"Python", "Java", "Kotlin", "Go", "REST", "HTTP", "SQL"},
    "embedded": {"C", "C++", "Rust"},
    "mobile": {"Kotlin", "Swift"},
}
all_skills = reduce(set[Skill].union, skills.values(), set[Skill]())

def generate_job(programmer_type: ProgrammerType) -> Job:
    relevant_skills = skills[programmer_type]
    deadline = datetime.now() + timedelta(days=random.randrange(0,10), hours=random.randrange(0, 24), minutes=random.randrange(0, 60))
    match programmer_type:
        case "frontend":
            mainSkill = random.choice(list(relevant_skills))
            otherSkill = random.choice(list(relevant_skills - {mainSkill}))
            
            return Job(
                name=random.choice([f"Frontend developer specializing in {mainSkill}", "Web dev", f"{mainSkill} dev"]),
                description=f"Looking for a frontend developer who is experienced with {mainSkill} and has familiarity with {otherSkill}",
                deadline=deadline,
                requirements=[SkillRequirement(mainSkill, proficiency=3), SkillRequirement(otherSkill, proficiency=1)]
            )
        case "backend":
            mainSkill = random.choice(list(relevant_skills))
            otherSkill = random.choice(list(relevant_skills - {mainSkill}))

            return Job(
                name=random.choice([f"Backend developer specializing in {mainSkill}", "Backend dev", f"{mainSkill} dev"]),
                description=f"Looking for a backend developer who is experienced with {mainSkill} and has familiarity with {otherSkill}",
                deadline=deadline,
                requirements=[SkillRequirement(mainSkill, proficiency=3), SkillRequirement(otherSkill, proficiency=1)]
            )
        case "embedded":
            skill = random.choice(list(relevant_skills))
            return Job(
                name=random.choice([f"Firmware developer", f"{skill} specialist"]),
                description=random.choice([f"Looking for a developer who knows their way around {skill}"]),
                deadline=deadline,
                requirements=[SkillRequirement(skill, proficiency=3)],
            )
        case "mobile":
            skill = random.choice(list(relevant_skills))
            return Job(
                name=random.choice([f"Mobile developer", f"{skill} developer"]),
                description=random.choice([f"Looking for native {skill} app developer"]),
                deadline=deadline,
                requirements=[SkillRequirement(skill, proficiency=3)],
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
        jobs=[generate_job(programmer_type=random.choice(programmer_types)) for _ in range(random.randrange(1, 8))],
    )

def generate_phone() -> str:
    def generate_random_digits(digits: int):
        return random.randrange(10**(digits - 1), 10**digits)
    return f"({generate_random_digits(3)}) {generate_random_digits(3)}-{generate_random_digits(4)}"

def generate_job_seeker() -> JobSeeker:
    skills = list(all_skills)
    random.shuffle(skills)
    proficiencies = [Proficiency(skill=skill, proficiency=random.choice([1,2,3])) for skill in skills]
    return JobSeeker(first_name=generate_name(), last_name=generate_name(), phone=generate_phone(), proficiencies=proficiencies)

def generate_company_account() -> Account:
    company = generate_company()
    email = f"{generate_name()}@{company.name.split()[0].lower()}.com"
    return Account(email=email, password="password", type=company)

seen_emails = set[str]()
def generate_job_seeker_account() -> Account:
    job_seeker = generate_job_seeker()
    while (email := f"{job_seeker.first_name}.{job_seeker.last_name}@gmail.com") not in seen_emails:
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
        case Company(name, description, jobs):
            cursor.execute("INSERT INTO company (id, name, description) VALUES (%s, %s, %s)", (account_id, name, description))
            for job in jobs:
                cursor.execute("INSERT INTO job (company_id, jname, description, apply_deadline) VALUES (%s, %s, %s, %s)", (account_id, job.name, job.description, job.deadline))
                job_id = cursor.lastrowid
                cursor.executemany("INSERT INTO job_skill_requirements VALUES (%s, %s, %s)", ((job_id, skills[requirement.skill], requirement.proficiency) for requirement in job.requirements))
        case JobSeeker(first_name, last_name, phone, proficiencies):
            cursor.execute("INSERT INTO job_seeker (id, fname, lname, phone) VALUES (%s, %s, %s, %s)", (account_id, first_name, last_name, phone))
            cursor.executemany("INSERT INTO job_seeker_skill VALUES (%s, %s, %s)", ((skills[proficiency.skill], account_id, proficiency.proficiency) for proficiency in proficiencies))


