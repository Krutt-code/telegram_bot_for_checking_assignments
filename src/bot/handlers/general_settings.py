from aiogram import Router
from aiogram.types import Message

from src.bot.filters.command import CommandFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.session import UserSession
from src.core.enums import CommandsEnum, ReplyKeyboardTypeEnum

general_settings_router = Router()


@general_settings_router.message(CommandFilter(CommandsEnum.GENERAL_SETTINGS))
async def general_settings_handler(_: Message, session: UserSession) -> None:
    await session.answer(
        TextsRU.SELECT_ACTION, reply_markup=ReplyKeyboardTypeEnum.GENERAL_SETTINGS
    )
