from typing import Dict, List, Union

from src.bot.lexicon.command_texts import COMMAND_DESCRIPTIONS_RU
from src.core.enums import CommandsEnum, InlineKeyboardTypeEnum, ReplyKeyboardTypeEnum

# Используем текст как значение кнопки
REPLY_KEYBOARDS: Dict[ReplyKeyboardTypeEnum, List[List[str]]] = {
    # Выбор роли
    ReplyKeyboardTypeEnum.ROLE: [
        [
            COMMAND_DESCRIPTIONS_RU[CommandsEnum.STUDENT_ROLE],
            COMMAND_DESCRIPTIONS_RU[CommandsEnum.TEACHER_ROLE],
        ],
    ],
    ReplyKeyboardTypeEnum.GENERAL_SETTINGS: [
        [COMMAND_DESCRIPTIONS_RU[CommandsEnum.FULL_NAME_PANEL]],
    ],
    ReplyKeyboardTypeEnum.ADMIN: [
        [
            COMMAND_DESCRIPTIONS_RU[CommandsEnum.STUDENT_ROLE],
            COMMAND_DESCRIPTIONS_RU[CommandsEnum.TEACHER_ROLE],
        ],
        [COMMAND_DESCRIPTIONS_RU[CommandsEnum.ADMIN_PANEL]],
    ],
    ReplyKeyboardTypeEnum.FULL_NAME_PANEL: [
        [COMMAND_DESCRIPTIONS_RU[CommandsEnum.SET_FULL_NAME]],
        [COMMAND_DESCRIPTIONS_RU[CommandsEnum.CANCEL]],
    ],
    ReplyKeyboardTypeEnum.ADMIN_PANEL: [
        [COMMAND_DESCRIPTIONS_RU[CommandsEnum.ADMIN_STUDENTS]],
        [COMMAND_DESCRIPTIONS_RU[CommandsEnum.ADMIN_GROUPS]],
        [COMMAND_DESCRIPTIONS_RU[CommandsEnum.ADMIN_TEACHERS]],
    ],  # TODO: Реализовать меню для админа
    ReplyKeyboardTypeEnum.STUDENT: [
        [
            COMMAND_DESCRIPTIONS_RU[CommandsEnum.STUDENT_HOMEWORKS],
            COMMAND_DESCRIPTIONS_RU[CommandsEnum.STUDENT_ANSWERS],
        ],
        [
            COMMAND_DESCRIPTIONS_RU[CommandsEnum.STUDENT_GROUP],
        ],
    ],
    ReplyKeyboardTypeEnum.TEACHER: [
        [
            COMMAND_DESCRIPTIONS_RU[CommandsEnum.TEACHER_HOMEWORKS],
            COMMAND_DESCRIPTIONS_RU[CommandsEnum.TEACHER_GROUPS],
        ],
    ],  # TODO: Реализовать меню заданий и групп преподователя
}

INLINE_KEYBOARDS: Dict[
    InlineKeyboardTypeEnum, Union[List[List[Dict[str, str]]], callable]
] = {}
