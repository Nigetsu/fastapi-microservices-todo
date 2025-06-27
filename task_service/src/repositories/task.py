from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import Result, select, func

from src.models import Task, TaskExecutor, TaskWatcher
from src.schemas.task import TaskFilters
from src.utils.repository import SqlAlchemyRepository


class TaskRepository(SqlAlchemyRepository[Task]):
    _model = Task

    async def get_tasks_by_filters(self, filters: TaskFilters) -> Sequence[Task]:
        query = select(self._model)

        if filters.author_id:
            query = query.where(self._model.author_id.in_(filters.author_id))

        if filters.status:
            query = query.where(self._model.status.in_(filters.status))

        if filters.assignee_id:
            query = query.where(self._model.status.in_(filters.assignee_id))

        res: Result = await self._session.execute(query)
        return res.scalars().all()

    async def count_executor_tasks(self, user_id: UUID) -> int:
        res = select(func.count()).select_from(TaskExecutor).where(TaskExecutor.user_id == user_id)
        result = await self._session.scalar(res)
        return result or 0

    async def count_watcher_tasks(self, user_id: UUID) -> int:
        res = select(func.count()).select_from(TaskWatcher).where(TaskWatcher.user_id == user_id)
        result = await self._session.scalar(res)
        return result or 0

    async def add_executor(self, task_id: UUID, user_id: UUID) -> None:
        self._session.add(TaskExecutor(task_id=task_id, user_id=user_id))

    async def add_watcher(self, task_id: UUID, user_id: UUID) -> None:
        self._session.add(TaskWatcher(task_id=task_id, user_id=user_id))
