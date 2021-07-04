from flask import Blueprint

from app.decorators import company_login_required

company = Blueprint("company", __name__)


@company.route("/homepage")
@company_login_required
def homepage():
    return "Temporary homepage for company"
