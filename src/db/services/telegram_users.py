from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.schemas import TelegramUserCreateSchema, TelegramUserSchema
from src.db.repositories import TelegramUsersRepository
from src.db.session import with_session


class TelegramUsersService:
    """
    Сервис для работы с пользователями Telegram
    """

    telegram_users_repository: TelegramUsersRepository = TelegramUsersRepository

    @with_session
    async def create(
        self, schema: TelegramUserCreateSchema, session: AsyncSession = None
    ) -> int:
        return await self.telegram_users_repository.create(schema, session=session)

    @with_session
    async def get_by_id(
        self, user_id: int, session: AsyncSession = None
    ) -> Optional[TelegramUserSchema]:
        return await self.telegram_users_repository.get_by_id(user_id, session=session)

    @with_session
    async def get_or_create(
        self, schema: TelegramUserCreateSchema, session: AsyncSession = None
    ) -> int:
        """
        Получить пользователя по user_id или создать, если его ещё нет.
        Возвращает user_id.
        """
        existing = await self.get_by_id(schema.user_id, session=session)
        if existing:
            return existing.user_id
        return await self.create(schema, session=session)

    @with_session
    async def update(
        self, user_id: int, schema: TelegramUserSchema, session: AsyncSession = None
    ) -> None:
        return await self.telegram_users_repository.update_by_id(
            user_id, schema, session=session
        )

    @with_session
    async def delete(self, user_id: int, session: AsyncSession = None) -> None:
        return await self.telegram_users_repository.delete_by_id(
            user_id, session=session
        )
