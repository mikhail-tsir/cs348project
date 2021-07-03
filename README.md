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

    The docker compose file spins up the web server and the mysql database, in two separate docker containers. The mysql container automatically runs `db/init.sql` to create the table(s).

    In order to generate a test dataset, run
    ```bash
        docker-compose run generate_data
    ```

3. Navigate to `http://localhost:5000`
