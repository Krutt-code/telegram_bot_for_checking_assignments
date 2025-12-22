from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.schemas import TelegramFileCreateSchema, TelegramFileSchema
from src.db.repositories import TelegramFilesRepository
from src.db.session import with_session


class TelegramFilesService:
    """
    Сервис для работы с файлами Telegram.
    """

    telegram_files_repository: TelegramFilesRepository = TelegramFilesRepository

    @classmethod
    @with_session
    async def create(
        cls, schema: TelegramFileCreateSchema, session: AsyncSession = None
    ) -> int:
        return await cls.telegram_files_repository.create(schema, session=session)

    @classmethod
    @with_session
    async def get_by_id(
        cls, telegram_file_id: int, session: AsyncSession = None
    ) -> Optional[TelegramFileSchema]:
        return await cls.telegram_files_repository.get_by_id(
            telegram_file_id, session=session, load_relationships=["owner_user"]
        )
