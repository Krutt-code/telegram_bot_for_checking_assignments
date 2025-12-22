from __future__ import annotations

from typing import Iterable, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.schemas import (
    HomeworkFileCreateSchema,
    HomeworkFileSchema,
    TelegramFileCreateSchema,
)
from src.db.models import HomeworkFilesModel
from src.db.repositories import HomeworkFilesRepository
from src.db.services.telegram_files import TelegramFilesService
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
            load_relationships=["telegram_file", "telegram_file.owner_user"],
            session=session,
        )

    @classmethod
    @with_session
    async def delete_by_homework_id(
        cls, homework_id: int, session: AsyncSession = None
    ) -> int:
        return await cls.homework_files_repository.delete(
            where={HomeworkFilesModel.homework_id: homework_id},
            session=session,
        )

    @classmethod
    @with_session
    async def attach_telegram_files(
        cls,
        *,
        homework_id: int,
        telegram_files: Optional[Iterable[TelegramFileCreateSchema]] = None,
        session: AsyncSession = None,
    ) -> None:
        if not telegram_files:
            return
        for tf in telegram_files:
            telegram_file_id = await TelegramFilesService.create(tf, session=session)
            await cls.homework_files_repository.create(
                HomeworkFileCreateSchema(
                    homework_id=homework_id, telegram_file_id=telegram_file_id
                ),
                session=session,
            )
