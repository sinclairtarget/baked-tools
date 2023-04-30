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


class WebhookData(BaseModel):
    event_type: str
    entity: Entity
    project: Project
    meta : AttributeChangeMeta


class WebhookBody(BaseModel):
    data: WebhookData
    timestamp: datetime
