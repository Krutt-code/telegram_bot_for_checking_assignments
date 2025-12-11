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

    @with_session
    async def create(
        self, schema: HomeworkCreateSchema, session: AsyncSession = None
    ) -> int:
        return await self.homeworks_repository.create(schema, session=session)

    @with_session
    async def get_by_id(
        self, homework_id: int, session: AsyncSession = None
    ) -> Optional[HomeworkSchema]:
        return await self.homeworks_repository.get_by_id(
            homework_id, session=session, load_relationships=["teacher"]
        )

    @with_session
    async def delete_by_id(
        self, homework_id: int, session: AsyncSession = None
    ) -> bool:
        return await self.homeworks_repository.delete_by_id(
            homework_id, session=session
        )
