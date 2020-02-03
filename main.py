from flask import Flask
from flask import request
from flask import jsonify

from libs.common import check_dir_existence


errors = [404, 406, 403]

app = Flask(__name__)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    base_url = '/api/v1/crates/{}'.format(path)
    package_path = list(path.rsplit('/', 1))
    package_path.remove('download')
    package_path = ' '.join(map(str, package_path))

    message, status_code = check_dir_existence(package_path)
    if status_code in errors:
        return jsonify(error_message=message), status_code
    return jsonify(message=message), status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5151')
