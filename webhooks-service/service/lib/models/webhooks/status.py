from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator


TEST_CONNECTION_EVENT_TYPE = "Test_Connection"


class Entity(BaseModel):
    type: Optional[str]
    id: int


class Project(BaseModel):
    type: str
    id: int


class AttributeChangeMeta(BaseModel):
    old_value: Optional[str] = None
    new_value: Optional[str] = None

class User(BaseModel):
    id: int
    type: str


class WebhookData(BaseModel):
    event_type: str
    entity: Entity
    project: Project
    meta : AttributeChangeMeta
    user: User


class WebhookBody(BaseModel):
    data: WebhookData
    timestamp: datetime

    @validator("data")
    def data_is_valid(cls, data, values):
        if data.event_type != TEST_CONNECTION_EVENT_TYPE:
            if not data.entity.type:
                raise ValueError("Entity needs type.")

            if not data.meta.old_value:
                raise ValueError("Attribute change meta needs old value.")

            if not data.meta.new_value:
                raise ValueError("Attribute change meta needs new value.")

        return data

    @property
    def is_test_connection(self):
        return self.data.event_type == TEST_CONNECTION_EVENT_TYPE
