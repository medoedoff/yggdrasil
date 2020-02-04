import os

from flask import Flask
from flask import jsonify
from flask import send_file

from libs.common import check_dir_existence, check_file_existence

errors = [404, 406, 403]

app = Flask(__name__)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    base_dir_path = list(path.rsplit('/', 1))
    base_dir_path.remove('download')
    base_dir_path = ' '.join(map(str, base_dir_path))
    base_dir_path = 'packages/{}'.format(base_dir_path)
    base_package_path = 'packages/{}'.format(path)

    message, status_code = check_dir_existence(base_dir_path)
    if status_code in errors:
        return jsonify(error_message=message), status_code

    message, status_code = check_file_existence(path)
    if status_code in errors:
        return jsonify(error_message=message), status_code

    return send_file(base_package_path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5151')
