from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.filters.access import HasRealFullNameFilter
from src.bot.filters.command import CommandFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.navigation import NavigationHelper
from src.bot.session import UserSession
from src.core.enums import CommandsEnum, ReplyKeyboardTypeEnum

role_router = Router()
role_router.message.filter(HasRealFullNameFilter())
role_router.callback_query.filter(HasRealFullNameFilter())


@role_router.message(CommandFilter(CommandsEnum.STUDENT_ROLE))
async def student_role_handler(
    _: Message, state: FSMContext, session: UserSession
) -> None:
    """
    Обработчик выбора роли студента.
    Точка входа - очищает историю навигации.
    """
    # Очищаем историю навигации (точка входа)
    await NavigationHelper.register_entry_point(state)

    await session.student_manager().initialize()
    await session.answer(
        TextsRU.HELLO_STUDENT, reply_markup=ReplyKeyboardTypeEnum.STUDENT
    )


@role_router.message(CommandFilter(CommandsEnum.TEACHER_ROLE))
async def teacher_role_handler(
    _: Message, state: FSMContext, session: UserSession
) -> None:
    """
    Обработчик выбора роли преподавателя.
    Точка входа - очищает историю навигации.
    """
    # Очищаем историю навигации (точка входа)
    await NavigationHelper.register_entry_point(state)

    await session.teacher_manager().initialize()
    await session.answer(
        TextsRU.HELLO_TEACHER, reply_markup=ReplyKeyboardTypeEnum.TEACHER
    )
