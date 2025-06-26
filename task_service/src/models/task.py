from datetime import datetime, UTC
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import (
    UUID,
    DateTime,
    ForeignKey,
    String,
    Text,
    text,
)
from sqlalchemy import (
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base
from src.schemas.task import TaskDB

if TYPE_CHECKING:
    from src.models.board import Board
    from src.models.column import Column
    from src.models.sprint import Sprint
    from src.models.group import Group
    from src.models.task_watcher import TaskWatcher
    from src.models.task_executor import TaskExecutor


class TaskStatus(str, Enum):
    TODO = 'todo'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(SQLAlchemyEnum(TaskStatus), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC))
    author_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), nullable=False)
    assignee_id: Mapped[Optional[uuid4]] = mapped_column(UUID(as_uuid=True))
    column_id: Mapped[Optional[uuid4]] = mapped_column(UUID(as_uuid=True), ForeignKey('columns.id'))
    sprint_id: Mapped[Optional[uuid4]] = mapped_column(UUID(as_uuid=True), ForeignKey('sprints.id'))
    board_id: Mapped[Optional[uuid4]] = mapped_column(UUID(as_uuid=True), ForeignKey('boards.id'))
    group_id: Mapped[Optional[uuid4]] = mapped_column(UUID(as_uuid=True), ForeignKey('groups.id'))

    column: Mapped[Optional['Column']] = relationship(back_populates='tasks')
    sprint: Mapped[Optional['Sprint']] = relationship(back_populates='tasks')
    board: Mapped[Optional['Board']] = relationship(back_populates='tasks')
    group: Mapped[Optional['Group']] = relationship(back_populates='tasks')
    watchers_link: Mapped[list['TaskWatcher']] = relationship(
        'TaskWatcher',
        cascade="all, delete-orphan",
        back_populates='task'
    )

    executors_link: Mapped[list['TaskExecutor']] = relationship(
        'TaskExecutor',
        cascade="all, delete-orphan",
        back_populates='task'
    )

    def to_schema(self) -> TaskDB:
        return TaskDB(**self.__dict__)
