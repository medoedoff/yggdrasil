from os import path
from flask import Flask
from flask import jsonify
from mirror_app.view import mirror_blueprint
from logging.config import fileConfig

log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.cfg')

app = Flask(__name__)
app.register_blueprint(mirror_blueprint)

fileConfig(log_file_path)


@app.route('/check')
def health_check():
    return jsonify(status='ok')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5151')
