from flask import request, jsonify


def get_json_data(required_fields=None):
    """Return JSON payload from request or an error response."""
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return None, jsonify({'error': 'Invalid or missing JSON data'}), 400
    if required_fields:
        for field in required_fields:
            if not data.get(field):
                return None, jsonify({'error': f'{field} is required'}), 400
    return data, None, None
