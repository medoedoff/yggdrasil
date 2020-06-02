from flask import Blueprint

login = Blueprint('login', __name__)


@login.route('/login', methods=['GET', 'POST'])
def login():
    pass
