from sqlalchemy.exc import SQLAlchemyError
from core.models.user import User
from core.models.base import async_session_maker
from sqlalchemy.future import select


class UserDAO:
    model = User

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def add(cls, **value):
        async with async_session_maker() as session:
            async with session.begin():
                new_instance = cls.model(**value)
                session.add(new_instance)
                await session.flush()
                await session.refresh(new_instance)
                return new_instance