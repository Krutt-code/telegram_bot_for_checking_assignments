from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.filters.command import CommandFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.navigation import NavigationHelper
from src.bot.session import UserSession
from src.core.enums import CommandsEnum, ReplyKeyboardTypeEnum

general_settings_router = Router()


@general_settings_router.message(CommandFilter(CommandsEnum.GENERAL_SETTINGS))
async def general_settings_handler(
    _: Message, state: FSMContext, session: UserSession
) -> None:
    """
    Обработчик команды "Общие настройки".
    Не является точкой входа, но обычно вызывается из главного меню роли.
    """
    # Регистрируем текущий шаг навигации
    # Предполагаем, что сюда пришли из меню роли, поэтому не очищаем историю
    await NavigationHelper.register_navigation_step(
        state,
        CommandsEnum.GENERAL_SETTINGS,
        ReplyKeyboardTypeEnum.GENERAL_SETTINGS,
        TextsRU.SELECT_ACTION,
    )

    await session.answer(
        TextsRU.SELECT_ACTION, reply_markup=ReplyKeyboardTypeEnum.GENERAL_SETTINGS
    )
