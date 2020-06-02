from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView

admin = Admin(name='GIB-Teldrassil')


class MyAdminIndexView(AdminIndexView):
    pass


class MyModelView(ModelView):
    pass
