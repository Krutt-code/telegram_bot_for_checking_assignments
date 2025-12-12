from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.schemas import HomeworkCreateSchema, HomeworkSchema
from src.db.repositories import HomeworksRepository
from src.db.session import with_session


class HomeworksService:
    """
    Сервис для работы с заданиями (homeworks).
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
            homework_id, session=session, load_relationships=["teacher"]
        )

    @classmethod
    @with_session
    async def delete_by_id(cls, homework_id: int, session: AsyncSession = None) -> bool:
        return await cls.homeworks_repository.delete_by_id(homework_id, session=session)
