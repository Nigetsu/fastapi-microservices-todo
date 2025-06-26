from datetime import date
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import UUID, String, CheckConstraint, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base

if TYPE_CHECKING:
    from src.models.task import Task


class Sprint(Base):
    __tablename__ = 'sprints'

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)

    __table_args__ = (
        CheckConstraint('end_date > start_date', name='check_sprint_dates'),
    )

    tasks: Mapped[list['Task']] = relationship(back_populates='sprint')
