"""
Отображаем список заданий для студента.

Вывод по 1 заданию с кнопкой начала работы над заданием. И пагинацией далее или назад(если есть).
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.filters import CommandFilter
from src.bot.filters.callback import CallbackFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.navigation import NavigationHelper
from src.bot.session import UserSession
from src.core.enums import CommandsEnum, HomeworkMediaTypeEnum, InlineKeyboardTypeEnum
from src.core.schemas import (
    InlineButtonSchema,
    PaginatedListKeyboardSchema,
    PaginationCallbackSchema,
    PaginationStateSchema,
    StudentHomeworkCallbackSchema,
)
from src.db.services import HomeworkFilesService, HomeworksService

homeworks_router = Router()


_PAGINATION_PREFIX = "student_homeworks:"
_PER_PAGE = 1
_STATE_PHOTO_MSG_IDS_KEY = "student_homeworks_photo_message_ids"


def _format_dt(dt: Optional[datetime]) -> str:
    if not dt:
        return ""
    try:
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return str(dt)


def _extract_group_id_from_key(key: str) -> Optional[int]:
    # ожидаем: "student_homeworks:<group_id>"
    try:
        prefix, raw_id = key.split(":", 1)
        if prefix != _PAGINATION_PREFIX.rstrip(":"):
            return None
        return int(raw_id)
    except Exception:
        return None


async def _delete_previous_photos(state: FSMContext, session: UserSession) -> None:
    data = await state.get_data()
    msg_ids = data.get(_STATE_PHOTO_MSG_IDS_KEY) or []
    if not isinstance(msg_ids, list) or not msg_ids:
        return
    for mid in msg_ids:
        try:
            await session.delete_message(int(mid))
        except Exception:
            # не критично (сообщение могло быть уже удалено)
            pass
    await state.update_data({_STATE_PHOTO_MSG_IDS_KEY: []})


async def _send_homework_photos(
    *,
    state: FSMContext,
    session: UserSession,
    homework_id: int,
) -> None:
    await _delete_previous_photos(state, session)

    files = await HomeworkFilesService.get_files_by_homework_id(homework_id)
    photo_ids: list[int] = []
    for f in files:
        tf = f.telegram_file
        if not tf or tf.file_type != HomeworkMediaTypeEnum.PHOTO.value:
            continue
        try:
            msg = await session.message.answer_photo(photo=tf.file_id)
            photo_ids.append(msg.message_id)
        except Exception:
            continue
    await state.update_data({_STATE_PHOTO_MSG_IDS_KEY: photo_ids})


def _build_homework_text(homework) -> str:
    start_at_line = ""
    if homework.start_at:
        start_at_line = TextsRU.STUDENT_HOMEWORK_START_AT_LINE.format(
            start_at=_format_dt(homework.start_at)
        )

    teacher_line = ""
    try:
        full_name = homework.teacher.user.real_full_name if homework.teacher else None
    except Exception:
        full_name = None
    if full_name:
        teacher_line = TextsRU.STUDENT_HOMEWORK_TEACHER_LINE.format(
            teacher_full_name=full_name
        )

    return TextsRU.STUDENT_HOMEWORK_VIEW.format(
        title=homework.title,
        text=homework.text,
        end_at=_format_dt(homework.end_at),
        start_at_line=start_at_line,
        teacher_line=teacher_line,
    )


def _build_homework_keyboard(
    *,
    group_id: int,
    page: int,
    total_pages: int,
    homework_id: int,
    allow_answer: bool,
):
    key = f"{_PAGINATION_PREFIX}{group_id}"
    extra_buttons = []
    if allow_answer:
        extra_buttons.append(
            InlineButtonSchema(
                text=TextsRU.STUDENT_HOMEWORK_ANSWER_BUTTON,
                callback_data=StudentHomeworkCallbackSchema(
                    action="answer", homework_id=homework_id
                ).pack(),
            )
        )
    return PaginatedListKeyboardSchema(
        items=[],
        extra_buttons=extra_buttons,
        pagination=PaginationStateSchema(key=key, page=page, total_pages=total_pages),
    ).model_dump()


@homeworks_router.message(CommandFilter(CommandsEnum.STUDENT_HOMEWORKS))
async def student_homeworks_review_handler(
    _: Message,
    state: FSMContext,
    session: UserSession,
) -> None:
    await NavigationHelper.register_navigation_step(
        state,
        CommandsEnum.STUDENT_HOMEWORKS,
        keyboard=None,
        text=TextsRU.SELECT_ACTION,
    )

    group = await session.student_manager().get_group()
    if not group:
        await session.answer(TextsRU.STUDENT_GROUP_NOT_FOUND)
        return

    page_data = await HomeworksService.get_homeworks_page_by_group_id(
        group.group_id, page=1, per_page=_PER_PAGE
    )
    if not page_data.items:
        await session.answer(TextsRU.STUDENT_HOMEWORKS_EMPTY)
        return

    hw = page_data.items[0]
    allow_answer = bool(hw.end_at and hw.end_at > datetime.now())
    await _send_homework_photos(
        state=state, session=session, homework_id=hw.homework_id
    )

    await session.answer(
        _build_homework_text(hw),
        reply_markup=InlineKeyboardTypeEnum.STUDENT_HOMEWORK_REVIEW,
        keyboard_data=_build_homework_keyboard(
            group_id=group.group_id,
            page=page_data.page,
            total_pages=page_data.total_pages,
            homework_id=hw.homework_id,
            allow_answer=allow_answer,
        ),
    )


@homeworks_router.callback_query(
    CallbackFilter(
        PaginationCallbackSchema,
        key=lambda k: isinstance(k, str) and k.startswith(_PAGINATION_PREFIX),
    )
)
async def student_homeworks_pagination_handler(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: PaginationCallbackSchema,
) -> None:
    await session.answer_callback_query()

    group_id = _extract_group_id_from_key(callback_data.key)
    if not group_id:
        await session.answer(TextsRU.TRY_AGAIN)
        return

    page_data = await HomeworksService.get_homeworks_page_by_group_id(
        group_id, page=callback_data.page, per_page=_PER_PAGE
    )
    if not page_data.items:
        await session.edit_message(
            TextsRU.STUDENT_HOMEWORKS_EMPTY,
            message_id=session.message.message_id,
            reply_markup=None,
        )
        await _delete_previous_photos(state, session)
        return

    hw = page_data.items[0]
    allow_answer = bool(hw.end_at and hw.end_at > datetime.now())
    await _send_homework_photos(
        state=state, session=session, homework_id=hw.homework_id
    )

    await session.edit_message(
        _build_homework_text(hw),
        message_id=session.message.message_id,
        reply_markup=InlineKeyboardTypeEnum.STUDENT_HOMEWORK_REVIEW,
        keyboard_data=_build_homework_keyboard(
            group_id=group_id,
            page=page_data.page,
            total_pages=page_data.total_pages,
            homework_id=hw.homework_id,
            allow_answer=allow_answer,
        ),
    )
