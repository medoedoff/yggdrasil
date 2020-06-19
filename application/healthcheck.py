from flask import jsonify, Blueprint

health_check_blueprint = Blueprint('health_check', __name__)


@health_check_blueprint.route('/check', methods=['GET'])
def health_check():
    return jsonify(status='ok')
