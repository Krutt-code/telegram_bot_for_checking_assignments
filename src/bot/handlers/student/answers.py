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
from src.core.enums import CommandsEnum, InlineKeyboardTypeEnum
from src.core.schemas import (
    PaginatedListKeyboardSchema,
    PaginationCallbackSchema,
    PaginationStateSchema,
)
from src.db.services import AnswersService, StudentsService

answers_router = Router()

_PAGINATION_KEY = "student_answers"
_PER_PAGE = 1


def _format_dt(dt: Optional[datetime]) -> str:
    if not dt:
        return ""
    try:
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return str(dt)


def _status_to_text(status: str) -> str:
    status = (status or "").lower()
    if status == "sent":
        return TextsRU.STUDENT_ANSWER_STATUS_SENT
    if status == "reviewed":
        return TextsRU.STUDENT_ANSWER_STATUS_REVIEWED
    if status == "rejected":
        return TextsRU.STUDENT_ANSWER_STATUS_REJECTED
    if status == "accepted":
        return TextsRU.STUDENT_ANSWER_STATUS_ACCEPTED
    return status or TextsRU.STUDENT_ANSWER_STATUS_SENT


def _build_answer_text(answer) -> str:
    homework_title = answer.homework.title if answer.homework else ""
    grade_line = f"<b>Оценка:</b> {answer.grade}\n" if answer.grade is not None else ""
    comment_line = (
        f"<b>Комментарий:</b> {answer.teacher_comment}\n"
        if answer.teacher_comment
        else ""
    )
    return TextsRU.STUDENT_ANSWER_VIEW.format(
        homework_title=homework_title,
        sent_at=_format_dt(answer.sent_at),
        status=_status_to_text(getattr(answer.status, "value", str(answer.status))),
        grade_line=grade_line,
        comment_line=comment_line,
        student_answer=answer.student_answer or "",
    )


def _build_keyboard(*, page: int, total_pages: int) -> dict:
    return PaginatedListKeyboardSchema(
        items=[],
        extra_buttons=[],
        pagination=PaginationStateSchema(
            key=_PAGINATION_KEY,
            page=page,
            total_pages=total_pages,
        ),
    ).model_dump()


@answers_router.message(CommandFilter(CommandsEnum.STUDENT_ANSWERS))
async def student_answers_review_handler(
    _: Message,
    state: FSMContext,
    session: UserSession,
) -> None:
    await NavigationHelper.register_navigation_step(
        state,
        CommandsEnum.STUDENT_ANSWERS,
        keyboard=None,
        text=TextsRU.SELECT_ACTION,
    )

    student = await StudentsService.get_by_user_id(session.user_id)
    if not student:
        await session.answer(TextsRU.TRY_AGAIN)
        return

    page_data = await AnswersService.get_answers_page_by_student_id(
        student.student_id, page=1, per_page=_PER_PAGE
    )
    if not page_data.items:
        await session.answer(TextsRU.STUDENT_ANSWERS_EMPTY)
        return

    ans = page_data.items[0]
    await session.answer(
        _build_answer_text(ans),
        reply_markup=InlineKeyboardTypeEnum.STUDENT_ANSWERS_REVIEW,
        keyboard_data=_build_keyboard(
            page=page_data.page, total_pages=page_data.total_pages
        ),
    )


@answers_router.callback_query(
    CallbackFilter(PaginationCallbackSchema, key=_PAGINATION_KEY)
)
async def student_answers_pagination_handler(
    _: CallbackQuery,
    session: UserSession,
    callback_data: PaginationCallbackSchema,
) -> None:
    await session.answer_callback_query()

    student = await StudentsService.get_by_user_id(session.user_id)
    if not student:
        await session.answer(TextsRU.TRY_AGAIN)
        return

    page_data = await AnswersService.get_answers_page_by_student_id(
        student.student_id, page=callback_data.page, per_page=_PER_PAGE
    )
    if not page_data.items:
        await session.edit_message(
            TextsRU.STUDENT_ANSWERS_EMPTY,
            message_id=session.message.message_id,
            reply_markup=None,
        )
        return

    ans = page_data.items[0]
    await session.edit_message(
        _build_answer_text(ans),
        message_id=session.message.message_id,
        reply_markup=InlineKeyboardTypeEnum.STUDENT_ANSWERS_REVIEW,
        keyboard_data=_build_keyboard(
            page=page_data.page, total_pages=page_data.total_pages
        ),
    )

