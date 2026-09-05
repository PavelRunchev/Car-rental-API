from flask import jsonify, Response
from typing import Any


def success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> tuple[Response, int]:
    return jsonify({"success": True,"message": message,"data": data}), status_code


def error_response(message: str = "Error", status_code: int = 400, errors: dict[str, str] | None = None) -> tuple[Response, int]:
    return jsonify({"success": False,"message": message,"errors": errors}), status_code