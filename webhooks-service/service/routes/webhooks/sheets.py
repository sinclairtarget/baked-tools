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
    except KeyError:
        return {
            "message": 'Missing key "spreadsheet_name".'
        }, 400


    logger.info(f"Got request to update spreadsheet: {spreadsheet_name}.")
    project_name = _parse_project_name_from_spreadsheet_name(spreadsheet_name)
    logger.info(f"Project name is: {project_name}.")

    sg = SG()
    logger.info("Resolving project ID...")
    try:
        project_id = sg.resolve_project_id(project_name)
    except ProjectNotFoundError as e:
        return {
            "message": f'Project "{e.project_name}" not found.'
        }, 400

    logger.info(f"Found project ID: {project_id}")

    logger.info("Getting shots...")
    shots = sg.list_shots(project_id)

    logger.info("Syncing with Google sheets...")
    gc = GoogleSheetsClient()
    success = gc.sync_shots_to_spreadsheet(project_name, shots)
    return "", 204 if success else 502
