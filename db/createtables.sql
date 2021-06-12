CREATE TABLE Account
  ( 
     id     DECIMAL(9, 0) NOT NULL PRIMARY KEY, 
     email    VARCHAR(30) NOT NULL, 
     account_password	VARCHAR(25) NOT NULL
  ); 

CREATE TABLE Company 
  (  
	 id DECIMAL(9, 0) NOT NULL,
	 PRIMARY KEY(id), 
	 FOREIGN KEY(id) REFERENCES Account(id),
     company_name   VARCHAR(30) NOT NULL
  ); 

CREATE TABLE Job_seeker 
  (  
	 id DECIMAL(9, 0) NOT NULL,
	 PRIMARY KEY(id), 
	 FOREIGN KEY(id) REFERENCES Account(id),
     name   VARCHAR(30) NOT NULL
  ); 
  
CREATE TABLE Job 
  ( 	
	 job_id     VARCHAR(40) NOT NULL PRIMARY KEY, 
     jname		VARCHAR(20) NOT NULL, 
     company_id DECIMAL(9, 0) NOT NULL,
     description     VARCHAR(10), 
     apply_deadline      VARCHAR(20), 
     FOREIGN KEY(company_id) REFERENCES Company(company_id) 
  ); 

CREATE TABLE Skill 
  ( 	
	 skill_id     VARCHAR(40) NOT NULL PRIMARY KEY, 
     sname		VARCHAR(20) NOT NULL
  ); 

CREATE TABLE Application 
  ( 
     skill_id  DECIMAL(9, 0) NOT NULL, 
     job_id  DECIMAL(9, 0) NOT NULL, 
     PRIMARY KEY(skill_id, job_id), 
     FOREIGN KEY(skill_id) REFERENCES Job_seeker(id), 
     FOREIGN KEY(job_id) REFERENCES Job(job_id) 
  ); 

CREATE TABLE Job_seeker_skill 
  ( 
     skill_id  DECIMAL(9, 0) NOT NULL, 
     job_seeker_id  DECIMAL(9, 0) NOT NULL, 
     PRIMARY KEY(skill_id, job_seeker_id), 
     FOREIGN KEY(job_seeker_id) REFERENCES Job_seeker(id), 
     FOREIGN KEY(skill_id) REFERENCES Skill(skill_id) 
  ); 
  
  CREATE TABLE Job_skill_requirements
  ( 
     skill_id  DECIMAL(9, 0) NOT NULL, 
     job_id  DECIMAL(9, 0) NOT NULL, 
     PRIMARY KEY(skill_id, job_id), 
     FOREIGN KEY(skill_id) REFERENCES Skill(id), 
     FOREIGN KEY(job_id) REFERENCES Job(job_id)
  ); 
  
