from dataclasses import dataclass
from enum import Enum

from fastapi import Query
from pydantic import UUID4, BaseModel, field_validator

from src.schemas.filter import TypeFilter
from src.schemas.response import BaseCreateResponse, BaseResponse


class TaskID(BaseModel):
    id: UUID4


class TaskStatus(str, Enum):
    TODO = 'todo'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'


class TaskCreateRequest(BaseModel):
    title: str
    status: TaskStatus
    author_id: UUID4
    assignee_id: UUID4 | None = None

    @field_validator('title')
    def validate_title_length(cls, v):
        if len(v) < 3:
            raise ValueError('Title must be at least 3 characters long')
        return v


class TaskDB(TaskID, TaskCreateRequest):
    pass


class TasksListResponse(BaseResponse):
    payload: list[TaskDB]


class TaskCreateResponse(BaseResponse):
    payload: UUID4


class TaskResponse(BaseCreateResponse):
    payload: TaskDB


class TaskUpdateRequest(BaseModel):
    title: str
    description: str | None

    @field_validator('title')
    def validate_title_length(cls, v):
        if len(v) < 3:
            raise ValueError('Title must be at least 3 characters long')
        return v

    @field_validator('description')
    def validate_description(cls, v):
        if v is not None:
            forbidden_chars = ['<', '>', '&', "'", '"']
            if any(char in v for char in forbidden_chars):
                raise ValueError('Description contains invalid characters')
            if len(v) > 2000:
                raise ValueError('Description too long (max 2000 chars)')
            if len(v) < 3:
                raise ValueError('Description too short (min 3 chars)')
        return v


@dataclass
class TaskFilters(TypeFilter):
    assignee_id: list[UUID4] | None = Query(None)
    status: list[TaskStatus] | None = Query(None)
    author_id: list[UUID4] | None = Query(None)
