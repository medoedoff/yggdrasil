import json

from hashlib import sha256

from flask import jsonify, Blueprint, request
from libs.common import check_package_dir_existence
from libs.repository import Index, SavePackage, ReformatPackageJson

upload_package_blueprint = Blueprint('upload_package', __name__)

conflict_status = 409
success_status = 200


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
    index_path = '/opt/tds/crates.io-index'
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

    index = Index(index_path=index_path, package_info=package_info, package_name=package_name)
    package = SavePackage(path_to_save=package_path, package_data=tar_bytes)

    status = index.synchronise()
    if status == success_status:
        check_package_dir_existence(package_dir)
        package.save()
        return jsonify(message='Success!'), success_status
    elif status == conflict_status:
        return jsonify(message='Package current version already exists!'), conflict_status
