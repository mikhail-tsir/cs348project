from re import L
from flask import Flask
from flaskext.mysql import MySQL
from flask_login import LoginManager

db = MySQL()


def create_app():
    app = Flask(__name__)
    app.config["MYSQL_DATABASE_USER"] = "root"
    app.config["MYSQL_DATABASE_PASSWORD"] = "root"
    app.config["MYSQL_DATABASE_DB"] = "test_db"
    app.config["MYSQL_DATABASE_HOST"] = "db"

    app.config[
        "SECRET_KEY"
    ] = "ShVmYq3t6w9y$B&E)H@McQfTjWnZr4u7x!A%C*F-JaNdRgUkXp2s5v8y/B?E(G+KbPeShVmYq3t6w9z$C&F)J@McQfTjWnZr4u7x!A%D*G-KaPdRgUkXp2s5v8y/B?E("

    db.init_app(app)

    # blueprint for auth routes
    # import here to avoid circular imports (I think)
    from app.auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    # blueprint for all other parts of app
    from app.main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from app.models.job_seeker import JobSeeker

    @login_manager.user_loader
    def load_user(user_id):
        with db.connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM job_seeker_account WHERE id = %s;", int(user_id)
            )
            result = cursor.fetchone()
            return JobSeeker(*result) if result else None

    return app
