CREATE TABLE account (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  email TEXT NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE company (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  company_name TEXT NOT NULL,
  description TEXT,
  account_id INT NOT NULL,
  FOREIGN KEY (account_id) REFERENCES account(id)
);

CREATE TABLE job_seeker (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  fname TEXT NOT NULL,
  lname TEXT NOT NULL,
  account_id INT NOT NULL,
  cv BLOB,
  phone TEXT,
  FOREIGN KEY (account_id) REFERENCES account(id)
);

CREATE TABLE job (
  id INT NOT NULL PRIMARY KEY,
  jname TEXT NOT NULL,
  company_id INT NOT NULL,
  description TEXT NOT NULL,
  apply_deadline TIMESTAMP NOT NULL,
  FOREIGN KEY (company_id) REFERENCES company(id)
);

CREATE TABLE skill (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  sname TEXT NOT NULL
);

CREATE TABLE application (
  job_seeker_id INT NOT NULL,
  job_id INT NOT NULL,
  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(job_seeker_id, job_id),
  FOREIGN KEY (job_seeker_id) REFERENCES job_seeker(id),
  FOREIGN KEY (job_id) REFERENCES job(id)
);

CREATE TABLE job_seeker_skill (
  skill_id INT NOT NULL,
  job_seeker_id INT NOT NULL,
  proficiency INT NOT NULL,
  PRIMARY KEY(skill_id, job_seeker_id),
  FOREIGN KEY (job_seeker_id) REFERENCES job_seeker(id),
  FOREIGN KEY (skill_id) REFERENCES skill(id),
  CONSTRAINT proficiency_check CHECK (
    proficiency > 0
    AND proficiency <= 3
  )
);

CREATE TABLE job_skill_requirements (
  job_id INT NOT NULL,
  skill_id INT NOT NULL,
  min_proficiency INT NOT NULL,
  PRIMARY KEY(skill_id, job_id),
  FOREIGN KEY (skill_id) REFERENCES skill(id),
  FOREIGN KEY (job_id) REFERENCES job(id),
  CONSTRAINT min_proficiency_constraint CHECK (
    min_proficiency > 0
    AND min_proficiency <= 3
  )
);

CREATE VIEW relevance AS
SELECT SUM(seeker.proficiency * reqs.min_proficiency) AS score, reqs.job_id,  seeker.job_seeker_id
FROM job_skill_requirements AS reqs, job_seeker_skill AS seeker
WHERE reqs.skill_id = seeker.skill_id
GROUP BY reqs.job_id,  seeker.job_seeker_id;


-- constraints to ensure that no account belongs to
-- a company AND a job seeker
ALTER TABLE
  company
ADD
  CONSTRAINT company_account_id_check CHECK (
    account_id NOT IN (
      SELECT
        account_id
      FROM
        job_seeker
    )
  );

ALTER TABLE
  job_seeker
ADD
  CONSTRAINT job_seeker_account_id_check CHECK (
    account_id NOT IN (
      SELECT
        account_id
      FROM
        company
    )
  );
