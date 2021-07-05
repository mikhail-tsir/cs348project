-- new job seeker or company account
INSERT INTO account (id, email, password)
VALUES (10000, 'ewfwf@gmail.com', 'abcde');

-- jobseeker signup
INSERT INTO job_seeker (id, fname, lname, phone)
VALUES (10000, 'Bob', 'Smith', '(874) 131-3972');

-- company signup
INSERT INTO company (id, name, description)
VALUES (10000, 'abc', 'desc')

-- create new job posting
INSERT INTO job (id, jname, company_id, description, apply_deadline)
VALUES (10000, 'newJob', 10000, 'desc', '2021-08-30 00:00:00'); 

-- create new skill category
INSERT INTO skill (id, sname)
VALUES (10000, 'javascript')

-- jobseeker applies to new job
INSERT INTO application (job_seeker_id, job_id)
VALUES (10000, 10000);

-- job seeker add to their skills
INSERT INTO job_seeker_skill (skill_id, job_seeker_id, proficiency)
VALUES (10000, 10000, 2)

-- job requirements
INSERT INTO job_skill_requirements (job_id, skill_id, min_proficiency)
VALUES (10000, 10000, 1)

-- Hardcoded numeric and string values will be replaced by actual values provided by the user

-- display jobs to the job seeker based on relevance
SELECT job.*
FROM relevance, job
WHERE relevance.job_id = job.id
  AND relevance.job_seeker_id = 10000   -- will be replaced by the id of current job seeker who is logged int
  AND job.apply_deadline <= CURRENT_TIMESTAMP
ORDER BY relevance.score DESC;

-- display applicants to the hiring manager for a given job based on relevance
SELECT job_seeker.*
FROM relevance, job_seeker, application
WHERE relevance.job_id = 10000          -- will be replaced
  AND relevance.job_seeker_id = job_seeker.id
  AND application.job_id = relevance.job_id
  AND application.job_seeker_id = job_seeker.id
ORDER BY relevance.score DESC;

-- display the possible skills
SELECT *
FROM skill;

-- display job_seeker_skill before insert
SELECT *
FROM job_seeker_skill;

-- update skill proficiency from 2 to 3
UPDATE job_seeker_skill
SET proficiency = 3
WHERE skill_id = 10000, job_seeker_id = 10000

-- display job_seeker_skill after update
SELECT *
FROM job_seeker_skill;

-- update job skill requirement's proficiency
UPDATE job_skill_requirements
SET proficiency = 3
WHERE job_id = 1, skill_id = 4

-- display job_skill_requirements after update
SELECT *
FROM job_skill_requirements;
