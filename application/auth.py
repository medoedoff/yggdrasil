from flask import Blueprint, request, render_template, jsonify, redirect, url_for
from flask_security import Security
from flask_security.utils import get_hmac, _pwd_context

from .models import Users

from http import HTTPStatus

login_blueprint = Blueprint('login_auth', __name__)

security = Security()

unauthorized_message = 'Could not verify'


@login_blueprint.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_form = request.form['email']
        password_form = request.form['password']

        user = Users.query.filter_by(email=email_form).first()
        if not user:
            return jsonify(message=unauthorized_message), HTTPStatus.UNAUTHORIZED.value

        password_form = get_hmac(password_form)
        verify = _pwd_context.verify(password_form, user.password)

        if verify:
            return redirect(url_for('admin'))
        else:
            return jsonify(message=unauthorized_message), HTTPStatus.UNAUTHORIZED.value

    return render_template('login.html')
