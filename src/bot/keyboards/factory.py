from typing import Dict, List, Optional, Union

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from src.bot.keyboards.keyboards import INLINE_KEYBOARDS, REPLY_KEYBOARDS
from src.bot.lexicon.command_texts import COMMAND_DESCRIPTIONS_RU
from src.core.enums import CommandsEnum, InlineKeyboardTypeEnum, ReplyKeyboardTypeEnum

# ----- Утилиты создания -----


def make_reply_markup(layout: List[List[str]]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=btn) for btn in row] for row in layout],
        resize_keyboard=True,
    )


def make_inline_markup(layout: List[List[Dict[str, str]]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(**btn) for btn in row] for row in layout]
    )


# ----- Фабрика -----


class KeyboardFactory:
    @staticmethod
    def get_navigation_only(
        *, include_back: bool = False, include_cancel: bool = False
    ) -> ReplyKeyboardMarkup:
        layout: List[List[str]] = []
        if include_back:
            layout.append([COMMAND_DESCRIPTIONS_RU[CommandsEnum.BACK]])
        if include_cancel:
            layout.append([COMMAND_DESCRIPTIONS_RU[CommandsEnum.CANCEL]])
        if not layout:
            raise ValueError("Невозможно создать навигационную клавиатуру без кнопок")
        return make_reply_markup(layout)

    @staticmethod
    def get_reply(
        name: Optional[ReplyKeyboardTypeEnum],
        *,
        include_back: bool = False,
        include_cancel: bool = False,
    ) -> ReplyKeyboardMarkup:
        layout = REPLY_KEYBOARDS.get(name)
        if not layout:
            raise ValueError(f"Неизвестный тип reply-клавиатуры: {name}")

        # Создаем копию layout, чтобы не модифицировать исходный
        layout = [row[:] for row in layout]

        # Добавляем кнопку "Назад" если нужно
        if include_back:
            layout.append([COMMAND_DESCRIPTIONS_RU[CommandsEnum.BACK]])

        # Добавляем кнопку "Отмена" если нужно
        if include_cancel:
            layout.append([COMMAND_DESCRIPTIONS_RU[CommandsEnum.CANCEL]])

        if not layout:
            return

        return make_reply_markup(layout)

    @staticmethod
    def get_inline(
        name: InlineKeyboardTypeEnum, callback_data: Union[str, Dict[str, str]] = ""
    ) -> InlineKeyboardMarkup:
        layout = INLINE_KEYBOARDS.get(name)
        if layout is None:
            raise ValueError(f"Неизвестный тип inline-клавиатуры: {name}")
        if callable(layout):
            return make_inline_markup(layout(callback_data))
        return make_inline_markup(layout)
