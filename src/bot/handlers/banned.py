"""
Обработчик для заблокированных пользователей.
"""

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from src.bot.filters import IsBannedFilter
from src.bot.lexicon.texts import TextsRU
from src.services import UserLocksStorage

banned_router = Router()


@banned_router.message(IsBannedFilter())
async def handle_banned_user_message(
    message: Message, user_locks_storage: UserLocksStorage, state: FSMContext
) -> None:
    """
    Обрабатывает любые сообщения от заблокированных пользователей.

    Очищает состояние FSM и убирает клавиатуру.

    Args:
        message: Сообщение от пользователя
        user_locks_storage: Хранилище блокировок пользователей
        state: FSM контекст
    """
    user_id = message.from_user.id

    # Получаем причину блокировки
    reason = await user_locks_storage.get_ban_reason(user_id)
    if not reason:
        reason = "Не указана"

    # Очищаем состояние FSM
    await state.clear()

    # Отправляем сообщение с удалением клавиатуры
    await message.answer(
        TextsRU.USER_BANNED.format(reason=reason), reply_markup=ReplyKeyboardRemove()
    )


@banned_router.callback_query(IsBannedFilter())
async def handle_banned_user_callback(
    callback: CallbackQuery, user_locks_storage: UserLocksStorage, state: FSMContext
) -> None:
    """
    Обрабатывает любые callback-запросы от заблокированных пользователей.

    Очищает состояние FSM.

    Args:
        callback: Callback-запрос от пользователя
        user_locks_storage: Хранилище блокировок пользователей
        state: FSM контекст
    """
    user_id = callback.from_user.id

    # Получаем причину блокировки
    reason = await user_locks_storage.get_ban_reason(user_id)
    if not reason:
        reason = "Не указана"

    # Очищаем состояние FSM
    await state.clear()

    # Отправляем alert с причиной блокировки
    await callback.answer(TextsRU.USER_BANNED.format(reason=reason), show_alert=True)
