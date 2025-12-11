from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.schemas import TelegramFileCreateSchema, TelegramFileSchema
from src.db.repositories import TelegramFilesRepository
from src.db.session import with_session


class TelegramFilesService:
    """
    Сервис для работы с файлами Telegram (telegram_files).
    """

    telegram_files_repository: TelegramFilesRepository = TelegramFilesRepository

    @with_session
    async def create(
        self, schema: TelegramFileCreateSchema, session: AsyncSession = None
    ) -> int:
        return await self.telegram_files_repository.create(schema, session=session)

    @with_session
    async def get_by_id(
        self, telegram_file_id: int, session: AsyncSession = None
    ) -> Optional[TelegramFileSchema]:
        return await self.telegram_files_repository.get_by_id(
            telegram_file_id, session=session, load_relationships=["owner_user"]
        )
