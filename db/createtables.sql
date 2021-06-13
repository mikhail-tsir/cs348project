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
  FOREIGN KEY account_id REFERENCES account(id)
);

CREATE TABLE job_seeker (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  fname TEXT NOT NULL,
  lname TEXT NOT NULL,
  account_id INT NOT NULL,
  cv BLOB,
  phone TEXT,
  FOREIGN KEY account_id REFERENCES account(id)
);

CREATE TABLE job (
  id INT NOT NULL PRIMARY KEY,
  jname TEXT NOT NULL,
  company_id INT NOT NULL,
  description TEXT NOT NULL,
  apply_deadline TIMESTAMP NOT NULL,
  FOREIGN KEY company_id REFERENCES company(id)
);

CREATE TABLE skill (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  sname TEXT NOT NULL,
  proficiency INT NOT NULL,
  CONSTRAINT proficiency_check CHECK (
    proficiency > 0
    AND proficiency <= 3
  )
);

CREATE TABLE application (
  job_seeker_id INT NOT NULL,
  job_id INT NOT NULL,
  APPLIED_AT TIMESTAMP NOT NULL CURRENT_TIMESTAMP,
  PRIMARY KEY(skill_id, job_id),
  FOREIGN KEY job_seeker_id REFERENCES job_seeker(id),
  FOREIGN KEY job_id REFERENCES job(id)
);

CREATE TABLE job_seeker_skill (
  skill_id INT NOT NULL,
  job_seeker_id INT NOT NULL,
  PRIMARY KEY(skill_id, job_seeker_id),
  FOREIGN KEY(job_seeker_id) REFERENCES job_seeker(id),
  FOREIGN KEY(skill_id) REFERENCES skill(id)
);

CREATE TABLE job_skill_requirements (
  job_id INT NOT NULL,
  skill_id INT NOT NULL,
  min_proficiency INT NOT NULL,
  PRIMARY KEY(skill_id, job_id),
  FOREIGN KEY(skill_id) REFERENCES skill(id),
  FOREIGN KEY(job_id) REFERENCES job(id),
  CONSTRAINT min_proficiency_constraint CHECK (
    min_proficiency > 0
    AND min_proficiency <= 3
  )
);

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
