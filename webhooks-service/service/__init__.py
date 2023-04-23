import json

from flask import Flask
import werkzeug.exceptions

from .lib.logging import configure_logging, get_logger
from .routes import health
from .routes.webhooks import status


logger = get_logger(__name__)


def create_app():
    configure_logging("INFO")

    app = Flask(__name__)

    app.register_blueprint(health.bp)
    app.register_blueprint(status.bp, url_prefix="/webhooks/status")

    @app.errorhandler(werkzeug.exceptions.HTTPException)
    def handle_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        # start with the correct headers and status code from the error
        response = e.get_response()
        # replace the body with JSON
        response.data = json.dumps({
            "error": e.name,
            "description": e.description,
        })
        response.content_type = "application/json"
        return response

    logger.info("Application created.")
    return app
