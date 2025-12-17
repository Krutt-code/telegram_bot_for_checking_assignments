from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.bot.lexicon.callback_data import CALLBACK_DATA

callbacks_router = Router()


@callbacks_router.callback_query(F.data == CALLBACK_DATA["NOOP"])
async def noop_callback_handler(query: CallbackQuery) -> None:
    """
    Универсальный обработчик для noop-кнопок.
    Просто закрывает "часики" у пользователя.
    """
    await query.answer()
