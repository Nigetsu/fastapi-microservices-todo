from typing import Annotated
from uuid import uuid4
from sqlalchemy import UUID
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncAttrs,
)
from sqlalchemy.orm import (
    mapped_column,
    DeclarativeBase,
)

from core.config import get_db_url

DATABASE_URL = get_db_url()

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

uuid_pk = Annotated[uuid4, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
