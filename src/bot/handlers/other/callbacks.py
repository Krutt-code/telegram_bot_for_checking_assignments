from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.bot.lexicon.callback_data import CALLBACK_DATA
from src.core.logger import get_function_logger

callbacks_router = Router()


@callbacks_router.callback_query(F.data == CALLBACK_DATA["NOOP"])
async def noop_callback_handler(query: CallbackQuery) -> None:
    """
    Универсальный обработчик для noop-кнопок.
    Просто закрывает "часики" у пользователя.
    """
    await query.answer()


@callbacks_router.callback_query()
async def other_callback_handler(query: CallbackQuery) -> None:
    """
    Универсальный обработчик для других callback_query.
    """
    logger = get_function_logger(other_callback_handler)
    logger.debug(f"Other callback query: {query.data}")
    await query.answer()
