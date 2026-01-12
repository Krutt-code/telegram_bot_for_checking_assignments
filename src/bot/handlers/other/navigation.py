"""
Обработчики для навигации (кнопки "Назад" и "Отмена").
"""

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.filters.command import CommandFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.navigation import NavigationManager, handle_back_command
from src.bot.session import UserSession
from src.core.enums import CommandsEnum, ReplyKeyboardTypeEnum, UserRoleEnum
from src.core.logger import get_logger

navigation_router = Router()
logger = get_logger(__name__)


@navigation_router.message(CommandFilter(CommandsEnum.BACK))
async def back_handler(
    message: Message, state: FSMContext, session: UserSession
) -> None:
    """
    Обработчик кнопки "Назад".
    Возвращает пользователя на предыдущий шаг в навигации.
    """
    await handle_back_command(message, state, session)


async def _get_fallback_menu(session: UserSession) -> tuple[str, ReplyKeyboardTypeEnum]:
    """
    Фолбэк, если истории навигации нет: возвращаемся в меню по роли.
    """
    if await session.is_admin():
        return TextsRU.SELECT_ACTION, ReplyKeyboardTypeEnum.ADMIN
    role = await session.get_role()
    if role == UserRoleEnum.STUDENT:
        return TextsRU.SELECT_ACTION, ReplyKeyboardTypeEnum.STUDENT
    if role == UserRoleEnum.TEACHER:
        return TextsRU.SELECT_ACTION, ReplyKeyboardTypeEnum.TEACHER
    return TextsRU.SELECT_ROLE, ReplyKeyboardTypeEnum.ROLE


@navigation_router.message(StateFilter("*"), CommandFilter(CommandsEnum.CANCEL))
async def cancel_handler(_: Message, state: FSMContext, session: UserSession) -> None:
    """
    Универсальная "Отмена" для любого сценария в FSM.

    - Очищает FSM, но сохраняет history навигации
    - Возвращает на предыдущий шаг из history
    - Если history нет — возвращает в меню по роли
    """
    nav_manager = NavigationManager(state)

    # очищаем данные сценария, но не теряем history
    await nav_manager.clear_fsm_keep_history()

    cancel_target = await nav_manager.get_cancel_target()
    await session.answer(TextsRU.CANCEL)

    # Если сценарий был запущен с "якорем отмены" — возвращаемся в него (первый шаг/меню)
    if cancel_target:
        await nav_manager.rewind_history_to(cancel_target.command)
        await nav_manager.clear_cancel_target()
        await session.answer(
            cancel_target.text or TextsRU.SELECT_ACTION,
            reply_markup=cancel_target.keyboard,
        )
        return

    # Фолбэк: если якоря нет, возвращаемся на предыдущий шаг из истории
    previous_step = await nav_manager.pop_previous(default_text=TextsRU.SELECT_ACTION)
    if previous_step:
        await session.answer(
            previous_step.text or TextsRU.SELECT_ACTION,
            reply_markup=previous_step.keyboard,
        )
        return

    text, keyboard = await _get_fallback_menu(session)
    await session.answer(text, reply_markup=keyboard)
