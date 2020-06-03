import datetime
import random
import jwt
from os import getenv
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin

db = SQLAlchemy()


class BaseModel(db.Model):
    # This is an abstract model, i.e no Table
    __abstract__ = True

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)


users_roles = db.Table('users_roles',
                       db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                       db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
                       )


class Roles(BaseModel, RoleMixin):
    # Primary key
    id = db.Column(db.Integer(), primary_key=True)

    # Details
    name = db.Column(db.String(80), unique=True, index=True)
    description = db.Column(db.String(255))

    # __str__ is required by Flask-Admin, so we can have human-readable values for the Role when editing a User.
    def __str__(self):
        return self.name

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f'role: {self.name}'


class Users(BaseModel, UserMixin):
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Public key
    public_id = db.Column(db.String(50), unique=True)

    # Info
    first_name = db.Column(db.String(length=128))
    last_name = db.Column(db.String(length=128))

    # Credentials
    email = db.Column(db.String(length=128), unique=True, index=True)
    password = db.Column(db.String(255))

    # User status
    active = db.Column(db.Boolean(), default=False)
    super_user = db.Column(db.Boolean(), default=False)

    roles = db.relationship('Roles', secondary=users_roles, backref=db.backref('users', lazy='dynamic'))

    @staticmethod
    def encode_auth_token(public_id):
        """
            Generates the Auth Token
            :return: string
        """
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
            'iat': datetime.datetime.utcnow(),
            'sub': public_id
        }
        return jwt.encode(
            payload,
            getenv('SECRET_KEY'),
            algorithm='HS256'
        )

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """

        payload = jwt.decode(auth_token, getenv('SECRET_KEY'))
        return payload['sub']

    @staticmethod
    def gen_public_id(length=16):
        characters_and_digits = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
        public_id = ''.join(random.sample(characters_and_digits, length))
        return public_id

    def __repr__(self):
        return f'email: {self.email}'
