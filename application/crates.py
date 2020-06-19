import json
import logging

from os import getenv
from hashlib import sha256
from config import Settings
from flask import jsonify, send_file, Blueprint, request
from libs.common import check_package_dir_existence, check_package_existence
from libs.repository import Index, SavePackage, ReformatPackageJson, HTTPStatus

from .utils import csrf
from .auth import token_required

mirror_blueprint = Blueprint('mirror', __name__)
upload_package_blueprint = Blueprint('upload_package', __name__)

error_statuses = {
    HTTPStatus.CONFLICT.value: 'package current version already exists',
    HTTPStatus.BAD_REQUEST.value: 'invalid package name',
    HTTPStatus.FORBIDDEN.value: 'You have not valid access rights'
}

success_statuses = {
    HTTPStatus.OK.value: 'ok'
}


# Cashing packages from upstream
@mirror_blueprint.route('/<package>/<version>/download', methods=['GET'])
@csrf.exempt
def mirror(package, version):
    """
    :param version: str package version
    :param package: str package name
    :return: package if ok or error
    """
    package_name = package
    version = version

    base_dir_path = f'{Settings.current_application_path}/packages/{package_name}/{version}'
    base_package_path = f'{base_dir_path}/download'

    base_url = f'https://crates.io/api/v1/crates/{package_name}/{version}/download'

    try:
        check_package_dir_existence(base_dir_path)
        check_package_existence(base_package_path, base_url)
    except (PermissionError, OSError, IOError, FileNotFoundError) as e:
        return jsonify(error=f'Some error occurred: {e}'), HTTPStatus.NOT_ACCEPTABLE.value

    return send_file(base_package_path)


# Logging request info
@upload_package_blueprint.before_request
def log_request_info():
    logging.info('Headers: %s', request.headers)
    logging.info('Body: %s', request.get_data())


# Upload private packages
@upload_package_blueprint.route('/new', methods=['PUT'])
@csrf.exempt
@token_required
def upload(current_user):
    """
    :param current_user: dict or None if None current user authentication not passed
    format of data:
    < le u32 of json >
    < json request > (metadata for the package)
    < le u32 of tarball >
    < source tarball >
    """
    if current_user is not None and current_user.is_active:
        data = request.data
        git_index_path = getenv('GIT_INDEX_PATH', None)
        json_bytes = data[4:int.from_bytes(data[0:4], "little") + 4]  # get json bytes information about package
        tar_bytes = data[int.from_bytes(data[0:4], "little") + 8:]  # get data bytes of package
        package_hash = sha256(tar_bytes).hexdigest()
        package_metadata = json.loads(json_bytes)

        reformat_package_metadata = ReformatPackageJson(package_metadata=package_metadata, package_hash=package_hash)
        package_info = reformat_package_metadata.reformat()

        package_name = package_info['name']
        package_version = package_info['vers']
        package_path = f'packages/{package_name}/{package_version}/download'
        package_dir = f'packages/{package_name}/{package_version}'

        index = Index(index_path=git_index_path, package_info=package_info, package_name=package_name)
        package = SavePackage(path_to_save=package_path, package_data=tar_bytes)

        status = index.synchronise()
        if status in success_statuses:
            check_package_dir_existence(package_dir)
            package.save()
            return jsonify(message=success_statuses[HTTPStatus.OK.value]), status
        elif status in error_statuses:
            return jsonify(message=error_statuses[status]), status
    else:
        return jsonify(message=error_statuses[HTTPStatus.FORBIDDEN.value]), HTTPStatus.FORBIDDEN.value

