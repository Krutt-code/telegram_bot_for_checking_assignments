from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.schemas import HomeworkCreateSchema, HomeworkSchema
from src.db.models import HomeworkGroupsModel, HomeworksModel, TeachersModel
from src.db.pagination import Page, paginate_select
from src.db.repositories import HomeworksRepository
from src.db.session import with_session


class HomeworksService:
    """
    Сервис для работы с заданиями.
    """

    homeworks_repository: HomeworksRepository = HomeworksRepository

    @classmethod
    @with_session
    async def create(
        cls, schema: HomeworkCreateSchema, session: AsyncSession = None
    ) -> int:
        return await cls.homeworks_repository.create(schema, session=session)

    @classmethod
    @with_session
    async def get_by_id(
        cls, homework_id: int, session: AsyncSession = None
    ) -> Optional[HomeworkSchema]:
        return await cls.homeworks_repository.get_by_id(
            homework_id, session=session, load_relationships=["teacher", "teacher.user"]
        )

    @classmethod
    @with_session
    async def delete_by_id(cls, homework_id: int, session: AsyncSession = None) -> bool:
        return await cls.homeworks_repository.delete_by_id(homework_id, session=session)

    @classmethod
    @with_session
    async def get_homeworks_page_by_group_id(
        cls,
        group_id: int,
        *,
        page: int = 1,
        per_page: int = 1,
        session: AsyncSession = None,
    ) -> Page[HomeworkSchema]:
        """
        Получить страницу заданий, доступных студенту по его группе.
        """
        stmt = (
            select(HomeworksModel)
            .join(
                HomeworkGroupsModel,
                HomeworkGroupsModel.homework_id == HomeworksModel.homework_id,
            )
            .where(HomeworkGroupsModel.group_id == group_id)
            .options(joinedload(HomeworksModel.teacher).joinedload(TeachersModel.user))
            .order_by(HomeworksModel.end_at.desc(), HomeworksModel.homework_id.desc())
        )

        count_stmt = (
            select(func.count())
            .select_from(HomeworkGroupsModel)
            .where(HomeworkGroupsModel.group_id == group_id)
        )

        page_models: Page = await paginate_select(
            session,
            stmt,
            page=page,
            per_page=per_page,
            count_stmt=count_stmt,
        )
        return page_models.map(HomeworkSchema.model_validate)
