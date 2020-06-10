from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.menu import MenuLink
from flask_security.utils import hash_password
from flask_security import current_user
from flask_jwt_extended import JWTManager
from wtforms import PasswordField, ValidationError
from flask import redirect, url_for

from .utils import password_validation, email_validation
from .models import Tokens

admin = Admin(name='GIB-Teldrassil', template_mode='bootstrap3')
jwt = JWTManager()


class MyAdminIndexViewSet(AdminIndexView):
    def is_accessible(self, *args, **kwargs):
        if current_user.is_authenticated and current_user.is_active:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))

    @expose('/')
    def index(self):
        tokens = Tokens.query.filter_by(user_id=current_user.id).all()
        response_data = {
            'full_name': f'{current_user.first_name} {current_user.last_name}',
            'auth_tokens': {
            }
        }
        for i in range(len(tokens)):
            response_data['auth_tokens'][i] = [tokens[i].name, tokens[i].description, tokens[i].authorized_at]

        return self.render('admin/index.html', data=response_data)


class MyModelViewSet(ModelView):
    def is_accessible(self, *args, **kwargs):
        if current_user.is_authenticated and current_user.is_active and current_user.has_role('admin'):
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))


class MyLogoutMenuLink(MenuLink):
    def is_accessible(self, *args, **kwargs):
        return current_user.is_authenticated


class UserModelViewSet(MyModelViewSet):
    column_exclude_list = 'password'
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


class BlacklistedModelViewSet(MyModelViewSet):
    column_exclude_list = ('created', 'updated')
    form_excluded_columns = ('created', 'updated')


class TokensModelViewSet(MyModelViewSet):
    column_exclude_list = ('created', 'updated')
    form_excluded_columns = ('created', 'updated')
