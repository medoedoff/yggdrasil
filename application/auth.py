from flask import Blueprint, request, render_template, redirect, url_for
from flask_security.utils import get_hmac, _pwd_context
from flask_security import login_user, logout_user, current_user

from functools import wraps

from .models import Users, jwt
from .utils import flask_security_datastore_commit

auth = Blueprint('auth', __name__)


# Token check
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_token = request.cookies.get('auth_token', None)
        user = None
        if auth_token is not None:
            try:
                token_data = Users.decode_auth_token(auth_token)
                public_id = token_data.get('sub', None)
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                return f(user, *args, **kwargs)
            blacklist = token_data.get('blacklist', False)
            if blacklist:
                return f(user, *args, **kwargs)
            user = Users.query.filter_by(public_id=public_id).first()
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
            return render_template('login/index.html', error=error)

        password_form = get_hmac(password_form)
        verify = _pwd_context.verify(password_form, user.password)

        if verify and user.active:
            # Track current ip, last ip and other information for security proposes
            login_user(user)
            flask_security_datastore_commit()
            return redirect(url_for('admin.index'))
        else:
            return render_template('login/index.html', error=error)

    return render_template('login/index.html')


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
