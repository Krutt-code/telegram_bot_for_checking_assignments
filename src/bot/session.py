from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Union

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.methods import AnswerCallbackQuery
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    ReplyMarkupUnion,
)

from src.bot.keyboards.factory import KeyboardFactory
from src.bot.logger import bot_logger
from src.bot.managers import StudentManager, TeacherManager
from src.bot.managers.base import BaseUserManager
from src.bot.navigation import NavigationManager
from src.core.enums import InlineKeyboardTypeEnum, ReplyKeyboardTypeEnum, UserRoleEnum
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
        state: Optional[FSMContext] = None,
    ) -> None:
        self.message: Message
        self._is_callback_query = False
        if isinstance(obj, Message):
            self.message = obj
        elif isinstance(obj, CallbackQuery):
            self.callback_query = obj
            self.message = self._get_fake_message(obj)
        else:
            raise TypeError("Неверный тип объекта для инициализации UserSession")

        self.bot: Bot = self.message.bot

        self.user_id = self.message.from_user.id
        self.chat_id = self.message.chat.id
        self.username = self.message.from_user.username or ""
        self.full_name = self.message.from_user.full_name or ""

        self.users_client = users_client
        self.admin_storage = admin_storage
        self.role_storage = role_storage
        self._state: Optional[FSMContext] = state

        self.logger = bot_logger.get_class_logger(self)

    def bind_state(self, state: Optional[FSMContext]) -> None:
        """
        Привязать FSMContext к сессии, чтобы `answer()` мог автоматически
        добавлять навигационные кнопки (Назад/Отмена).
        """
        self._state = state

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
            Union[
                ReplyKeyboardMarkup,
                InlineKeyboardMarkup,
                ReplyKeyboardTypeEnum,
                InlineKeyboardTypeEnum,
            ]
        ] = None,
        keyboard_data: Union[str, Dict[str, str]] = "",
    ) -> None:
        if isinstance(reply_markup, ReplyKeyboardTypeEnum):
            reply_markup = KeyboardFactory.get_reply(reply_markup)
        elif isinstance(reply_markup, InlineKeyboardTypeEnum):
            reply_markup = KeyboardFactory.get_inline(reply_markup, keyboard_data)
        await self.message.bot.edit_message_text(
            text=text,
            chat_id=self.chat_id,
            message_id=message_id,
            reply_markup=reply_markup,
        )

    async def answer(
        self,
        text: Optional[str] = None,
        *,
        reply_markup: Optional[
            Union[ReplyMarkupUnion, ReplyKeyboardTypeEnum, InlineKeyboardTypeEnum]
        ] = None,
        keyboard_data: Union[str, Dict[str, str]] = "",
        reply_to_message_id: Optional[int] = None,
        include_back: Optional[bool] = None,
        include_cancel: Optional[bool] = None,
    ) -> List[int]:
        """
        Отправляет сообщение и возвращает список id сообщений.

        Args:
            text: Текст сообщения
            reply_markup: Клавиатура для отображения
            reply_to_message_id: ID сообщения для ответа
            include_back: Добавить кнопку "Назад" (None = авто по навигации)
            include_cancel: Добавить кнопку "Отмена" (None = авто по навигации)
        """

        # --- Авто-навигация ---
        # Правило:
        # - если есть cancel_target -> всегда показываем "Отмена"
        # - иначе, если в истории >= 2 шагов -> показываем "Назад"
        if (include_back is None or include_cancel is None) and self._state is not None:
            nav = NavigationManager(self._state)
            cancel_target = await nav.get_cancel_target()
            if cancel_target is not None:
                auto_cancel = True
                auto_back = False
            else:
                history = await nav.get_history()
                auto_cancel = False
                auto_back = len(history) >= 2

            if include_cancel is None:
                include_cancel = auto_cancel
            if include_back is None:
                include_back = auto_back

        include_back = bool(include_back)
        include_cancel = bool(include_cancel)

        if isinstance(reply_markup, ReplyKeyboardTypeEnum):
            self.logger.debug(f"Отправка reply-клавиатуры: {reply_markup}")
            reply_markup = KeyboardFactory.get_reply(
                reply_markup, include_back=include_back, include_cancel=include_cancel
            )
        elif isinstance(reply_markup, InlineKeyboardTypeEnum):
            reply_markup = KeyboardFactory.get_inline(reply_markup, keyboard_data)
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

    async def answer_callback_query(
        self,
        text: Optional[str] = None,
        show_alert: Optional[bool] = None,
        url: Optional[str] = None,
        cache_time: Optional[int] = None,
    ) -> AnswerCallbackQuery:
        return await self.callback_query.answer(
            text=text, show_alert=show_alert, url=url, cache_time=cache_time
        )

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
