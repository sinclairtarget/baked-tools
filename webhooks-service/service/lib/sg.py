import os
import logging

import shotgun_api3

from .errors import APIKeyNotFoundError


logger = logging.getLogger(__name__)


API_KEY_ENV_VAR_NAME = "SHOTGRID_API_KEY"
_HOSTNAME = "https://baked.shotgunstudio.com"
_SCRIPT_NAME = "baked-tools"


class SG:
    def __init__(self, hostname=_HOSTNAME, api_key=None):
        self._hostname = hostname

        try:
            self._api_key = (
                api_key or os.environ[API_KEY_ENV_VAR_NAME]
            )
        except KeyError as e:
            raise APIKeyNotFoundError(API_KEY_ENV_VAR_NAME) from e

        self._api = shotgun_api3.Shotgun(
            self._hostname,
            script_name=_SCRIPT_NAME,
            api_key=self._api_key,
        )

    def find_shot(self, shot_id):
        return self._api.find_one(
            "Shot",
            [["id", "is", shot_id]],
            [
                "id",
                "cached_display_name",
                "project",
                "code",
                "created_at",
                "created_by",
                "updated_at",
                "updated_by",
                "description",
                "user",
                "sg_status_list",
                "tasks",
            ]
        )

    def find_shot_by_task(self, task_id):
        return self._api.find_one(
            "Shot",
            [["tasks", "is", { "type": "Task", "id": task_id }]],
            [
                "id",
                "cached_display_name",
                "project",
                "code",
                "created_at",
                "created_by",
                "updated_at",
                "updated_by",
                "description",
                "user",
                "sg_status_list",
                "tasks",
            ]
        )

    def find_task(self, task_id):
        return self._api.find_one(
            "Task",
            [["id", "is", task_id]],
            [
                "id",
                "cached_display_name",
                "project",
                "code",
                "created_at",
                "created_by",
                "updated_at",
                "updated_by",
                "sg_status_list",
                "sg_versions",
                "sg_latest_version",
                "sg_shot_code",
            ]
        )

    def find_version(self, version_id):
        return self._api.find_one(
            "Version",
            [["id", "is", version_id]],
            [
                "id",
                "cached_display_name",
                "project",
                "created_at",
                "created_by",
                "updated_at",
                "updated_by",
                "sg_status_list",
                "sg_link_to_shot",
                "sg_task",
            ]
        )


    def find_tasks(self, task_ids):
        filters = [{
            "filter_operator": "any",
            "filters": [["id", "is", task_id] for task_id in task_ids]
        }]
        return self._api.find(
            "Task",
            filters,
            [
                "id",
                "project",
                "cached_display_name",
                "sg_status_list",
            ])

    def set_task_status(self, task_ids, new_status):
        batch_data = [
            {
                "request_type": "update",
                "entity_type": "Task",
                "entity_id": task_id,
                "data": {
                    "sg_status_list": new_status,
                }
            }
            for task_id in task_ids
        ]
        return self._api.batch(batch_data)

    def set_shot_status(self, shot_id, new_status):
        data = {
            "shots": [{ "type": "Shot", "id": shot_id }],
            "sg_status_list": new_status,
        }
        return self._api.update("Shot", shot_id, data)


def update_linked_tasks(project_id, shot_id, valid_task_statuses):
    """
    For the given shot, finds all linked tasks and updates their status.

    If a linked task already has a status in the list valid_task_statuses, the
    linked task is not updated. Otherwise, the linked task has its status
    updated to the first status in valid_task_statuses.

    Returns a tuple with the list of original tasks and a list of tasks that
    were updated.
    """
    sg = SG()
    shot = sg.find_shot(shot_id)

    linked_task_ids = [t["id"] for t in shot["tasks"]]
    linked_tasks = sg.find_tasks(linked_task_ids)
    tasks_to_update = [
        t for t in linked_tasks
        if not t["sg_status_list"] in valid_task_statuses
    ]

    updated_tasks = sg.set_task_status(
        (t["id"] for t in tasks_to_update),
        valid_task_statuses[0]
    )

    return tasks_to_update, updated_tasks


def update_linked_shot(project_id, task_id, valid_shot_statuses):
    """
    For the given task, finds the linked shot and updates its status.

    If the linked shot already has a status in the list valid_shot_statuses,
    the linked shot is not updated. Otherwise, the linked shot has its status
    updated to the first status in valid_shot_statuses.

    Returns a tuple of the original shot and the updated shot.
    """
    sg = SG()
    shot = sg.find_shot_by_task(task_id)

    if shot["sg_status_list"] in valid_shot_statuses:
        return shot, None
    else:
        updated_shot = sg.set_shot_status(shot["id"], valid_shot_statuses[0])
        return shot, updated_shot


def update_linked_task(project_id, version_id, valid_task_statuses):
    sg = SG()
    version = sg.find_version(version_id)

    task_id = version["sg_task"]["id"]
    task = sg.find_task(task_id)

    if task["sg_status_list"] in valid_task_statuses:
        return task, None
    else:
        updated_tasks = sg.set_task_status([task_id], valid_task_statuses[0])
        return task, updated_tasks[0]
