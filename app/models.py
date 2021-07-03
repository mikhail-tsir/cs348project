from dataclasses import dataclass
from flask_login import UserMixin
from typing import Union

@dataclass
class JobSeeker():
    fname: str
    lname: str


@dataclass
class Company():
    name: str


class Account(UserMixin):
    def __init__(self, id: int, email: str, password: str, user: Union[JobSeeker, Company]):
        self.id = id
        self.email = email
        self.password = password
        self.user = user
        super().__init__()
