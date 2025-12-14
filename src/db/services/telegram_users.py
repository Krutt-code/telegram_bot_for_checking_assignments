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
            if (
                (schema.username and existing.username != schema.username)
                or (schema.full_name and existing.full_name != schema.full_name)
                or (
                    schema.real_full_name
                    and existing.real_full_name != schema.real_full_name
                )
            ):
                await cls.update(existing.user_id, schema, session=session)
            return existing.user_id
        return await cls.create(schema, session=session)

    @classmethod
    @with_session
    async def get_real_full_name(
        cls, user_id: int, session: AsyncSession = None
    ) -> Optional[str]:
        data = await cls.telegram_users_repository.get_by_id(user_id, session=session)
        if not data:
            return None
        return data.real_full_name

    @classmethod
    @with_session
    async def set_real_full_name(
        cls, user_id: int, real_full_name: str, session: AsyncSession = None
    ) -> None:
        if not real_full_name:
            return
        await cls.telegram_users_repository.update_values(
            where={"user_id": user_id},
            values={"real_full_name": real_full_name},
            session=session,
        )
