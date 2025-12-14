from __future__ import annotations

from typing import Iterable, List, Optional, Union

from aiogram.types import CallbackQuery, Message, ReplyKeyboardMarkup

from src.bot.keyboards.factory import KeyboardFactory
from src.bot.logger import bot_logger
from src.bot.managers import StudentManager, TeacherManager
from src.bot.managers.base import BaseUserManager
from src.core.enums import ReplyKeyboardTypeEnum, UserRoleEnum
from src.redis import RedisTelegramUsersClient
from src.services import AdminStorage, RoleStorage
from src.utils.telegram_messages import split_telegram_html_message


class UserSession:
    """
    Сессия пользователя на уровне Telegram-бота.

    Это объект, который объединяет данные апдейта (Message/CallbackQuery)
    и удобные поля (user_id, chat_id и т.п.).
    """

    def __init__(
        self,
        obj: Union[Message, CallbackQuery],
        *,
        users_client: RedisTelegramUsersClient,
        admin_storage: AdminStorage,
        role_storage: RoleStorage,
    ) -> None:
        self.message: Message
        if isinstance(obj, Message):
            self.message = obj
        elif isinstance(obj, CallbackQuery):
            self.message = self._get_fake_message(obj)
        else:
            raise TypeError("Неверный тип объекта для инициализации UserSession")

        self.user_id = self.message.from_user.id
        self.chat_id = self.message.chat.id
        self.username = self.message.from_user.username or ""
        self.full_name = self.message.from_user.full_name or ""

        self.users_client = users_client
        self.admin_storage = admin_storage
        self.role_storage = role_storage

        self.logger = bot_logger.get_class_logger(self)

    async def is_admin(self) -> bool:
        return await self.admin_storage.is_admin(self.user_id)

    async def get_role(self) -> Optional[UserRoleEnum]:
        return await self.role_storage.get_role(self.user_id)

    async def set_role(self, role: UserRoleEnum) -> None:
        await self.role_storage.set_role(self.user_id, role)

    async def clear_role(self) -> None:
        await self.role_storage.clear_role(self.user_id)

    def user_manager(self) -> BaseUserManager:
        return BaseUserManager(self)

    def student_manager(self) -> StudentManager:
        return StudentManager(self)

    def teacher_manager(self) -> TeacherManager:
        return TeacherManager(self)

    async def edit_message(
        self,
        text: str,
        message_id: int,
        reply_markup: Optional[
            Union[ReplyKeyboardMarkup, ReplyKeyboardTypeEnum]
        ] = None,
    ) -> None:
        if isinstance(reply_markup, ReplyKeyboardTypeEnum):
            reply_markup = KeyboardFactory.get_reply(reply_markup)
        await self.message.bot.edit_message_text(
            text=text,
            chat_id=self.chat_id,
            message_id=message_id,
            reply_markup=reply_markup,
        )

    async def answer(
        self,
        text: str,
        *,
        reply_markup: Optional[
            Union[ReplyKeyboardMarkup, ReplyKeyboardTypeEnum]
        ] = None,
        reply_to_message_id: Optional[int] = None,
        include_back: bool = False,
        include_cancel: bool = False,
    ) -> List[int]:
        """
        Отправляет сообщение и возвращает список id сообщений.

        Args:
            text: Текст сообщения
            reply_markup: Клавиатура для отображения
            reply_to_message_id: ID сообщения для ответа
            include_back: Добавить кнопку "Назад"
            include_cancel: Добавить кнопку "Отмена"
        """
        if isinstance(reply_markup, ReplyKeyboardTypeEnum):
            self.logger.debug(f"Отправка reply-клавиатуры: {reply_markup}")
            reply_markup = KeyboardFactory.get_reply(
                reply_markup, include_back=include_back, include_cancel=include_cancel
            )
        elif reply_markup is None and (include_back or include_cancel):
            reply_markup = KeyboardFactory.get_navigation_only(
                include_back=include_back,
                include_cancel=include_cancel,
            )
        parts = split_telegram_html_message(text)
        message_ids = []
        for part in parts:
            self.logger.debug(f"Отправка части сообщения: {part}")
            message = await self.message.answer(
                text=part,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
            )
            message_ids.append(message.message_id)
        return message_ids

    async def delete_message(self, message_id: int) -> None:
        await self.message.bot.delete_message(
            chat_id=self.chat_id,
            message_id=message_id,
        )

    async def delete_messages(self, message_ids: Iterable[int]) -> None:
        for message_id in message_ids:
            await self.delete_message(message_id)

    @staticmethod
    def _get_fake_message(callback_query: CallbackQuery) -> Message:
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
