"""
Обработка ошибок aiogram и логирование.
"""

from typing import Any

from aiogram import Router
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramEntityTooLarge,
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramNotFound,
    TelegramRetryAfter,
)
from aiogram.types import CallbackQuery, ErrorEvent, Message, Update

from src.core.logger import ModulLogger

# Создаем отдельный логгер для ошибок aiogram
aiogram_errors_logger = ModulLogger("aiogram_errors")
logger = aiogram_errors_logger.get_logger("errors")

error_router = Router()


@error_router.errors()
async def errors_handler(event: ErrorEvent) -> Any:
    """
    Глобальный обработчик ошибок aiogram.

    Логирует все необработанные исключения и пытается уведомить пользователя
    о технической проблеме.
    """
    update: Update = event.update
    exception: Exception = event.exception

    # Определяем тип ошибки для лучшего логирования
    error_type = type(exception).__name__
    error_message = str(exception)

    # Получаем информацию о пользователе и сообщении
    user_info = "Unknown"
    message_text = None

    if update.message:
        user_info = f"User ID: {update.message.from_user.id}, Username: @{update.message.from_user.username or 'None'}"
        message_text = (
            update.message.text or update.message.caption or "[non-text message]"
        )
    elif update.callback_query:
        user_info = f"User ID: {update.callback_query.from_user.id}, Username: @{update.callback_query.from_user.username or 'None'}"
        message_text = f"[callback: {update.callback_query.data}]"

    # Логируем ошибку с полной информацией
    logger.error(
        f"Ошибка обработки update:\n"
        f"  Тип ошибки: {error_type}\n"
        f"  Сообщение: {error_message}\n"
        f"  Пользователь: {user_info}\n"
        f"  Текст/данные: {message_text}\n"
        f"  Update ID: {update.update_id}",
        exc_info=exception,
    )

    errors_users_dont_need_notification = [
        TelegramNetworkError.__name__,
        TelegramRetryAfter.__name__,
        TelegramForbiddenError.__name__,
        TelegramBadRequest.__name__,
        TelegramNotFound.__name__,
        TelegramEntityTooLarge.__name__,
    ]
    if error_type not in errors_users_dont_need_notification:
        # Пытаемся уведомить пользователя
        try:
            if update.message:
                await _notify_user_message(update.message, exception)
            elif update.callback_query:
                await _notify_user_callback(update.callback_query, exception)
        except Exception as notification_error:
            logger.error(
                f"Не удалось уведомить пользователя об ошибке: {notification_error}",
                exc_info=notification_error,
            )

    # Возвращаем True, чтобы aiogram считал ошибку обработанной
    return True


async def _notify_user_message(message: Message, exception: Exception) -> None:
    """
    Отправляет пользователю уведомление об ошибке через обычное сообщение.
    """
    error_type = type(exception).__name__

    # Определяем тип ошибки для более понятного сообщения
    if "Redis" in error_type or "Connection" in error_type:
        user_message = (
            "⚠️ <b>Временная техническая проблема</b>\n\n"
            "Сервис временно недоступен. Пожалуйста, попробуйте позже.\n"
            "Если проблема повторяется, обратитесь к администратору."
        )
    elif "Database" in error_type or "SQL" in error_type or "Operational" in error_type:
        user_message = (
            "⚠️ <b>Проблема с базой данных</b>\n\n"
            "Не удалось выполнить операцию. Попробуйте позже.\n"
            "Ваши данные в безопасности."
        )
    else:
        user_message = (
            "⚠️ <b>Произошла ошибка</b>\n\n"
            "К сожалению, не удалось обработать ваш запрос.\n"
            "Попробуйте еще раз или обратитесь к администратору.\n\n"
            f"<code>Код ошибки: {error_type}</code>"
        )

    await message.answer(user_message)


async def _notify_user_callback(callback: CallbackQuery, exception: Exception) -> None:
    """
    Отправляет пользователю уведомление об ошибке через callback alert.
    """
    error_type = type(exception).__name__

    if "Redis" in error_type or "Connection" in error_type:
        alert_text = "⚠️ Сервис временно недоступен. Попробуйте позже."
    elif "Database" in error_type or "SQL" in error_type or "Operational" in error_type:
        alert_text = "⚠️ Проблема с базой данных. Попробуйте позже."
    else:
        alert_text = f"⚠️ Ошибка: {error_type}. Попробуйте позже."

    await callback.answer(alert_text, show_alert=True)
