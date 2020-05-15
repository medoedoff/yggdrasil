import os

from flask import jsonify, Blueprint, request
from libs.common import check_package_dir_existence

upload_package_blueprint = Blueprint('upload_package', __name__)
error_status = 406

UPLOAD_DIRECTORY = "upload"
check_package_dir_existence(UPLOAD_DIRECTORY)


@upload_package_blueprint.route('/api/v1/crates/new', methods=['PUT'])
def upload():
    """
    format of data:
    < le u32 of json >
    < json request > (metadata for the package)
    < le u32 of tarball >
    < source tarball >
    """
    data = request.data
    json_bytes = data[4:int.from_bytes(data[0:4], "little") + 4]  # get json bytes information about package

    return jsonify(data=data)
