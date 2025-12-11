from __future__ import annotations

from typing import Optional

from aiogram.types import CallbackQuery, Message

from src.bot import bot_logger


class UserSession:
    """
    Сессия пользователя на уровне Telegram-бота.

    Это объект, который объединяет данные апдейта (Message/CallbackQuery)
    и удобные поля (user_id, chat_id и т.п.).
    """

    def __init__(
        self,
        message: Optional[Message] = None,
        callback_query: Optional[CallbackQuery] = None,
    ) -> None:
        self.message = self.get_aiogram_message(message, callback_query)

        self.user_id = self.message.from_user.id
        self.chat_id = self.message.chat.id
        self.username = self.message.from_user.username or ""
        self.full_name = self.message.from_user.full_name or ""

        self._logger = bot_logger.get_class_logger(self)

        self._stage_storage = ""

    @staticmethod
    def get_fake_message(callback_query: CallbackQuery) -> Message:
        """Поддельный объект Message от aiogram на основе callback_query."""
        msg = Message.model_construct(
            message_id=callback_query.message.message_id,
            chat=callback_query.message.chat,
            date=callback_query.message.date,
            from_user=callback_query.from_user,
            text=callback_query.message.text,
        )
        msg._bot = callback_query.bot
        return msg

    def get_aiogram_message(
        self,
        message: Optional[Message] = None,
        callback_query: Optional[CallbackQuery] = None,
    ) -> Message:
        if message:
            self.message = message
        elif callback_query:
            self.message = self.get_fake_message(callback_query)
        else:
            raise TypeError("Нет аргументов для инициализации UserSession")
        return self.message
