from datetime import datetime

from pydantic import BaseModel


class Entity(BaseModel):
    type: str
    id: int


class Project(BaseModel):
    type: str
    id: int


class AttributeChangeMeta(BaseModel):
    old_value: str
    new_value: str


class ShotAttributeChange(BaseModel):
    entity: Entity
    project: Project
    meta : AttributeChangeMeta


class ShotStatusWebhookBody(BaseModel):
    data: ShotAttributeChange
    timestamp: datetime
