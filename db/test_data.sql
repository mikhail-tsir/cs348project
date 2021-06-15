INSERT INTO account (email, password)
VALUES 
('johnsmith@gmail.com', 'password'),
('bob123@gmail.com', 'password'),
('emily34432@hotmail.com', 'password'),
('user1234@yahoo.com', 'password'),
('companyA@companyA.com', 'password'),
('companyB@companyB.com', 'password'),
('companyC@companyC.com', 'password');

INSERT INTO company (name, description, id)
VALUES
('companyA', 'Laptop maker', 5),
('companyB', 'Cybersecurity', 6),
('companyC', 'Software company', 7);

INSERT INTO job_seeker (fname, lname, cv, phone, id)
VALUES
('John', 'Smith', null, '111-1111', 1),
('Bob', 'Smith', null, '222-2222', 2),
('Emily', 'Em', null, '333-3333', 3),
('Mario', 'Bro', null, '444-4444', 4);

INSERT INTO job (jname, company_id, description, apply_deadline)
VALUES
('Software Developer', 5, 'desc', '2021-02-04 00:00:00'),
('Hardware Developer', 6, 'desc', '2021-05-13 00:00:00'),
('Software Tester', 5, 'desc', '2021-09-11 00:00:00'),
('Fullstack Developer', 7, 'desc', '2021-06-29 00:00:00'),
('Data Science', 7, 'desc', '2021-04-29 00:00:00');

INSERT INTO skill (sname)
VALUES
('C++'),
('Python'),
('Java'),
('HTML/CSS'),
('Javascript');

INSERT INTO application
VALUES
(1, 1, '2021-05-30 00:00:00'),
(1, 2, '2021-05-20 00:00:00'),
(2, 2, '2021-04-30 00:00:00'),
(3, 2, '2021-04-30 00:00:00'),
(3, 3, '2021-05-10 00:00:00'),
(3, 5, '2021-05-23 00:00:00'),
(4, 4, '2021-05-25 00:00:00'),
(4, 5, '2021-05-26 00:00:00');

INSERT INTO job_seeker_skill
VALUES
(1,1,1),
(4,1,2),
(2,2,1),
(3,4,3),
(5,4,3),
(1,3,2);

INSERT INTO job_skill_requirements
VALUES
(1,1,1),
(1,2,1),
(2,1,2),
(2,2,2),
(3,4,3),
(3,5,1),
(4,3,3),
(5,3,2);