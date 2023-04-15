from flask import Flask


from .lib.logging import configure_logging, get_logger


logger = get_logger(__name__)


def create_app():
    configure_logging("INFO")

    app = Flask(__name__)

    from . import health
    app.register_blueprint(health.bp)

    logger.info("Application created.")
    return app
