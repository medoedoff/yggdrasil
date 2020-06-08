from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView
from flask_admin.menu import MenuLink
from flask_security.utils import hash_password
from flask_security import current_user
from wtforms import PasswordField, ValidationError
from flask import redirect, url_for

from .auth import token_required_admin_panel
from .utils import password_validation, email_validation

admin = Admin(name='GIB-Teldrassil')


class MyAdminIndexViewSet(AdminIndexView):
    @token_required_admin_panel
    def is_accessible(self, *args, **kwargs):
        if current_user.is_authenticated and current_user.is_active:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login_get'))


class MyModelViewSet(ModelView):
    @token_required_admin_panel
    def is_accessible(self, *args, **kwargs):
        if current_user.is_authenticated and current_user.is_active:
            if 'admin' in current_user.roles or current_user.super_user:
                return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login_get'))


class MyLogoutMenuLink(MenuLink):
    @token_required_admin_panel
    def is_accessible(self, *args, **kwargs):
        return current_user.is_authenticated


class UserModelViewSet(MyModelViewSet):
    column_exclude_list = ('password', 'public_id')
    form_columns = ('email', 'Password', 'Confirm password', 'first_name', 'last_name', 'roles', 'active')
    form_extra_fields = {
        'Password': PasswordField('Password'),
        'Confirm password': PasswordField('Confirm password')
    }
    form_excluded_columns = ('created', 'updated', 'last_login_at', 'current_login_at',
                             'last_login_ip', 'current_login_ip', 'login_count', 'password')

    def on_model_change(self, form, model, is_created=True):
        creation_mode = all([model.email, form.data.get('Password', None)])
        if creation_mode:
            password = form.data.get('Password', None)
            confirm_password = form.data.get('Confirm password', None)
            pwd_validation = password_validation(password)
            e_validation = email_validation(model.email)
            if not e_validation:
                raise ValidationError('Invalid email')
            if password != confirm_password:
                raise ValidationError('Passwords are not equal')
            if not pwd_validation:
                raise ValidationError('Passwords is too weak')
            model.password = hash_password(password)


class RoleModelViewSet(MyModelViewSet):
    pass
