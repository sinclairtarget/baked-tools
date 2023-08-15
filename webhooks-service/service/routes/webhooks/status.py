from datetime import datetime, timezone

from flask import Blueprint, request, current_app, g
import pydantic

from ...lib.logging import get_logger
from ...lib.models.webhooks.status import WebhookBody
from ...lib.sg import (
    update_linked_tasks, update_linked_shot, update_linked_task, SG
)
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


@bp.before_request
def handle_webhook():
    post_body = request.get_json()

    try:
        webhook_post_body = WebhookBody.parse_obj(post_body)
    except pydantic.ValidationError as e:
        return validation_error_response(e), 400

    g.webhook = webhook_post_body
    if g.webhook.is_test_connection:
        return "", 204

    if g.webhook.data.user.type != "HumanUser":
        return "", 204


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
    shot_id = g.webhook.data.entity.id
    project_id = g.webhook.data.project.id
    old_shot_status = g.webhook.data.meta.old_value
    new_shot_status = g.webhook.data.meta.new_value
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
    delay_seconds = (now - g.webhook.timestamp).total_seconds()
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
    task_id = g.webhook.data.entity.id
    project_id = g.webhook.data.project.id
    old_task_status = g.webhook.data.meta.old_value
    new_task_status = g.webhook.data.meta.new_value
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
    delay_second = (now - g.webhook.timestamp).total_seconds()
    return {
        "project_id": project_id,
        "task_id": task_id,
        "lag_after_original_event_ms": int(delay_second * 1000),
        "old_task_status": old_task_status,
        "new_task_status": new_task_status,
        "original_shot": original_shot,
        "updated_shot": updated_shot,
    }, 200


@bp.route("/version", methods=("POST",))
def handle_version_status_change():
    """
    {
      "data": {
        "id": "771230.141915.0",
        "meta": {
          "type": "attribute_change",
          "entity_id": 46898,
          "new_value": "note",
          "old_value": "cnv",
          "entity_type": "Version",
          "attribute_name": "sg_status_list",
          "field_data_type": "status_list"
        },
        "user": {
          "id": 1346,
          "type": "HumanUser"
        },
        "entity": {
          "id": 46898,
          "type": "Version"
        },
        "project": {
          "id": 2817,
          "type": "Project"
        },
        "operation": "update",
        "created_at": "2023-05-22 17:40:39.834737",
        "event_type": "Shotgun_Version_Change",
        "delivery_id": "222d1fd2-07b9-4225-a696-e4c617de8e8d",
        "session_uuid": "bb303728-f8c7-11ed-9945-0242ac110004",
        "attribute_name": "sg_status_list",
        "event_log_entry_id": 3842748
      },
      "timestamp": "2023-05-22T17:40:40Z"
    }
    """
    version_id = g.webhook.data.entity.id
    project_id = g.webhook.data.project.id
    old_version_status = g.webhook.data.meta.old_value
    new_version_status = g.webhook.data.meta.new_value
    logger.info(
        f'Version {version_id} was updated from status "{old_version_status}" to '
        f'"{new_version_status}" in project {project_id}.'
    )

    try:
        task_statuses = current_app.config["STATUS_MAPPING"].map_version_status(
            new_version_status
        )
    except UnknownStatusError as e:
        return unknown_status_error_response(e), 400

    if not task_statuses:
        logger.info("Status not mapped to anything.")
        return "", 204

    logger.info(
        "Updating linked task to a status that is one of: "
        + ", ".join(task_statuses)
    )

    original_task, updated_task = update_linked_task(
        project_id, version_id, task_statuses,
    )

    if updated_task is None:
        logger.info("Linked task did not need to be changed.")
    else:
        logger.info("Updated linked task.")
        shot_statuses = current_app.config["STATUS_MAPPING"].map_task_status(
            updated_task["sg_status_list"]
        )

        if shot_statuses:
            logger.info(
                "Also updating linked shot to a status that is one of: "
                + ", ".join(shot_statuses)
            )
            _, updated_shot = update_linked_shot(
                project_id, updated_task["id"], shot_statuses,
            )
            if updated_shot is None:
                logger.info("Linked shot did not need to be changed.")
            else:
                logger.info("Updated linked shot.")


    now = datetime.now(timezone.utc)
    delay_second = (now - g.webhook.timestamp).total_seconds()
    return {
        "project_id": project_id,
        "version_id": version_id,
        "lag_after_original_event_ms": int(delay_second * 1000),
        "old_version_status": old_version_status,
        "new_version_status": new_version_status,
        "original_task": original_task,
        "updated_task": updated_task,
    }, 200


@bp.route("/version-created", methods=("POST",))
def handle_version_created():
    """
    {
      "data": {
        "id": "798477.150082.0",
        "event_log_entry_id": 3980684,
        "event_type": "Shotgun_Version_New",
        "operation": "create",
        "user": {
          "type": "HumanUser",
          "id": 1346
        },
        "entity": {
          "type": "Version",
          "id": 47971
        },
        "project": {
          "type": "Project",
          "id": 2817
        },
        "meta": {
          "type": "new_entity",
          "entity_type": "Version",
          "entity_id": 47971
        },
        "created_at": "2023-06-21 01:39:15.647563",
        "attribute_name": null,
        "session_uuid": "2f5fab2e-0fd4-11ee-a1de-0242ac110003",
        "delivery_id": "5171371f-f36a-4111-ad63-b4b594ee5cbc"
      },
      "timestamp": "2023-06-21T01:39:16Z"
    }

    """
    version_id = g.webhook.data.entity.id
    project_id = g.webhook.data.project.id
    logger.info(f"Version {version_id} was created in project {project_id}.")

    sg = SG()
    version = sg.find_version(version_id)
    if version["code"].lower().startswith("qr_"):
        logger.info(f"Ensuring version {version_id} has status CNV.")
        sg.set_version_status(version_id, "cnv")
        version_status = "cnv"
    else:
        version_status = version["sg_status_list"]

    try:
        task_statuses = current_app.config["STATUS_MAPPING"].map_version_status(
            version_status
        )
    except UnknownStatusError as e:
        return unknown_status_error_response(e), 400

    if not task_statuses:
        logger.info(
            f"Version status \"{version_status}\" not mapped to any task "
            "statuses."
        )
        return "", 204

    logger.info(
        "Updating linked task to a status that is one of: "
        + ", ".join(task_statuses)
    )

    original_task, updated_task = update_linked_task(
        project_id, version_id, task_statuses,
    )

    if updated_task is None:
        logger.info("Linked task did not need to be changed.")
    else:
        logger.info("Updated linked task.")
        shot_statuses = current_app.config["STATUS_MAPPING"].map_task_status(
            updated_task["sg_status_list"]
        )

        if shot_statuses:
            logger.info(
                "Also updating linked shot to a status that is one of: "
                + ", ".join(shot_statuses)
            )
            _, updated_shot = update_linked_shot(
                project_id, updated_task["id"], shot_statuses,
            )
            if updated_shot is None:
                logger.info("Linked shot did not need to be changed.")
            else:
                logger.info("Updated linked shot.")

    now = datetime.now(timezone.utc)
    delay_second = (now - g.webhook.timestamp).total_seconds()
    return {
        "project_id": project_id,
        "version_id": version_id,
        "lag_after_original_event_ms": int(delay_second * 1000),
        "version_status": version_status,
        "original_task": original_task,
        "updated_task": updated_task,
    }, 200
