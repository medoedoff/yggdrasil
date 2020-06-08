import datetime

from flask import Blueprint, request, render_template, jsonify, redirect, url_for, make_response
from flask_security.utils import get_hmac, _pwd_context
from flask_security import login_user

from functools import wraps

from .models import Users, jwt
from .utils import flask_security_datastore_commit

from http import HTTPStatus

auth = Blueprint('auth', __name__)
unauthorized_message = 'Could not verify'


# Token check for flask_admin
def token_required_admin_panel(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_token = request.cookies.get('auth_token', None)
        if auth_token is not None:
            try:
                token_data = Users.decode_auth_token(auth_token)
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                return False
            public_id = token_data.get('sub', None)
            blacklist = token_data.get('blacklist', None)
            if blacklist:
                return False
            current_user = Users.query.filter_by(public_id=public_id).first()
            return f(current_user, *args, **kwargs)
        else:
            return False

    return decorated


# Token check
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_token = request.cookies.get('auth_token', None)
        if auth_token is not None:
            try:
                public_id = Users.decode_auth_token(auth_token)
                public_id = public_id.get('sub', None)
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                return redirect(url_for('login_auth.login_get'))
            current_user = Users.query.filter_by(public_id=public_id).first()
            return f(current_user, *args, **kwargs)
        else:
            return redirect(url_for('login_auth.login_get'))

    return decorated


@auth.route('/', methods=['GET'])
@token_required
def root(current_user):
    if current_user:
        return redirect(url_for('admin.index'))


@auth.route('/login', methods=['GET'])
def login_get():
    return render_template('login/index.html')


@auth.route('/login', methods=['POST'])
def login_post():
    if request.method == 'POST':
        email_form = request.form['email']
        password_form = request.form['password']

        user = Users.query.filter_by(email=email_form).first()
        if not user:
            return jsonify(message=unauthorized_message), HTTPStatus.UNAUTHORIZED.value

        password_form = get_hmac(password_form)
        verify = _pwd_context.verify(password_form, user.password)

        if verify and user.active:
            # Token credentials
            exp_date = datetime.datetime.utcnow() + datetime.timedelta(days=7)
            iat = datetime.datetime.utcnow()
            auth_token = user.encode_auth_token(user.public_id, exp_date, iat)

            if auth_token:
                # Track current ip, last ip and other information for security proposes
                login_user(user)
                flask_security_datastore_commit()

                response = make_response(redirect(url_for('admin.index')))
                response.set_cookie('auth_token', auth_token, expires=exp_date)
                return response
        else:
            return jsonify(message=unauthorized_message), HTTPStatus.UNAUTHORIZED.value


@auth.route('/logout', methods=['POST'])
def logout():
    pass
