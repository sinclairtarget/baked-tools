import json
import sys
import os

from flask import Flask
import werkzeug.exceptions

from .lib.logging import configure_logging, get_logger
from .lib.config import load_status_mapping
from .lib.errors import ConfigurationError
from .routes import health
from .routes.webhooks import status


WEBHOOK_SECRET_TOKEN_ENV_VAR_NAME = "SHOTGRID_SECRET_TOKEN"


logger = get_logger(__name__)


def create_app():
    if "LOGFILE_PATH" in os.environ:
        configure_logging("INFO", filename=os.environ["LOGFILE_PATH"])
    else:
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
        app.config["SECRET_TOKEN"] = os.environ[WEBHOOK_SECRET_TOKEN_ENV_VAR_NAME]
    except KeyError:
        print(
            "Could not start application because of missing secret token.",
            file=sys.stderr,
        )
        print(
            f'Did you set the "{WEBHOOK_SECRET_TOKEN_ENV_VAR_NAME}" env var?',
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        m = load_status_mapping()
    except ConfigurationError as e:
        print(
            "Could not start application because of a configuration issue:\n" +
            str(e),
            file=sys.stderr,
        )
        sys.exit(1)

    if inconsistency := m.check_inconsistent():
        print(
            "Could not start application because status mapping was inconsistent:\n" +
            inconsistency,
            file=sys.stderr,
        )
        sys.exit(1)

    app.config["STATUS_MAPPING"] = m

    logger.info("Application created.")
    return app
