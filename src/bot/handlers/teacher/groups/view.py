from __future__ import annotations

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.bot.filters.callback import CallbackFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.navigation import NavigationHelper
from src.bot.session import UserSession
from src.core.enums import CommandsEnum, ReplyKeyboardTypeEnum
from src.core.schemas import PaginationCallbackSchema, TeacherGroupCallbackSchema

teacher_group_view_router = Router()


def _extract_group_id_from_students_key(key: str) -> int | None:
    # ожидаем: "teacher_group_students:<group_id>"
    try:
        prefix, raw_id = key.split(":", 1)
        if prefix != "teacher_group_students":
            return None
        return int(raw_id)
    except Exception:
        return None


@teacher_group_view_router.callback_query(
    CallbackFilter(TeacherGroupCallbackSchema, action="view")
)
async def teacher_group_view_handler(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherGroupCallbackSchema,
) -> None:
    await session.answer_callback_query()

    view = await session.teacher_manager().build_group_students_page_view(
        group_id=callback_data.group_id,
        page=1,
    )
    if not view:
        await session.answer(TextsRU.TEACHER_GROUP_OPEN_FAILED)
        return

    # Запоминаем текущую группу для reply-команд (edit/delete/link)
    await state.update_data(
        current_group_id=view.group_id, current_group_name=view.group_name
    )

    await NavigationHelper.register_navigation_step(
        state,
        CommandsEnum.TEACHER_GROUP_VIEW,
        ReplyKeyboardTypeEnum.TEACHER_GROUP_VIEW,
        TextsRU.SELECT_ACTION,
    )

    # Reply-клавиатура действий над группой
    await session.answer(
        TextsRU.SELECT_ACTION,
        reply_markup=ReplyKeyboardTypeEnum.TEACHER_GROUP_VIEW,
    )
    # Inline-список студентов с пагинацией
    await session.answer(
        view.text,
        reply_markup=view.keyboard_type,
        keyboard_data=view.keyboard_data,
    )


@teacher_group_view_router.callback_query(
    CallbackFilter(
        PaginationCallbackSchema,
        key=lambda k: isinstance(k, str) and k.startswith("teacher_group_students:"),
    )
)
async def teacher_group_students_pagination_handler(
    _: CallbackQuery,
    session: UserSession,
    callback_data: PaginationCallbackSchema,
) -> None:
    await session.answer_callback_query()

    group_id = _extract_group_id_from_students_key(callback_data.key)
    if not group_id:
        await session.answer(TextsRU.TRY_AGAIN)
        return

    view = await session.teacher_manager().build_group_students_page_view(
        group_id=group_id,
        page=callback_data.page,
    )
    if not view:
        await session.answer(TextsRU.TEACHER_GROUP_OPEN_FAILED)
        return

    await session.edit_message(
        view.text,
        message_id=session.message.message_id,
        reply_markup=view.keyboard_type,
        keyboard_data=view.keyboard_data,
    )
