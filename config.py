import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Settings:
    current_application_path = os.path.dirname(os.path.abspath('__main__'))
    log_file_path = f'{current_application_path}/logging.cfg'
    env_path = f'{current_application_path}/.env'


class Config:
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    FLASK_ADMIN_SWATCH = 'flatly'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_TRACKABLE = True


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgres://teldrassil@127.0.0.1/teldrassil_db'
    DEVELOPMENT = True
    DEBUG = True
    SECURITY_PASSWORD_SALT = 'aF&YQ&a?63y=7dG'
