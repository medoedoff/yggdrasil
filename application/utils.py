import re
import datetime
from random import sample

from flask import current_app
from werkzeug.local import LocalProxy

security = LocalProxy(lambda: current_app.extensions['security'])
datastore = LocalProxy(lambda: security.datastore)
db = LocalProxy(lambda: current_app.extensions['sqlalchemy'].db)


def flask_security_datastore_commit():
    return datastore.commit()


def gen_public_id(length=16):
    characters_and_digits = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
    public_id = ''.join(sample(characters_and_digits, length))
    return public_id


def password_validation(password):
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,128}$"

    # compiling regex
    pat = re.compile(reg)

    # searching regex
    mat = re.search(pat, password)

    return mat


def email_validation(email):
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    mat = EMAIL_REGEX.match(email)
    return mat


def gen_token_payload(email, token_id=None, days_lifetime=1):
    """
    Generates token payload
    :param email: str user's email
    :param days_lifetime: bool or int token life time value (days)
    :param token_id: str token id
    :return: dict payload
    """
    exp_date = datetime.datetime.utcnow() + datetime.timedelta(days=days_lifetime)
    iat = datetime.datetime.utcnow()

    if days_lifetime:
        payload = {
            'exp': exp_date,
            'iat': iat,
            'sub': email,
            'token_id': token_id or gen_public_id()
        }
    else:
        payload = {
            'sub': email,
            'token_id': token_id or gen_public_id()
        }
    return payload
