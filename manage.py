import os
import sys
import re

from flask_script import Manager, prompt, prompt_pass
from flask_migrate import Migrate, MigrateCommand
from flask_security import SQLAlchemyUserDatastore, Security
from flask_security.utils import hash_password

from users_app.models import *

from app import app, db

app.config.from_object(os.getenv('APP_SETTINGS'))

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


@manager.command
def createsuperuser():
    """
    Create a super user of the system, requiring Email and password.
    """

    email = prompt('User E-Mail')
    email_confirm = prompt('Confirm E-Mail')

    if not email == email_confirm:
        sys.exit('\nCould not create user: E-Mail did not match')

    if not EMAIL_REGEX.match(email):
        sys.exit('\nCould not create user: Invalid E-Mail addresss')

    password = prompt_pass('User password')
    password_confirm = prompt_pass('Confirmed password')

    if not password == password_confirm:
        sys.exit('\nCould not create user: Passwords did not match')

    datastore = SQLAlchemyUserDatastore(db, Users, Roles)
    security = Security(app, datastore)
    datastore.create_user(
        email=email,
        password=hash_password(password),
        active=True,
        super_user=True)

    db.session.commit()


if __name__ == '__main__':
    manager.run()
