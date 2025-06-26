from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base

if TYPE_CHECKING:
    from src.models.task import Task


class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    tasks: Mapped[list['Task']] = relationship(back_populates='group')
