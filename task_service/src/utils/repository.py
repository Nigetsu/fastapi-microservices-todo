from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, Never, TypeVar
from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Base

if TYPE_CHECKING:
    from sqlalchemy.engine import Result


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one_and_get_obj(self, *args: Any, **kwargs: Any) -> Never:
        raise NotImplementedError

    @abstractmethod
    async def get_by_filter_one_or_none(self, *args: Any, **kwargs: Any) -> Never:
        raise NotImplementedError

    @abstractmethod
    async def update_one_by_id(self, *args: Any, **kwargs: Any) -> Never:
        raise NotImplementedError

    @abstractmethod
    async def delete_by_ids(self, *args: Any, **kwargs: Any) -> Never:
        raise NotImplementedError


M = TypeVar('M', bound=Base)


class SqlAlchemyRepository(AbstractRepository, Generic[M]):
    _model: type[M]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_one_and_get_obj(self, **kwargs: Any) -> M:
        query = insert(self._model).values(**kwargs).returning(self._model)
        obj: Result = await self._session.execute(query)
        return obj.scalar_one()

    async def get_by_filter_one_or_none(self, **kwargs: Any) -> M | None:
        query = select(self._model).filter_by(**kwargs)
        res: Result = await self._session.execute(query)
        return res.unique().scalar_one_or_none()

    async def update_one_by_id(self, obj_id: int | str | UUID, **kwargs: Any) -> M | None:
        query = update(self._model).filter(self._model.id == obj_id).values(**kwargs).returning(self._model)
        obj: Result | None = await self._session.execute(query)
        return obj.scalar_one_or_none()

    async def delete_by_ids(self, *args: int | str | UUID) -> None:
        query = delete(self._model).filter(self._model.id.in_(args))
        await self._session.execute(query)
