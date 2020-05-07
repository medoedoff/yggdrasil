from flask import jsonify, send_file, Blueprint
from libs.common import check_package_dir_existence, check_package_existence

mirror_blueprint = Blueprint('mirror', __name__)
error_status = 406


@mirror_blueprint.route('/', defaults={'path': ''})
@mirror_blueprint.route('/<path:path>')
def mirror(path):
    """
    :param path: take from request url path to package
    :return: package if ok or error
    """
    try:
        base_dir_path = list(path.rsplit('/', 1))
        base_dir_path.remove('download')
        base_dir_path = ' '.join(map(str, base_dir_path))
        base_dir_path = f'packages/{base_dir_path}'
        base_package_path = f'packages/{path}'
    except ValueError:
        return jsonify(error='Incorrect request'), error_status

    base_path = f'packages/{path}'
    base_url = f'https://crates.io/api/v1/crates/{path}'

    try:
        check_package_dir_existence(base_dir_path)
        check_package_existence(base_path, base_url)
    except (PermissionError, OSError, IOError) as e:
        return jsonify(error=f'Some error occurred: {e}'), error_status

    return send_file(base_package_path)
