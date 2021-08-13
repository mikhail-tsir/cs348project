from flask import current_app
from flask_login import login_required, current_user
from functools import wraps
from app.models import JobSeeker, Company
from app import db

def jobseeker_login_required(func):
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if type(current_user.user) == Company:
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    
    return wrapper


def company_login_required(func):
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if type(current_user.user) == JobSeeker:
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    
    return wrapper


def authorize_company(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with db.connect() as conn, conn.cursor() as cursor:
            arg = args[0] if len(args) > 0 else kwargs["job_id"]
            cursor.execute(
                "SELECT company_id FROM job WHERE id = %s;", arg
            )

            result = cursor.fetchone()
            if len(result) == 0 or result[0] != current_user.id:
                return current_app.login_manager.unauthorized()
            return func(*args, **kwargs)
    
    return wrapper
