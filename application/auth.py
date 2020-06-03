from flask import Blueprint, request, render_template, jsonify, redirect, url_for, make_response
from flask_security import Security
from flask_security.utils import get_hmac, _pwd_context

from functools import wraps

from .models import Users, jwt

from http import HTTPStatus

login_blueprint = Blueprint('login_auth', __name__)

security = Security()

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


@login_blueprint.route('/', methods=['GET'])
def login_get():
    return render_template('login/index.html')


@login_blueprint.route('/', methods=['POST'])
def login_post():
    if request.method == 'POST':
        email_form = request.form['email']
        password_form = request.form['password']

        user = Users.query.filter_by(email=email_form).first()
        if not user:
            return jsonify(message=unauthorized_message), HTTPStatus.UNAUTHORIZED.value

        password_form = get_hmac(password_form)
        verify = _pwd_context.verify(password_form, user.password)

        if verify:
            auth_token = user.encode_auth_token(user.public_id)
            if auth_token:
                response = make_response(redirect(url_for('admin.index')))
                response.set_cookie('auth_token', auth_token)
                return response
        else:
            return jsonify(message=unauthorized_message), HTTPStatus.UNAUTHORIZED.value
