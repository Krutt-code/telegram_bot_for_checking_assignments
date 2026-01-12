from typing import Dict, List, Union

from src.bot.keyboards.paginated_list import paginated_list_inline
from src.bot.lexicon.command_texts import COMMAND_DESCRIPTIONS_RU
from src.bot.lexicon.texts import TextsRU
from src.core.enums import CommandsEnum, InlineKeyboardTypeEnum, ReplyKeyboardTypeEnum
from src.core.schemas import StudentGroupExitCallbackSchema

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
    ],
    ReplyKeyboardTypeEnum.TEACHER_GROUPS: [
        [COMMAND_DESCRIPTIONS_RU[CommandsEnum.TEACHER_GROUP_CREATE]],
    ],
    ReplyKeyboardTypeEnum.TEACHER_HOMEWORKS: [
        [COMMAND_DESCRIPTIONS_RU[CommandsEnum.TEACHER_HOMEWORK_CREATE]],
    ],
    ReplyKeyboardTypeEnum.TEACHER_GROUP_VIEW: [
        [
            COMMAND_DESCRIPTIONS_RU[CommandsEnum.TEACHER_GROUP_EDIT],
            COMMAND_DESCRIPTIONS_RU[CommandsEnum.TEACHER_GROUP_DELETE],
        ],
        [COMMAND_DESCRIPTIONS_RU[CommandsEnum.TEACHER_GROUP_GET_LINK]],
    ],
    ReplyKeyboardTypeEnum.TEACHER_GRADING_COMMENT: [
        [TextsRU.TEACHER_GRADING_COMMENT_SKIP],
    ],
    # TODO: Реализовать меню заданий и групп преподователя
}

INLINE_KEYBOARDS: Dict[
    InlineKeyboardTypeEnum, Union[List[List[Dict[str, str]]], callable]
] = {
    InlineKeyboardTypeEnum.TEACHER_GROUPS_REVIEW: (paginated_list_inline),
    InlineKeyboardTypeEnum.TEACHER_GROUP_STUDENTS_REVIEW: (paginated_list_inline),
    InlineKeyboardTypeEnum.TEACHER_HOMEWORK_REVIEW: (paginated_list_inline),
    InlineKeyboardTypeEnum.TEACHER_HOMEWORK_EDIT_MENU: (paginated_list_inline),
    InlineKeyboardTypeEnum.TEACHER_HOMEWORK_GROUPS_SELECT: (paginated_list_inline),
    InlineKeyboardTypeEnum.TEACHER_HOMEWORK_CONFIRM: (paginated_list_inline),
    InlineKeyboardTypeEnum.TEACHER_GRADING_CHECK: (paginated_list_inline),
    InlineKeyboardTypeEnum.TEACHER_GRADING_REVIEWED: (paginated_list_inline),
    InlineKeyboardTypeEnum.STUDENT_HOMEWORK_REVIEW: (paginated_list_inline),
    InlineKeyboardTypeEnum.STUDENT_ANSWERS_REVIEW: (paginated_list_inline),
    InlineKeyboardTypeEnum.STUDENT_GROUP_EXIT: [
        [
            {
                "text": TextsRU.STUDENT_GROUP_EXIT,
                "callback_data": StudentGroupExitCallbackSchema(action="exit").pack(),
            }
        ]
    ],
}
