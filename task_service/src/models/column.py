from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import UUID, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base

if TYPE_CHECKING:
    from src.models.task import Task
    from src.models.board import Board


class Column(Base):
    __tablename__ = 'columns'

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    board_id: Mapped[int] = mapped_column(ForeignKey('boards.id'), nullable=False)

    board: Mapped['Board'] = relationship(back_populates='columns')
    tasks: Mapped[list['Task']] = relationship(back_populates='column')
