import datetime
import jwt
from os import getenv
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from .utils import gen_public_id

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

    # Info
    first_name = db.Column(db.String(length=128))
    last_name = db.Column(db.String(length=128))

    # Credentials
    email = db.Column(db.String(length=128), unique=True, index=True)
    password = db.Column(db.String(255))

    # User status
    active = db.Column(db.Boolean(), default=False, nullable=False)
    super_user = db.Column(db.Boolean(), default=False)

    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer)

    roles = db.relationship('Roles', secondary=users_roles, backref=db.backref('users', lazy='dynamic'))

    @staticmethod
    def encode_auth_token(payload):
        """
            Generates the Auth Token
            :param payload: dict token payload
        """
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
        return payload

    def __repr__(self):
        return f'email: {self.email}'


class Tokens(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    token_id = db.Column(db.String(32), unique=True, index=True, nullable=False, default=gen_public_id())
    name = db.Column(db.String(length=128))
    description = db.Column(db.Text())
    authorized_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    users = db.relationship('Users', backref=db.backref('tokens', lazy='dynamic'))

    def __repr__(self):
        return f'name: {self.name}'


class BlacklistedTokens(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    token_id = db.Column(db.String(32), unique=True, index=True)

    def __repr__(self):
        return f'token_id: {self.token_id}'
