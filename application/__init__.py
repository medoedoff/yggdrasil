from os import getenv
from logging.config import fileConfig
from dotenv import load_dotenv

from flask import Flask
from flask_security import SQLAlchemyUserDatastore, Security

from .admin import admin, MyAdminIndexViewSet, UserModelViewSet, RoleModelViewSet

from .models import db, Users, Roles

from config import Settings

security = Security()

fileConfig(Settings.log_file_path)

load_dotenv(dotenv_path=Settings.env_path)


def create_app():
    app = Flask(__name__)
    app.config.from_object(getenv('APP_SETTINGS'))

    user_datastore = SQLAlchemyUserDatastore(db, Users, Roles)

    db.init_app(app)
    admin.init_app(app, index_view=MyAdminIndexViewSet())
    security.init_app(app, user_datastore, register_blueprint=False)

    admin.add_view(UserModelViewSet(Users, db.session))
    admin.add_view(RoleModelViewSet(Roles, db.session))

    with app.app_context():
        from .crates import mirror_blueprint, upload_package_blueprint
        from .healthcheck import health_check_blueprint
        from .auth import login_blueprint

        app.register_blueprint(mirror_blueprint, url_prefix='/api/v1/crates')
        app.register_blueprint(upload_package_blueprint, url_prefix='/api/v1/crates')
        app.register_blueprint(health_check_blueprint)
        app.register_blueprint(login_blueprint)

        return app
