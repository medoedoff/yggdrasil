from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_security.utils import get_hmac, _pwd_context
from flask_security import login_user, logout_user, current_user

from functools import wraps
from datetime import datetime

from .models import Users, BlacklistedTokens, Tokens, jwt
from .utils import flask_security_datastore_commit, db

auth = Blueprint('auth', __name__)


# Token check
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_token = request.headers.get('Authorization', None)
        user = None
        if auth_token is not None:
            try:
                token_data = Users.decode_auth_token(auth_token)
                email = token_data.get('sub', None)
                token_id = token_data.get('token_id', None)
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                return f(user, *args, **kwargs)
            if token_id is not None:
                is_token_blacklisted = BlacklistedTokens.query.filter_by(token_id=token_id).first()
                if is_token_blacklisted:
                    return f(user, *args, **kwargs)
                else:
                    current_token = Tokens.query.filter_by(token_id=token_id).first()
                    current_token.authorized_at = datetime.utcnow().replace(second=0, microsecond=0)
                    db.session.add(current_token)
                    db.session.commit()
                    user = Users.query.filter_by(email=email).first()
                    return f(user, *args, **kwargs)
        else:
            return f(user, *args, **kwargs)

    return decorated


@auth.route('/', methods=['GET'])
def root():
    if current_user:
        return redirect(url_for('admin.index'))
    else:
        return redirect(url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.is_active:
        return redirect(url_for('admin.index'))
    if request.method == 'POST':
        error = 'Invalid email or password!'
        email_form = request.form['email']
        password_form = request.form['password']

        user = Users.query.filter_by(email=email_form).first()
        if not user:
            flash(f'{error}', 'error')
            return redirect(url_for('auth.login'))

        password_form = get_hmac(password_form)
        verify = _pwd_context.verify(password_form, user.password)

        if verify and user.active:
            # Track current ip, last ip and other information for security proposes
            login_user(user)
            flask_security_datastore_commit()
            return redirect(url_for('admin.index'))
        else:
            flash(f'{error}', 'error')
            return redirect(url_for('auth.login'))

    return render_template('login/index.html')


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
