from os import path, getenv
from dotenv import load_dotenv
from logging.config import fileConfig

from flask import Flask, request

from .admin import admin, MyAdminIndexView, MyModelView

from .models import db, Users, Roles

log_file_path = path.join(path.dirname(path.abspath(__file__)), '../logging.cfg')
env_path = path.join(path.dirname(path.abspath(__file__)), '../.env')

fileConfig(log_file_path)

load_dotenv(dotenv_path=env_path)


def create_app():
    app = Flask(__name__)
    app.config.from_object(getenv('APP_SETTINGS'))

    @app.before_request
    def log_request_info():
        app.logger.info('Headers: %s', request.headers)
        app.logger.info('Body: %s', request.get_data())

    db.init_app(app)
    admin.init_app(app, index_view=MyAdminIndexView())

    admin.add_view(MyModelView(Users, db.session))
    admin.add_view(MyModelView(Roles, db.session))

    with app.app_context():
        from .crates import mirror_blueprint, upload_package_blueprint
        from .healthcheck import health_check_blueprint

        app.register_blueprint(mirror_blueprint)
        app.register_blueprint(upload_package_blueprint)
        app.register_blueprint(health_check_blueprint)

        return app
