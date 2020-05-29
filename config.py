import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = False
    # SECRET_KEY = 'dont forget put the key'
    FLASK_ADMIN_SWATCH = 'cyborg'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgres://teldrassil@127.0.0.1/teldrassil_db'
    DEVELOPMENT = True
    DEBUG = True
    SECURITY_PASSWORD_SALT = 'aF&YQ&a?63y=7dG'
