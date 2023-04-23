from flask import Blueprint

from ..lib.logging import get_logger


logger = get_logger(__name__)
bp = Blueprint("health", __name__)


@bp.route("/ping", methods=("GET",))
def ping():
    logger.info("Hit to /ping.")
    return "PONG"
