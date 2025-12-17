from __future__ import annotations

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.filters import CommandFilter
from src.bot.filters.callback import CallbackFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.managers.teacher import TeacherManager
from src.bot.navigation import NavigationHelper
from src.bot.session import UserSession
from src.core.enums import CommandsEnum, ReplyKeyboardTypeEnum
from src.core.schemas import PaginationCallbackSchema

teacher_groups_review_router = Router()


@teacher_groups_review_router.message(CommandFilter(CommandsEnum.TEACHER_GROUPS))
async def teacher_groups_review_handler(
    _: Message, state: FSMContext, session: UserSession
) -> None:
    """
    Выводим список групп, которые закреплены за преподавателем.

    Делаем вывод групп с пагинацией по 10 групп на страницу.
    На группы можно кликать, чтобы посмотреть её данные.
    """
    await NavigationHelper.register_navigation_step(
        state,
        CommandsEnum.TEACHER_GROUPS,
        ReplyKeyboardTypeEnum.TEACHER_GROUPS,
        TextsRU.SELECT_ACTION,
    )

    view = await session.teacher_manager().build_groups_page_view(page=1)
    if not view:
        # на всякий случай: в норме teacher должен создаваться при выборе роли
        await session.answer(TextsRU.TEACHER_NOT_FOUND)
        return

    # Reply-клавиатура сценария (создание/другие действия) — отдельным сообщением
    # (нельзя совместить reply и inline в одном reply_markup).
    await session.answer(
        TextsRU.SELECT_ACTION,
        reply_markup=ReplyKeyboardTypeEnum.TEACHER_GROUPS,
    )
    await session.answer(
        view.text,
        reply_markup=view.keyboard_type,
        keyboard_data=view.keyboard_data,
    )


@teacher_groups_review_router.callback_query(
    CallbackFilter(
        PaginationCallbackSchema,
        key=TeacherManager.GROUPS_PAGINATION_KEY,
    )
)
async def teacher_groups_pagination_handler(
    _: CallbackQuery,
    session: UserSession,
    callback_data: PaginationCallbackSchema,
) -> None:
    await session.answer_callback_query()

    view = await session.teacher_manager().build_groups_page_view(
        page=callback_data.page
    )
    if not view:
        await session.answer(TextsRU.TEACHER_NOT_FOUND)
        return

    await session.edit_message(
        view.text,
        message_id=session.message.message_id,
        reply_markup=view.keyboard_type,
        keyboard_data=view.keyboard_data,
    )
