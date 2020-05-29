from logging.config import fileConfig
from os import path, getenv

from dotenv import load_dotenv
from flask import Flask, request
from flask import jsonify
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy

from mirror_app.view import mirror_blueprint
from upload_package_app.view import upload_package_blueprint

log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.cfg')
env_path = path.join(path.dirname(path.abspath(__file__)), '.env')

load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

# Configuration
app.config.from_object(getenv('APP_SETTINGS'))

# Extensions
db = SQLAlchemy(app)
admin = Admin(app)

# Blueprints
app.register_blueprint(mirror_blueprint)
app.register_blueprint(upload_package_blueprint)

# Logging
fileConfig(log_file_path)


@app.before_request
def log_request_info():
    app.logger.info('Headers: %s', request.headers)
    app.logger.info('Body: %s', request.get_data())


@app.route('/check')
def health_check():
    return jsonify(status='ok')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5151')
