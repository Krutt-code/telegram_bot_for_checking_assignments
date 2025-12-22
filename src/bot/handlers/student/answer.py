"""
Ответ на задание.
"""

from __future__ import annotations

from datetime import datetime

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.filters.callback import CallbackFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.navigation import NavigationManager
from src.bot.session import UserSession
from src.core.fsm_states import StudentHomeworkAnswerStates
from src.core.schemas import StudentHomeworkCallbackSchema
from src.db.services import HomeworksService

answer_router = Router()

_STATE_HOMEWORK_ID_KEY = "student_answer_homework_id"


@answer_router.callback_query(
    CallbackFilter(StudentHomeworkCallbackSchema, action="answer")
)
async def student_homework_answer_start(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: StudentHomeworkCallbackSchema,
) -> None:
    await session.answer_callback_query()

    hw = await HomeworksService.get_by_id(callback_data.homework_id)
    if not hw:
        await session.answer(TextsRU.TRY_AGAIN)
        return

    if hw.end_at and hw.end_at <= datetime.now():
        await session.answer(TextsRU.STUDENT_HOMEWORK_ANSWER_DEADLINE_PASSED)
        return

    nav_manager = NavigationManager(state)
    await nav_manager.set_cancel_target(await nav_manager.get_previous())

    await state.update_data({_STATE_HOMEWORK_ID_KEY: hw.homework_id})
    await state.set_state(StudentHomeworkAnswerStates.waiting_for_text)
    await session.answer(TextsRU.STUDENT_HOMEWORK_ANSWER_PROMPT)


@answer_router.message(StateFilter(StudentHomeworkAnswerStates.waiting_for_text))
async def student_homework_answer_receive_text(
    message: Message,
    state: FSMContext,
    session: UserSession,
) -> None:
    text = (message.text or "").strip()
    if not text:
        # если это не текст (фото/док) или пустая строка
        await session.answer(
            TextsRU.STUDENT_HOMEWORK_ANSWER_TEXT_ONLY
            if message.text is None
            else TextsRU.STUDENT_HOMEWORK_ANSWER_EMPTY
        )
        return

    homework_id = await state.get_value(_STATE_HOMEWORK_ID_KEY, None)
    if not homework_id:
        await session.answer(TextsRU.TRY_AGAIN)
        return

    hw = await HomeworksService.get_by_id(int(homework_id))
    if not hw:
        await session.answer(TextsRU.TRY_AGAIN)
        return

    if hw.end_at and hw.end_at <= datetime.now():
        await session.answer(TextsRU.STUDENT_HOMEWORK_ANSWER_DEADLINE_PASSED)
        nav_manager = NavigationManager(state)
        await nav_manager.clear_state_and_data_keep_navigation()
        return

    await session.student_manager().submit_answer(
        homework_id=int(homework_id), text=text
    )

    nav_manager = NavigationManager(state)
    await nav_manager.clear_state_and_data_keep_navigation()

    await session.answer(TextsRU.STUDENT_HOMEWORK_ANSWER_SENT)
