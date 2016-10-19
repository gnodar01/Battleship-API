import endpoints
from re import match

from models.ndbModels import User


def check_email(email):
    email_format_match = match(
        r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)',
        email)
    if not email_format_match:
        raise endpoints.ConflictException('E-mail is not valid')


def check_username_len(username):
    if len(username) < 3:
        raise endpoints.ConflictException(
            'Username must be at least 3 characters')


def check_user_exists(username):
    if User.query(User.name == username).get():
        raise endpoints.ConflictException(
            'A User with that name already exists')


def check_email_exists(email):
    if User.query(User.email == email).get():
        raise endpoints.ConflictException(
            'A User with that E-Mail already exists')
