from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.filters import CommandFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.navigation import NavigationHelper
from src.bot.session import UserSession
from src.core.enums import CommandsEnum, ReplyKeyboardTypeEnum

start_router = Router()


async def get_role_keyboard(session: UserSession) -> ReplyKeyboardTypeEnum:
    if await session.is_admin():
        return ReplyKeyboardTypeEnum.ADMIN
    else:
        return ReplyKeyboardTypeEnum.ROLE


@start_router.message(CommandFilter(CommandsEnum.START))
async def start_handler(_: Message, state: FSMContext, session: UserSession) -> None:
    """
    Обработчик команды /start.
    Выводит приветственное сообщение и предлагает выбрать роль.
    """
    # Очищаем историю навигации и состояние (точка входа)
    await NavigationHelper.register_entry_point(state)
    await state.clear()

    role_keyboard = await get_role_keyboard(session)
    await session.answer(TextsRU.HELLO, reply_markup=role_keyboard)


@start_router.message(CommandFilter(CommandsEnum.ROLE))
async def role_handler(_: Message, state: FSMContext, session: UserSession) -> None:
    """
    Обработчик команды /role.
    Предлагает выбрать роль.
    """
    # Очищаем историю навигации и состояние (точка входа)
    await NavigationHelper.register_entry_point(state)
    await state.clear()

    role_keyboard = await get_role_keyboard(session)
    await session.answer(TextsRU.SELECT_ROLE, reply_markup=role_keyboard)
