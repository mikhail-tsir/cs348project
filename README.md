# CS 348 Project

## Dev setup:

1. Clone this repo:
```bash
git clone git@github.com:mikhail-tsir/cs348project.git
```
2. Install python 3.x (3.8.5 if you want to match the docker image) [https://docs.python-guide.org/starting/installation/#python-3-installation-guides](https://docs.python-guide.org/starting/installation/#python-3-installation-guides)
3. Set up a virtual environment (you don't have to since you will likely be running in docker anyway, but it might be good to have a local copy of the environment to make your editor happy).
    ```bash
        python3 -m venv env
        source env/bin/activate
    ```

    To deactivate the virtual environment, run `deactivate`. To activate again, run `source env/bin/activate`.

4. Follow the instructions below to run and test the app.

## Running the app
1. Make sure you have Docker installed. If you're on Mac or Windows, install Docker desktop: [https://docs.docker.com/desktop/](https://docs.docker.com/desktop/). 
    If you're on Linux, install the Docker Engine: [https://docs.docker.com/engine/install/ubuntu/](https://docs.docker.com/engine/install/ubuntu/) and Docker Compose [https://docs.docker.com/compose/install/#install-compose-on-linux-systems](https://docs.docker.com/compose/install/#install-compose-on-linux-systems).
    
2. Run
    ```bash
        docker-compose up
    ```

    The docker compose file spins up the web server and the mysql database, in two separate docker containers. The mysql container automatically runs `db/createtables.sql` to create the table(s).

    In order to generate a test dataset, run
    ```bash
        docker-compose run --rm generate_data
    ```
    first.

3. Navigate to `http://localhost:5000`

## Features
* Jobseekers can log in and sign up. Try navigating the application and signing up then logging in as a job seeker!
* Companies can log in and sign up. Try navigating the application and signing up then logging in as a company! All authentication features for jobseekers is implemented in `app/auth/jobseeker_auth.py` and for companies in `app/auth/jobseeker_auth.py`. The actual functionality is in `app/util/auth_util.py`, however.
* Job seekers can view the (top 10) jobs most relevant to them.
  * If you sign up as a new user and log in as the new user, you will not be able to see postings, because the new user doesn't have any skills. The functionality to add/modify skills is not implemented yet, so you can't really appreciate this feature. To get around this, you can log in as an existing user: Try the email `Avi.Cha@gmail.com` (case sensitive) with the password `"password"`. This use should already have some pre-set skills.
  * This feature is implemented in `app/roles/jobseeker.py`
 
 There are more features that were added since milestone 2, see report and video demo for details.

#### Extra (bonus) features
* Security: passwords are hashed and salted (see `app/util/auth_util.py`).
* Authorization: Users logged in as a company cannot access jobseeker pages and users logged in as a job seeker cannot access company pages.
  * This feature is implemented in `app/decorators.py`
* A very nice UI.
* Arguably log in and sign up are 2 different features (they require completely different SQL queries) so we really have 4 core features in addition to these bonus ones :)
* Multi-user access control (see report and video demo for details)
* Security features (see report and video demo for details)
