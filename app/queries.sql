CREATE VIEW relevance AS
SELECT SUM(seeker.proficiency * reqs.min_proficiency) AS score, reqs.job_id AS job_id,  seeker.job_seeker_id AS job_seeker_id
        FROM job_skill_requirements AS reqs, job_sekeer_skill AS seeker
        WHERE reqs.skill_id = seeker.skill_id;

-- display jobs to the job seeker based on relevance
SELECT job, skill
FROM relevance, job, skill
WHERE relevance.job_id = job.id
  AND relevance.job_seeker_id = %s
ORDER BY relevance.score DESC;

-- apply to a job
INSERT INTO application
VALUES (%s, %s);

