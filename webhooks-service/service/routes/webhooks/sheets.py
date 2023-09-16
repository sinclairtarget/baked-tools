"""
Exposes an endpoint for syncing data with Google sheets.
"""
import time

from flask import Blueprint, request

from ...lib.logging import get_logger
from ...lib.sg import SG
from ...lib.google import GoogleSheetsClient
from ...lib.errors import ProjectNotFoundError


logger = get_logger(__name__)
bp = Blueprint("sheets", __name__)


def _parse_project_name_from_spreadsheet_name(spreadsheet_name):
    return spreadsheet_name.split("_")[0]


@bp.route("/sync", methods=("POST",))
def trigger_sync():
    logger.info("Got request to spreadsheet sync endpoint.")
    post_body = request.get_json()

    try:
        spreadsheet_name = post_body["spreadsheet_name"]
        spreadsheet_id = post_body["spreadsheet_id"]
    except KeyError as e:
        msg = f"Request was missing key: {e}"
        logger.error(msg)
        return { "message": msg }, 400


    start_time = time.perf_counter()

    logger.info(f"Got request to update spreadsheet: {spreadsheet_name}.")
    project_name = _parse_project_name_from_spreadsheet_name(spreadsheet_name)
    logger.info(f"Project name is: {project_name}.")

    sg = SG()
    logger.info("Resolving project ID...")
    try:
        project_id = sg.resolve_project_id(project_name)
    except ProjectNotFoundError as e:
        msg = f'Project "{e.project_name}" not found.'
        logger.error(msg)
        return { "message": msg }, 400

    logger.info(f"Found project ID: {project_id}")

    logger.info("Getting shots...")
    shots = sg.list_shots(project_id)

    logger.info("Syncing with Google sheets...")
    gc = GoogleSheetsClient()
    success, err = gc.sync_shots_to_spreadsheet(spreadsheet_id, shots)

    end_time = time.perf_counter()
    logger.info(f"Done in {end_time - start_time:0.2f} seconds.")

    if not success:
        msg = f"Could not sync with Google sheets: {err}"
        logger.error(msg)
        return { "message": msg }, 502

    return "", 204
