from __future__ import annotations

from typing import Optional

from aiogram.types import CallbackQuery, Message

from src.bot.session import UserSession
from src.db.services import TelegramUsersService


class BaseUserManager:
    """
    Базовый менеджер пользователя.

    Идея: менеджер знает Telegram-сессию пользователя и даёт “юзер-френдли” методы,
    которые далее вызывают db-сервисы / db-use-case’ы.
    """

    def __init__(
        self,
        message: Optional[Message] = None,
        callback_query: Optional[CallbackQuery] = None,
    ) -> None:
        self.session = UserSession(message=message, callback_query=callback_query)
        self.telegram_users = TelegramUsersService()

    async def ensure_telegram_user(self) -> int:
        """
        Гарантирует, что telegram_user существует в БД.
        Возвращает user_id.
        """
        from src.core.schemas import TelegramUserCreateSchema

        return await self.telegram_users.get_or_create(
            TelegramUserCreateSchema(
                user_id=self.session.user_id,
                username=self.session.username,
                full_name=self.session.full_name,
                real_full_name=None,
            )
        )
