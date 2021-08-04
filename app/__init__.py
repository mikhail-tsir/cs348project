from re import L
from flask import Flask
from flaskext.mysql import MySQL
from flask_login import LoginManager

import logging

db = MySQL()


def create_app():
    app = Flask(__name__)

    logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

    app.config["MYSQL_DATABASE_USER"] = "root"
    app.config["MYSQL_DATABASE_PASSWORD"] = "root"
    app.config["MYSQL_DATABASE_DB"] = "test_db"
    app.config["MYSQL_DATABASE_HOST"] = "db"

    app.config[
        "SECRET_KEY"
    ] = "ShVmYq3t6w9y$B&E)H@McQfTjWnZr4u7x!A%C*F-JaNdRgUkXp2s5v8y/B?E(G+KbPeShVmYq3t6w9z$C&F)J@McQfTjWnZr4u7x!A%D*G-KaPdRgUkXp2s5v8y/B?E("

    db.init_app(app)

    # import here to avoid circular imports (I think)
    from app.index import base
    from app.auth.company_auth import company_auth
    from app.auth.jobseeker_auth import jobseeker_auth
    from app.roles.jobseeker import jobseeker
    from app.roles.company import company

    app.register_blueprint(base)
    app.register_blueprint(company_auth, url_prefix="/company")
    app.register_blueprint(jobseeker_auth, url_prefix="/jobseeker")
    app.register_blueprint(company, url_prefix="/company")
    app.register_blueprint(jobseeker, url_prefix="/jobseeker")

    login_manager = LoginManager()
    login_manager.blueprint_login_views = {
        "jobseeker": "jobseeker_auth.login",
        "company": "company_auth.login",
    }

    login_manager.init_app(app)

    from app.models import Account, JobSeeker, Company

    @login_manager.user_loader
    def load_user(user_id):
        with db.connect() as conn, conn.cursor() as cursor:
            # if account belongs to user
            cursor.execute(
                "SELECT * FROM job_seeker_account WHERE id = %s;", int(user_id)
            )
            result = cursor.fetchone()
            if result:
                (id, fname, lname, email, password) = result
                return Account(id, email, password, JobSeeker(fname, lname))
            
            # if account belongs to company
            cursor.execute(
                "SELECT * FROM company_account WHERE id = %s", int(user_id)
            )
            result = cursor.fetchone()
            if result:
                (id, name, email, password) = result
                return Account(id, email, password, Company(name))
            
            # if id invalid
            return None

    return app
