import datetime

from flask import Blueprint, request, render_template, jsonify, redirect, url_for, make_response, current_app
from flask_security.utils import get_hmac, _pwd_context
from flask_security import login_user

from functools import wraps

from .models import Users, jwt
from .utils import flask_security_datastore_commit

from http import HTTPStatus

login_blueprint = Blueprint('login_auth', __name__)
unauthorized_message = 'Could not verify'


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_token = request.cookies.get('auth_token', None)
        if auth_token is not None:
            try:
                public_id = Users.decode_auth_token(auth_token)
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                return False
            current_user = Users.query.filter_by(public_id=public_id).first()
            return f(current_user, *args, **kwargs)
        else:
            return False

    return decorated


@login_blueprint.route('/login', methods=['GET'])
def login_get():
    return render_template('login/index.html')


@login_blueprint.route('/login', methods=['POST'])
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
