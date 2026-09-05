import traceback
from flask import Flask, Response
from app.utils.responses import error_response


def register_error_handlers(app: Flask) -> None:

    @app.errorhandler(404)
    def not_found(error) -> tuple[Response, int]:
        return error_response(message="Resource not found.",status_code=404)


    @app.errorhandler(500)
    def internal_server_error(error) -> tuple[Response, int]:
        return error_response(message="Internal server error.",status_code=500)


    @app.errorhandler(Exception)
    def handle_exception(error) -> tuple[Response, int]:
        print(error)
        traceback.print_exc()
        return error_response(message="An unexpected error occurred.",status_code=500)