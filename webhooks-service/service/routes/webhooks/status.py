from datetime import datetime, timezone

from flask import Blueprint, request, current_app
import pydantic

from ...lib.logging import get_logger
from ...lib.models.webhooks.status import ShotStatusWebhookBody
from ...lib.sg import update_linked_tasks


logger = get_logger(__name__)
bp = Blueprint("status", __name__)


def validation_error_response(validation_error):
    return {
        "error": "Validation Error",
        "description": str(validation_error),
    }


@bp.route("/shot", methods=("POST",))
def shot_status():
    """
    Receives the following JSON post body:

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
        webhook_post_body = ShotStatusWebhookBody.parse_obj(post_body)
    except pydantic.ValidationError as e:
        return validation_error_response(e), 400

    shot_id = webhook_post_body.data.entity.id
    project_id = webhook_post_body.data.project.id
    old_shot_status = webhook_post_body.data.meta.old_value
    new_shot_status = webhook_post_body.data.meta.new_value
    logger.info(
        f'Shot {shot_id} was updated from status "{old_shot_status}" to '
        f'"{new_shot_status}" in project {project_id}.'
    )

    task_statuses = current_app.config["STATUS_MAPPING"].map_shot_status(
        new_shot_status
    )
    logger.info(
        "Updating linked tasks to a status that is one of: "
        + ", ".join(task_statuses)
    )

    now = datetime.now(timezone.utc)
    delay_seconds = (now - webhook_post_body.timestamp).total_seconds()
    updated_tasks = update_linked_tasks(project_id, shot_id, task_statuses)

    return {
        "project_id": project_id,
        "shot_id": shot_id,
        "lag_after_original_event_seconds": int(delay_seconds),
        "old_shot_status": old_shot_status,
        "new_shot_status": new_shot_status,
        "updated_tasks": updated_tasks
    }, 200
