-- display jobs to the job seeker based on relevance
SELECT job.*
FROM relevance, job
WHERE relevance.job_id = job.id
  AND relevance.job_seeker_id = %s
  AND job.apply_deadline <= CURRENT_TIMESTAMP
ORDER BY relevance.score DESC;

-- display applicants to the hiring manager for a given job based on relevance
SELECT job_seeker.*
FROM relevance, job_seeker, application
WHERE relevance.job_id = %s
  AND relevance.job_seeker_id = job_seeker.id
  AND application.job_id = relevance.job_id
  AND application.job_seeker_id = job_seeker.id
ORDER BY relevance.score DESC;

-- display the possible skills
SELECT *
FROM skill;

--  job seeker adds skills with a given proficiency
INSERT INTO job_seeker_skill (skill_id, job_seeker_id, proficiency)
VALUES (%s, %s, %s);

-- apply to a job
INSERT INTO application (job_seeker_id, job_id)
VALUES (%s, %s);

-- recruiter adds a job listing
INSERT INTO job (jname, company_id, description, apply_deadline)
VALUES ($s, $s, $s, $s);
