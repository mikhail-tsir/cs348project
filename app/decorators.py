from flask import current_app
from flask_login import login_required, current_user
from functools import wraps
from app.models import JobSeeker, Company

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
