from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.menu import MenuLink
from flask_security.utils import hash_password
from flask_security import current_user
from flask_jwt_extended import JWTManager
from flask_wtf import FlaskForm
from flask import flash
from wtforms import PasswordField, ValidationError
from flask import redirect, url_for, request

from .utils import password_validation, email_validation, db, gen_token_payload, gen_public_id
from .models import Tokens, BlacklistedTokens, Users

admin = Admin(name='GIB-Teldrassil', template_mode='bootstrap3')
jwt = JWTManager()


class MyAdminIndexViewSet(AdminIndexView):
    def is_accessible(self, *args, **kwargs):
        if current_user.is_authenticated and current_user.is_active:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))

    @staticmethod
    def _create_token(data):
        token_id = gen_public_id()
        email = current_user.email
        save_to_db = Tokens(user_id=current_user.id, token_id=token_id, name=data.get('name'),
                            description=data.get('description'))
        db.session.add(save_to_db)
        db.session.commit()

        # Create auth token
        payload = gen_token_payload(email=email, token_id=token_id, days_lifetime=False)
        auth_token = Users.encode_auth_token(payload=payload).decode('utf-8')
        flash(f'Copy this token now, because it cannot be recovered in the future: {auth_token}', 'success')
        return redirect(url_for('admin.index'))

    @staticmethod
    def _revoke_token(data):
        token_id = data.get('Token id', None)
        black_list_token = BlacklistedTokens(token_id=token_id)
        db.session.add(black_list_token)
        db.session.commit()
        Tokens.query.filter_by(token_id=token_id).delete()
        db.session.commit()
        flash(f'Successfully revoked: {token_id}', 'success')
        return redirect(url_for('admin.index'))

    @expose('/', methods=('GET', 'POST'))
    def index(self):
        action = request.values.get('action')
        data = request.values
        auth_token = None
        tokens = Tokens.query.filter_by(user_id=current_user.id).all()
        response_data = {
            'full_name': f'{current_user.first_name} {current_user.last_name}',
            'auth_tokens': {
            }
        }
        for i in range(len(tokens)):
            response_data['auth_tokens'][i] = {
                'Token id': tokens[i].token_id,
                'Name': tokens[i].name,
                'Description': tokens[i].description,
                'Authorized at': tokens[i].authorized_at
            }
        if action == 'create':
            return self._create_token(data)

        elif action == 'revoke':
            return self._revoke_token(data)

        return self.render('admin/index.html', data=response_data, token=auth_token)


class MyModelViewSet(ModelView):
    form_base_class = FlaskForm

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
    form_excluded_columns = ('created', 'updated', 'token_id')
