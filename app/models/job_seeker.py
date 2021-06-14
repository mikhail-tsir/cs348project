from flask_login import UserMixin

# TODO: make separate jobseeker and company classes having account
class JobSeeker(UserMixin):
    def __init__(self, id, account_id, email, password, fname, lname):
        self.id = id
        self.account_id = account_id
        self.email = email
        self.password = password
        self.fname = fname
        self.lname = lname
        super().__init__()
