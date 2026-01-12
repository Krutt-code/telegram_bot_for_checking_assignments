"""
Хендлер админ-панели.
"""

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.filters.command import CommandFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.navigation import NavigationHelper
from src.bot.session import UserSession
from src.core.enums import CommandsEnum, ReplyKeyboardTypeEnum

admin_panel_router = Router()


@admin_panel_router.message(CommandFilter(CommandsEnum.ADMIN_PANEL))
async def admin_panel_handler(
    _: Message, session: UserSession, state: FSMContext
) -> None:
    """
    Показывает админ-панель.
    """
    await NavigationHelper.register_navigation_step(
        state,
        CommandsEnum.ADMIN_PANEL,
        ReplyKeyboardTypeEnum.ADMIN_PANEL,
        TextsRU.HELLO_ADMIN_PANEL,
    )
    await session.answer(
        TextsRU.HELLO_ADMIN_PANEL, reply_markup=ReplyKeyboardTypeEnum.ADMIN_PANEL
    )
