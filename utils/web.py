from flask import jsonify


def bad_request(message, status_code=400):
    return jsonify({'error': message}), status_code
