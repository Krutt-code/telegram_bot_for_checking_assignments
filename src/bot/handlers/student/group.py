"""
Отображаем пренадлежность.
-   Что за группа
-   Кто преподователь
Есть возможность выйти
"""

import time

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.filters import CommandFilter
from src.bot.filters.callback import CallbackFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.session import UserSession
from src.core.enums import CommandsEnum, InlineKeyboardTypeEnum
from src.core.schemas import StudentGroupExitCallbackSchema

group_router = Router()

_PENDING_TTL_SECONDS = 30
_PENDING_KEY = "pending_student_group_exit"


@group_router.message(CommandFilter(CommandsEnum.STUDENT_GROUP))
async def student_group_handler(_: Message, session: UserSession) -> None:
    assigned_group = await session.student_manager().get_assigned_group()
    if not assigned_group:
        await session.answer(TextsRU.STUDENT_GROUP_NOT_FOUND)
        return
    await session.answer(
        TextsRU.STUDENT_GROUP_INFO.format(
            group_name=assigned_group.group.name,
            teacher_full_name=assigned_group.teacher.user.real_full_name,
        ),
        reply_markup=InlineKeyboardTypeEnum.STUDENT_GROUP_EXIT,
    )


@group_router.callback_query(
    CallbackFilter(StudentGroupExitCallbackSchema, action="exit")
)
async def student_group_exit_handler(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: StudentGroupExitCallbackSchema,
) -> None:
    """
    2-step подтверждение через alert:
    - 1-й клик: показываем alert и запоминаем pending в FSM на короткое время
    - 2-й клик в пределах TTL: выполняем выход из группы и обновляем сообщение
    """
    now = int(time.time())
    pending = await state.get_value(_PENDING_KEY, None)

    if (
        not isinstance(pending, dict)
        or pending.get("expires_at", 0) < now
        or pending.get("action") != callback_data.action
    ):
        await state.update_data(
            {
                _PENDING_KEY: {
                    "action": callback_data.action,
                    "expires_at": now + _PENDING_TTL_SECONDS,
                }
            }
        )
        await session.answer_callback_query(
            TextsRU.STUDENT_GROUP_EXIT_CONFIRM, show_alert=True
        )
        return

    # подтверждено
    await state.update_data({_PENDING_KEY: None})

    # если группы уже нет — считаем что "выйти" не из чего
    current_group = await session.student_manager().get_group()
    if not current_group:
        await session.answer_callback_query(
            TextsRU.STUDENT_GROUP_EXIT_FAILED, show_alert=True
        )
        await session.edit_message(
            TextsRU.STUDENT_GROUP_NOT_FOUND,
            message_id=session.message.message_id,
            reply_markup=None,
        )
        return

    updated = await session.student_manager().leave_group()
    if not updated:
        await session.answer_callback_query(
            TextsRU.STUDENT_GROUP_EXIT_FAILED, show_alert=True
        )
        return

    await session.answer_callback_query(
        TextsRU.STUDENT_GROUP_EXIT_SUCCESS, show_alert=True
    )
    await session.edit_message(
        TextsRU.STUDENT_GROUP_EXIT_SUCCESS,
        message_id=session.message.message_id,
        reply_markup=None,
    )
