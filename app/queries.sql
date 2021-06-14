-- display jobs to the job seeker based on relevance
SELECT job.*, skill.*
FROM relevance, job, skill
WHERE relevance.job_id = job.id
  AND relevance.job_seeker_id = %s
ORDER BY relevance.score DESC;

-- apply to a job
INSERT INTO application
VALUES (%s, %s);

