from aiogram import Router
from aiogram.types import Message

from src.bot.filters.command import CommandFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.session import UserSession
from src.core.enums import CommandsEnum

help_router = Router()


@help_router.message(CommandFilter(CommandsEnum.HELP))
async def help_handler(_: Message, session: UserSession) -> None:
    await session.answer(TextsRU.HELP)
