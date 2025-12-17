from __future__ import annotations

import time

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.bot.filters.callback import CallbackFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.session import UserSession
from src.core.schemas import TeacherGroupStudentCallbackSchema

teacher_group_students_router = Router()

_PENDING_TTL_SECONDS = 30
_PENDING_KEY = "pending_student_remove"


@teacher_group_students_router.callback_query(
    CallbackFilter(TeacherGroupStudentCallbackSchema, action="rm")
)
async def teacher_group_student_remove_handler(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherGroupStudentCallbackSchema,
) -> None:
    """
    2-step подтверждение через alert:
    - 1-й клик: показываем alert и запоминаем pending в FSM на короткое время
    - 2-й клик (тот же студент) в пределах TTL: выполняем удаление и перерисовываем список
    """
    now = int(time.time())
    pending = await state.get_value(_PENDING_KEY, None)

    # если pending просрочен или другой студент/группа — ставим новый pending
    if (
        not isinstance(pending, dict)
        or pending.get("expires_at", 0) < now
        or pending.get("group_id") != callback_data.group_id
        or pending.get("student_id") != callback_data.student_id
    ):
        await state.update_data(
            {
                _PENDING_KEY: {
                    "group_id": callback_data.group_id,
                    "student_id": callback_data.student_id,
                    "page": callback_data.page,
                    "expires_at": now + _PENDING_TTL_SECONDS,
                }
            }
        )
        await session.answer_callback_query(
            TextsRU.TEACHER_GROUP_STUDENT_REMOVE_CONFIRM_ALERT, show_alert=True
        )
        return

    # подтверждено — удаляем
    await state.update_data({_PENDING_KEY: None})
    result = await session.teacher_manager().remove_student_from_group(
        group_id=callback_data.group_id,
        student_id=callback_data.student_id,
    )
    if not result.ok:
        await session.answer_callback_query(
            TextsRU.TEACHER_GROUP_STUDENT_REMOVE_FAILED_ALERT, show_alert=True
        )
        return

    await session.answer_callback_query(
        TextsRU.TEACHER_GROUP_STUDENT_REMOVE_SUCCESS_ALERT, show_alert=True
    )

    # Перерисовываем текущую страницу студентов (page внутри callback)
    view = await session.teacher_manager().build_group_students_page_view(
        group_id=callback_data.group_id,
        page=callback_data.page,
    )
    if not view:
        return

    await session.edit_message(
        view.text,
        message_id=session.message.message_id,
        reply_markup=view.keyboard_type,
        keyboard_data=view.keyboard_data,
    )
