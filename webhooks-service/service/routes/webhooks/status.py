from datetime import datetime, timezone

from flask import Blueprint, request, current_app
import pydantic

from ...lib.logging import get_logger
from ...lib.models.webhooks.status import WebhookBody
from ...lib.sg import update_linked_tasks, update_linked_shot
from ...lib.errors import UnknownStatusError
from ...lib.secret import verify_signature


logger = get_logger(__name__)
bp = Blueprint("status", __name__)


def validation_error_response(validation_error):
    return {
        "error": "Validation Error",
        "description": str(validation_error),
    }


def unknown_status_error_response(unknown_status_error):
    return {
        "error": "Unknown Status",
        "description": str(unknown_status_error),
    }


@bp.before_request
def ensure_request_from_shotgrid():
    if "x-sg-signature" not in request.headers:
        return {
            "error": "Authentication Error",
            "description": 'You must provide the "x-sg-signature" header.',
        }, 401

    signature = request.headers["x-sg-signature"]
    if not verify_signature(
        request.get_data(), current_app.config["SECRET_TOKEN"], signature,
    ):
        return {
            "error": "Authentication Error",
            "description": "Request signature not valid.",
        }, 401


@bp.route("/shot", methods=("POST",))
def handle_shot_status_change():
    """
    Receives e.g. the following JSON post body:

    {
      "data": {
        "id": "693322.80953.0",
        "event_log_entry_id": 3635187,
        "event_type": "Shotgun_Shot_Change",
        "operation": "update",
        "user": {
          "type": "HumanUser",
          "id": 1346
        },
        "entity": {
          "type": "Shot",
          "id": 20716
        },
        "project": {
          "type": "Project",
          "id": 2817
        },
        "meta": {
          "type": "attribute_change",
          "attribute_name": "sg_status_list",
          "entity_type": "Shot",
          "entity_id": 20716,
          "field_data_type": "status_list",
          "old_value": "omt",
          "new_value": "actv"
        },
        "created_at": "2023-04-22 21:13:51.550053",
        "attribute_name": "sg_status_list",
        "session_uuid": "85d7a282-e152-11ed-b7ea-0242ac110002",
        "delivery_id": "fe37d91a-fc99-4d9e-acb2-2a4b855348ba"
      },
      "timestamp": "2023-04-22T21:14:43Z"
    }
    """
    post_body = request.get_json()

    try:
        webhook_post_body = WebhookBody.parse_obj(post_body)
    except pydantic.ValidationError as e:
        return validation_error_response(e), 400

    if webhook_post_body.is_test_connection:
        return "", 204

    shot_id = webhook_post_body.data.entity.id
    project_id = webhook_post_body.data.project.id
    old_shot_status = webhook_post_body.data.meta.old_value
    new_shot_status = webhook_post_body.data.meta.new_value
    logger.info(
        f'Shot {shot_id} was updated from status "{old_shot_status}" to '
        f'"{new_shot_status}" in project {project_id}.'
    )

    try:
        task_statuses = current_app.config["STATUS_MAPPING"].map_shot_status(
            new_shot_status
        )
    except UnknownStatusError as e:
        return unknown_status_error_response(e), 400

    if not task_statuses:
        logger.info("Status not mapped to anything.")
        return "", 204

    logger.info(
        "Updating linked tasks to a status that is one of: "
        + ", ".join(task_statuses)
    )

    original_tasks, updated_tasks = update_linked_tasks(
        project_id, shot_id, task_statuses,
    )

    logger.info(f"Updated {len(updated_tasks)} linked tasks.")

    now = datetime.now(timezone.utc)
    delay_seconds = (now - webhook_post_body.timestamp).total_seconds()
    return {
        "project_id": project_id,
        "shot_id": shot_id,
        "lag_after_original_event_ms": int(delay_seconds * 1000),
        "old_shot_status": old_shot_status,
        "new_shot_status": new_shot_status,
        "original_tasks": original_tasks,
        "updated_tasks": updated_tasks,
    }, 200


@bp.route("/task", methods=("POST",))
def handle_task_status_change():
    """
    Receives e.g. the following JSON post body:

    {
      "data": {
        "id": "702994.82192.0",
        "event_log_entry_id": 3674504,
        "event_type": "Shotgun_Task_Change",
        "operation": "update",
        "user": {
          "type": "HumanUser",
          "id": 1346
        },
        "entity": {
          "type": "Task",
          "id": 23802
        },
        "project": {
          "type": "Project",
          "id": 2817
        },
        "meta": {
          "type": "attribute_change",
          "attribute_name": "sg_status_list",
          "entity_type": "Task",
          "entity_id": 23802,
          "field_data_type": "status_list",
          "old_value": "di",
          "new_value": "rdy"
        },
        "created_at": "2023-04-30 15:49:00.426711",
        "attribute_name": "sg_status_list",
        "session_uuid": "32046296-e76d-11ed-ba10-0242ac110003",
        "delivery_id": "c5591b71-7a59-4326-8579-a9e2dd32b8f4"
      },
      "timestamp": "2023-04-30T15:49:01Z"
    }
    """
    post_body = request.get_json()

    try:
        webhook_post_body = WebhookBody.parse_obj(post_body)
    except pydantic.ValidationError as e:
        return validation_error_response(e), 400

    if webhook_post_body.is_test_connection:
        return "", 204

    task_id = webhook_post_body.data.entity.id
    project_id = webhook_post_body.data.project.id
    old_task_status = webhook_post_body.data.meta.old_value
    new_task_status = webhook_post_body.data.meta.new_value
    logger.info(
        f'Task {task_id} was updated from status "{old_task_status}" to '
        f'"{new_task_status}" in project {project_id}.'
    )

    try:
        shot_statuses = current_app.config["STATUS_MAPPING"].map_task_status(
            new_task_status
        )
    except UnknownStatusError as e:
        return unknown_status_error_response(e), 400

    if not shot_statuses:
        logger.info("Status not mapped to anything.")
        return "", 204

    logger.info(
        "Updating linked shot to a status that is one of: "
        + ", ".join(shot_statuses)
    )

    original_shot, updated_shot = update_linked_shot(
        project_id, task_id, shot_statuses,
    )

    if updated_shot is None:
        logger.info("Linked shot did not need to be changed.")
    else:
        logger.info("Updated linked shot.")

    now = datetime.now(timezone.utc)
    delay_second = (now - webhook_post_body.timestamp).total_seconds()
    return {
        "project_id": project_id,
        "task_id": task_id,
        "lag_after_original_event_ms": int(delay_second * 1000),
        "old_task_status": old_task_status,
        "new_task_status": new_task_status,
        "original_shot": original_shot,
        "updated_shot": updated_shot,
    }, 200
