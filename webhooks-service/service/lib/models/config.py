from typing import Dict
from functools import reduce

from pydantic import BaseModel, conlist, validator


class ShotgridStatus(BaseModel):
    key: str
    label: str


class StatusMapping(BaseModel):
    shot_statuses: conlist(ShotgridStatus, min_items=1)
    task_statuses: conlist(ShotgridStatus, min_items=1)
    shot_to_task: Dict[str, conlist(str, min_items=1)]
    task_to_shot: Dict[str, conlist(str, min_items=1)]

    @validator("shot_to_task")
    def shot_to_task_is_valid(cls, shot_to_task, values):
        if "shot_statuses" in values:
            mapped_statuses = set(shot_to_task.keys())
            existing_statuses = set(v.key for v in values["shot_statuses"])

            unmapped_statuses = existing_statuses - mapped_statuses
            if unmapped_statuses:
                raise ValueError(
                    "The following shot statuses were not mapped to any task "
                    "statuses: " + ", ".join(unmapped_statuses)
                )

            nonexistent_statuses = mapped_statuses - existing_statuses
            if nonexistent_statuses:
                raise ValueError(
                    "The following shot statuses were mapped but do not exist: "
                    + ", ".join(nonexistent_statuses)
                )

        if "task_statuses" in values:
            output_statuses = set(
                reduce(list.__add__, (v for v in shot_to_task.values()))
            )
            existing_statuses = set(v.key for v in values["task_statuses"])
            nonexistent_statuses = output_statuses - existing_statuses
            if nonexistent_statuses:
                raise ValueError(
                    "The following task statuses were mapped to but do not "
                    "exist: " + ", ".join(nonexistent_statuses)
                )

    @validator("task_to_shot")
    def task_to_shot_is_valid(cls, task_to_shot, values):
        if "task_statuses" in values:
            mapped_statuses = set(task_to_shot.keys())
            existing_statuses = set(v.key for v in values["task_statuses"])

            unmapped_statuses = existing_statuses - mapped_statuses
            if unmapped_statuses:
                raise ValueError(
                    "The following task statuses were not mapped to any shot "
                    "statuses: " + ", ".join(unmapped_statuses)
                )

            nonexistent_statuses = mapped_statuses - existing_statuses
            if nonexistent_statuses:
                raise ValueError(
                    "The following task statuses were mapped but do not exist: "
                    + ", ".join(nonexistent_statuses)
                )

        if "shot_statuses" in values:
            output_statuses = set(
                reduce(list.__add__, (v for v in task_to_shot.values()))
            )
            existing_statuses = set(v.key for v in values["shot_statuses"])
            nonexistent_statuses = output_statuses - existing_statuses
            if nonexistent_statuses:
                raise ValueError(
                    "The following shot statuses were mapped to but do not "
                    "exist: " + ", ".join(nonexistent_statuses)
                )
