from __future__ import annotations

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.schemas import HomeworkFileSchema
from src.db.models import HomeworkFilesModel
from src.db.repositories import HomeworkFilesRepository
from src.db.session import with_session


class HomeworkFilesService:
    """
    Сервис для работы с файлами заданий (homework_files).
    """

    homework_files_repository: HomeworkFilesRepository = HomeworkFilesRepository

    @classmethod
    @with_session
    async def get_files_by_homework_id(
        cls, homework_id: int, session: AsyncSession = None
    ) -> List[HomeworkFileSchema]:
        return await cls.homework_files_repository.get_all_where(
            where={HomeworkFilesModel.homework_id: homework_id},
            load_relationships=["telegram_file"],
            session=session,
        )
