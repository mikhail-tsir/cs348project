-- Hardcoded numeric and string values will be replaced by actual values provided by the user

-- display jobs to the job seeker based on relevance
SELECT job.*
FROM relevance, job
WHERE relevance.job_id = job.id
  AND relevance.job_seeker_id = 2   -- will be replaced by the id of current job seeker who is logged int
  AND job.apply_deadline <= CURRENT_TIMESTAMP
ORDER BY relevance.score DESC;

-- display applicants to the hiring manager for a given job based on relevance
SELECT job_seeker.*
FROM relevance, job_seeker, application
WHERE relevance.job_id = 2          -- will be replaced
  AND relevance.job_seeker_id = job_seeker.id
  AND application.job_id = relevance.job_id
  AND application.job_seeker_id = job_seeker.id
ORDER BY relevance.score DESC;

-- display the possible skills
SELECT *
FROM skill;

--  job seeker adds skills with a given proficiency
INSERT INTO job_seeker_skill (skill_id, job_seeker_id, proficiency)
VALUES (2, 1, 3); -- will be replaced

-- apply to a job
INSERT INTO application (job_seeker_id, job_id)
VALUES (1, 5); -- will be replaced

-- recruiter adds a job listing
INSERT INTO job (jname, company_id, description, apply_deadline)
VALUES ('newJob', 5, 'desc', '2021-08-30 00:00:00'); -- will be replaced

-- recruiter adds a related skill to a job
INSERT INTO job_skill_requirements
VALUES (1, 4, 3); -- will be replaced
