from os import getenv
from logging.config import fileConfig

from flask import Flask
from flask_security import SQLAlchemyUserDatastore, Security
from flask_wtf.csrf import CSRFProtect

from .admin import admin, jwt, MyAdminIndexViewSet, UserModelViewSet, RoleModelViewSet, MyLogoutMenuLink,\
    BlacklistedModelViewSet, TokensModelViewSet

from .models import db, Users, Roles, BlacklistedTokens, Tokens

from config import Settings

security = Security()
csrf = CSRFProtect()

fileConfig(Settings.log_file_path)


def create_app():
    app = Flask(__name__)
    app.config.from_object(getenv('APP_SETTINGS', None))

    user_datastore = SQLAlchemyUserDatastore(db, Users, Roles)

    db.init_app(app)
    admin.init_app(app, index_view=MyAdminIndexViewSet())
    security.init_app(app, user_datastore, register_blueprint=False)
    jwt.init_app(app)
    csrf.init_app(app)

    admin.add_view(UserModelViewSet(Users, db.session))
    admin.add_view(RoleModelViewSet(Roles, db.session))
    admin.add_view(TokensModelViewSet(Tokens, db.session))
    admin.add_view(BlacklistedModelViewSet(BlacklistedTokens, db.session))
    admin.add_link(MyLogoutMenuLink(name='Logout', category='', url="/logout"))

    with app.app_context():
        from .crates import mirror_blueprint, upload_package_blueprint
        from .healthcheck import health_check_blueprint
        from .auth import auth

        app.register_blueprint(mirror_blueprint, url_prefix='/api/v1/crates')
        app.register_blueprint(upload_package_blueprint, url_prefix='/api/v1/crates')
        app.register_blueprint(health_check_blueprint)
        app.register_blueprint(auth)

        return app
