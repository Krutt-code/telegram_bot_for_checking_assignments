from __future__ import annotations

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.schemas import GroupSchema, HomeworkGroupCreateSchema
from src.db.models import GroupsModel, HomeworkGroupsModel
from src.db.repositories import HomeworkGroupsRepository
from src.db.session import with_session


class HomeworkGroupsService:
    """
    Сервис для работы с привязкой заданий к группам (homework_groups).
    """

    homework_groups_repository: HomeworkGroupsRepository = HomeworkGroupsRepository

    @classmethod
    @with_session
    async def get_groups_by_homework_id(
        cls, homework_id: int, session: AsyncSession = None
    ) -> List[GroupSchema]:
        stmt = (
            select(GroupsModel)
            .join(
                HomeworkGroupsModel,
                HomeworkGroupsModel.group_id == GroupsModel.group_id,
            )
            .where(HomeworkGroupsModel.homework_id == homework_id)
            .order_by(GroupsModel.group_id.asc())
        )
        res = await session.execute(stmt)
        models = res.unique().scalars().all()
        return [GroupSchema.model_validate(m) for m in models]

    @classmethod
    @with_session
    async def set_groups_for_homework(
        cls,
        *,
        homework_id: int,
        group_ids: list[int],
        session: AsyncSession = None,
    ) -> None:
        # удаляем старые привязки
        await cls.homework_groups_repository.delete(
            where={HomeworkGroupsModel.homework_id: homework_id},
            session=session,
        )
        # создаём новые
        for gid in group_ids:
            await cls.homework_groups_repository.create(
                HomeworkGroupCreateSchema(homework_id=homework_id, group_id=int(gid)),
                session=session,
            )
