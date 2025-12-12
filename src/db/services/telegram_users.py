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

    @classmethod
    @with_session
    async def create(
        cls, schema: TelegramUserCreateSchema, session: AsyncSession = None
    ) -> int:
        return await cls.telegram_users_repository.create(schema, session=session)

    @classmethod
    @with_session
    async def get_by_id(
        cls, user_id: int, session: AsyncSession = None
    ) -> Optional[TelegramUserSchema]:
        return await cls.telegram_users_repository.get_by_id(user_id, session=session)

    @classmethod
    @with_session
    async def get_or_create(
        cls, schema: TelegramUserCreateSchema, session: AsyncSession = None
    ) -> int:
        """
        Получить пользователя по user_id или создать, если его ещё нет.
        Возвращает user_id.
        """
        existing = await cls.get_by_id(schema.user_id, session=session)
        if existing:
            return existing.user_id
        return await cls.create(schema, session=session)

    @classmethod
    @with_session
    async def update(
        cls, user_id: int, schema: TelegramUserSchema, session: AsyncSession = None
    ) -> None:
        return await cls.telegram_users_repository.update_by_id(
            user_id, schema, session=session
        )

    @classmethod
    @with_session
    async def delete(cls, user_id: int, session: AsyncSession = None) -> None:
        return await cls.telegram_users_repository.delete_by_id(
            user_id, session=session
        )
