import re
import datetime
from random import sample

from flask import current_app
from werkzeug.local import LocalProxy

security = LocalProxy(lambda: current_app.extensions['security'])
datastore = LocalProxy(lambda: security.datastore)


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


def gen_token_payload(public_id, blacklist=False):
    exp_date = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    iat = datetime.datetime.utcnow()

    payload = {
        'exp': exp_date,
        'iat': iat,
        'sub': public_id,
        'blacklist': blacklist
    }
    return payload
