import json
import sys

from flask import Flask
import werkzeug.exceptions

from .lib.logging import configure_logging, get_logger
from .lib.config import load_status_mapping
from .lib.errors import ConfigurationError
from .routes import health
from .routes.webhooks import status


DEFAULT_STATUS_MAPPING_FILEPATH = "status_mapping.yaml"


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

    try:
        app.config["STATUS_MAPPING"] = load_status_mapping(
            DEFAULT_STATUS_MAPPING_FILEPATH
        )
    except ConfigurationError as e:
        print(
            "Could not start application because of a configuration issue:\n" +
            str(e),
            file=sys.stderr,
        )
        sys.exit(1)

    logger.info("Application created.")
    return app
