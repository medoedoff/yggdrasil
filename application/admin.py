from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView
from flask import redirect, url_for

from .auth import token_required

admin = Admin(name='GIB-Teldrassil')


class MyAdminIndexView(AdminIndexView):
    @token_required
    def is_accessible(self, current_user):
        return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login_auth.login_get'))


class MyModelView(ModelView):
    pass
