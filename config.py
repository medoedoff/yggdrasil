import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))


class Settings:
    current_application_path = os.path.dirname(os.path.abspath('__main__'))
    log_file_path = f'{current_application_path}/logging.cfg'
    env_path = f'{current_application_path}/.env'


class Config:
    load_dotenv(Settings.env_path)

    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY', None)
    FLASK_ADMIN_SWATCH = 'flatly'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_TRACKABLE = True
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', None)
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', None)


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
