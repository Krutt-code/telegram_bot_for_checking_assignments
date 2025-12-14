from __future__ import annotations

import hashlib
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Optional

from src.core.schemas import TelegramUserCreateSchema
from src.db.services import TelegramUsersService

if TYPE_CHECKING:
    from src.bot.session import UserSession


def ensure_telegram_user_decorator(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(self: "BaseUserManager", *args: Any, **kwargs: Any) -> Any:
        if not hasattr(self, "ensure_telegram_user"):
            raise AttributeError("ensure_telegram_user method not found")
        await self.ensure_telegram_user()
        return await func(self, *args, **kwargs)

    return wrapper


class BaseUserManager:
    """
    Базовый менеджер пользователя.

    Дает доступ к удобным методам для работы с пользователем.
    """

    def __init__(
        self,
        user_session: "UserSession",
    ) -> None:
        self.session = user_session
        self.telegram_users = TelegramUsersService()

    async def ensure_telegram_user(self) -> int:
        """
        Гарантирует, что telegram_user существует в БД.
        Возвращает user_id.
        """
        cache = self.session.users_client

        # Формируем хэш профиля, чтобы не обращаться в БД, если данные не менялись
        profile_hash = hashlib.sha1(
            f"{self.session.username}|{self.session.full_name}|{None}".encode()
        ).hexdigest()

        exists_cached, cached_hash = await cache.get_entry(self.session.user_id)
        if exists_cached and cached_hash == profile_hash:
            return self.session.user_id

        await self.telegram_users.get_or_create(
            TelegramUserCreateSchema(
                user_id=self.session.user_id,
                username=self.session.username,
                full_name=self.session.full_name,
                real_full_name=None,
            )
        )

        await cache.set_entry(
            self.session.user_id,
            profile_hash=profile_hash,
            ttl_seconds=3600,
        )

        return self.session.user_id

    @ensure_telegram_user_decorator
    async def has_real_full_name(self) -> bool:
        """
        Проверяет наличие real_full_name, отдавая приоритет кэшу.
        """
        cache = self.session.users_client
        cached_exists = await cache.get_full_name_exists(self.session.user_id)
        if cached_exists is not None:
            return cached_exists

        full_name = await self.telegram_users.get_real_full_name(self.session.user_id)
        exists = bool(full_name)
        await cache.set_full_name_exists(self.session.user_id, exists, ttl_seconds=3600)
        return exists

    @ensure_telegram_user_decorator
    async def get_real_full_name(self) -> Optional[str]:
        """
        Возвращает real_full_name. Обновляет кэш флага существования.
        """
        full_name = await self.telegram_users.get_real_full_name(self.session.user_id)
        await self.session.users_client.set_full_name_exists(
            self.session.user_id, bool(full_name), ttl_seconds=3600
        )
        return full_name

    async def set_real_full_name(self, real_full_name: str) -> None:
        """
        Устанавливает реальное полное имя пользователя.
        """
        await self.telegram_users.set_real_full_name(
            self.session.user_id, real_full_name
        )
        # ФИО нельзя удалить так что можем навесить флаг на долгое время
        await self.session.users_client.set_full_name_exists(
            self.session.user_id, True, ttl_seconds=86400
        )
