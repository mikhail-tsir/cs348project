CREATE TABLE account (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL,
  CONSTRAINT email_unique UNIQUE (email)
);

CREATE TABLE company (
  id INT NOT NULL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  FOREIGN KEY (id) REFERENCES account(id),
  CONSTRAINT name_unique UNIQUE (name)
);

CREATE TABLE job_seeker (
  id INT NOT NULL PRIMARY KEY,
  fname VARCHAR(255) NOT NULL,
  lname VARCHAR(255) NOT NULL,
  cv BLOB,
  phone VARCHAR(255),
  FOREIGN KEY (id) REFERENCES account(id)
);

CREATE TABLE job (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  jname VARCHAR(255) NOT NULL,
  company_id INT NOT NULL,
  description TEXT NOT NULL,
  apply_deadline TIMESTAMP NOT NULL,
  FOREIGN KEY (company_id) REFERENCES company(id)
);

CREATE TABLE skill (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  sname VARCHAR(255) NOT NULL,
  CONSTRAINT name_unique UNIQUE (sname)
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


-- procedure to be called by trigger to check for company id integrity
DELIMITER //
CREATE PROCEDURE company_id_check_proc(IN id INT)
READS SQL DATA
BEGIN

  IF id IN
    (SELECT job_seeker.id
    FROM job_seeker)
  THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Company account already belongs to job seeker';
  END IF;

END
//

-- triggers to check for job_seeker id integrity

-- before insert
CREATE TRIGGER company_id_check_insert
BEFORE INSERT
ON company FOR EACH ROW

BEGIN
  CALL company_id_check_proc(NEW.id);
END
//

-- before update
CREATE TRIGGER company_id_check_update
BEFORE UPDATE
ON company FOR EACH ROW

BEGIN
  CALL company_id_check_proc(NEW.id);
END
//

-- procedure to be called by trigger to check for job_seeker id integrity
CREATE PROCEDURE job_seeker_id_check_proc(IN id INT)
READS SQL DATA
BEGIN

  IF id IN
    (SELECT company.id
    FROM company)
  THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Job seeker account already belongs to company';
  END IF;

END
//

-- triggers to check for job_seeker id integrity

-- before insert
CREATE TRIGGER job_seeker_id_check_insert
BEFORE INSERT
ON job_seeker FOR EACH ROW

BEGIN
  CALL job_seeker_id_check_proc(NEW.id);
END
//

-- before update
CREATE TRIGGER job_seeker_id_check_update
BEFORE UPDATE
ON job_seeker FOR EACH ROW

BEGIN
  CALL job_seeker_id_check_proc(NEW.id);
END
//

DELIMITER ;

-- views

-- relevance view

CREATE VIEW relevance AS
  SELECT
    SUM(seeker.proficiency * reqs.min_proficiency) AS score,
    reqs.job_id,
    seeker.job_seeker_id
  FROM job_skill_requirements AS reqs
  INNER JOIN job_seeker_skill AS seeker
  ON reqs.skill_id = seeker.skill_id
  GROUP BY reqs.job_id, seeker.job_seeker_id;

-- companies view

CREATE VIEW company_account AS
  SELECT *
  FROM company
  NATURAL JOIN account;

-- jobseekers view

CREATE VIEW job_seeker_account AS
  SELECT *
  FROM job_seeker
  NATURAL JOIN account;

-- indexes

CREATE INDEX email_idx ON account (email);

CREATE INDEX email_password_idx ON account (email, password);
