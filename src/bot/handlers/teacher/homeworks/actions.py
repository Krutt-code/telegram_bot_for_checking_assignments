from __future__ import annotations

import time
from datetime import datetime

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.bot.filters.callback import CallbackFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.session import UserSession
from src.core.enums import InlineKeyboardTypeEnum
from src.core.schemas import (
    InlineButtonSchema,
    PaginatedListKeyboardSchema,
    TeacherHomeworkCallbackSchema,
)
from src.db.services import HomeworksService

teacher_homework_actions_router = Router()

_PENDING_TTL_SECONDS = 30
_PENDING_KEY = "pending_teacher_homework_delete"


def _edit_menu_keyboard(homework_id: int) -> dict:
    return PaginatedListKeyboardSchema(
        items=[],
        extra_buttons=[
            InlineButtonSchema(
                text=TextsRU.TEACHER_HOMEWORK_EDIT_TITLE,
                callback_data=TeacherHomeworkCallbackSchema(
                    action="edit_title", homework_id=homework_id
                ).pack(),
            ),
            InlineButtonSchema(
                text=TextsRU.TEACHER_HOMEWORK_EDIT_TEXT,
                callback_data=TeacherHomeworkCallbackSchema(
                    action="edit_text", homework_id=homework_id
                ).pack(),
            ),
            InlineButtonSchema(
                text=TextsRU.TEACHER_HOMEWORK_EDIT_FILES,
                callback_data=TeacherHomeworkCallbackSchema(
                    action="edit_files", homework_id=homework_id
                ).pack(),
            ),
            InlineButtonSchema(
                text=TextsRU.TEACHER_HOMEWORK_EDIT_GROUPS,
                callback_data=TeacherHomeworkCallbackSchema(
                    action="edit_groups", homework_id=homework_id
                ).pack(),
            ),
            InlineButtonSchema(
                text=TextsRU.TEACHER_HOMEWORK_EDIT_BACK,
                callback_data=TeacherHomeworkCallbackSchema(
                    action="back", homework_id=homework_id
                ).pack(),
            ),
        ],
    ).model_dump()


def _review_keyboard_with_pagination(
    *, homework_id: int, page: int, total_pages: int
) -> dict:
    return PaginatedListKeyboardSchema(
        items=[],
        extra_buttons=[
            InlineButtonSchema(
                text=TextsRU.TEACHER_HOMEWORK_EDIT_BUTTON,
                callback_data=TeacherHomeworkCallbackSchema(
                    action="edit_menu", homework_id=homework_id
                ).pack(),
            ),
            InlineButtonSchema(
                text=TextsRU.TEACHER_HOMEWORK_DELETE_BUTTON,
                callback_data=TeacherHomeworkCallbackSchema(
                    action="delete", homework_id=homework_id
                ).pack(),
            ),
        ],
        pagination={
            "key": "teacher_homeworks",
            "page": page,
            "total_pages": total_pages,
            "hide_if_single_page": True,
        },
    ).model_dump()


@teacher_homework_actions_router.callback_query(
    CallbackFilter(TeacherHomeworkCallbackSchema, action="edit_menu")
)
async def teacher_homework_edit_menu_handler(
    _: CallbackQuery,
    session: UserSession,
    callback_data: TeacherHomeworkCallbackSchema,
) -> None:
    await session.answer_callback_query()
    await session.edit_message(
        session.message.text or "",
        message_id=session.message.message_id,
        reply_markup=InlineKeyboardTypeEnum.TEACHER_HOMEWORK_EDIT_MENU,
        keyboard_data=_edit_menu_keyboard(callback_data.homework_id),
    )


@teacher_homework_actions_router.callback_query(
    CallbackFilter(TeacherHomeworkCallbackSchema, action="back")
)
async def teacher_homework_back_from_edit_menu_handler(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherHomeworkCallbackSchema,
) -> None:
    await session.answer_callback_query()
    page = int(await state.get_value("teacher_homeworks_current_page", 1) or 1)
    total_pages = int(await state.get_value("teacher_homeworks_total_pages", 1) or 1)
    await session.edit_message(
        session.message.text or "",
        message_id=session.message.message_id,
        reply_markup=InlineKeyboardTypeEnum.TEACHER_HOMEWORK_REVIEW,
        keyboard_data=_review_keyboard_with_pagination(
            homework_id=callback_data.homework_id, page=page, total_pages=total_pages
        ),
    )


@teacher_homework_actions_router.callback_query(
    CallbackFilter(TeacherHomeworkCallbackSchema, action="delete")
)
async def teacher_homework_delete_double_click_handler(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherHomeworkCallbackSchema,
) -> None:
    """
    Double click удаление через alert + TTL.
    """
    now = int(time.time())
    pending = await state.get_value(_PENDING_KEY, None)

    if (
        not isinstance(pending, dict)
        or pending.get("expires_at", 0) < now
        or pending.get("homework_id") != callback_data.homework_id
    ):
        await state.update_data(
            {
                _PENDING_KEY: {
                    "homework_id": callback_data.homework_id,
                    "expires_at": now + _PENDING_TTL_SECONDS,
                }
            }
        )
        await session.answer_callback_query(
            TextsRU.TEACHER_HOMEWORK_DELETE_CONFIRM_ALERT, show_alert=True
        )
        return

    await state.update_data({_PENDING_KEY: None})

    # безопасность: если дедлайн прошёл — удалить всё равно можно, это действие преподавателя
    ok = await HomeworksService.delete_by_id(callback_data.homework_id)
    if not ok:
        await session.answer_callback_query(TextsRU.TRY_AGAIN, show_alert=True)
        return

    await session.answer_callback_query(
        TextsRU.TEACHER_HOMEWORK_DELETE_SUCCESS_ALERT, show_alert=True
    )
    await session.edit_message(
        TextsRU.TEACHER_HOMEWORK_DELETED.format(
            deleted_at=datetime.now().strftime("%d.%m.%Y %H:%M")
        ),
        message_id=session.message.message_id,
        reply_markup=None,
    )
