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

from src.bot.lexicon.texts import TextsRU
from src.core.logger import ModulLogger

# Создаем отдельный логгер для ошибок aiogram
aiogram_errors_logger = ModulLogger("aiogram_errors")
logger = aiogram_errors_logger.get_logger("errors")

error_router = Router()


@error_router.errors()
async def errors_handler(event: ErrorEvent) -> Any:
    """
    Глобальный обработчик ошибок aiogram.

    Логирует все необработанные исключения и уведомляет пользователя
    о технической проблеме дружелюбным сообщением.

    Исключения Telegram API (сетевые ошибки, блокировка бота и т.д.)
    логируются, но не отправляются пользователю.

    Args:
        event: Событие с ошибкой от aiogram

    Returns:
        True - чтобы aiogram считал ошибку обработанной
    """
    update: Update = event.update
    exception: Exception = event.exception

    # Определяем тип и сообщение ошибки
    error_type = type(exception).__name__
    error_message = str(exception)

    # Извлекаем информацию о пользователе и контексте
    user_info = "Unknown"
    message_text = None

    if update.message:
        user_info = (
            f"User ID: {update.message.from_user.id}, "
            f"Username: @{update.message.from_user.username or 'None'}"
        )
        message_text = (
            update.message.text or update.message.caption or "[non-text message]"
        )
    elif update.callback_query:
        user_info = (
            f"User ID: {update.callback_query.from_user.id}, "
            f"Username: @{update.callback_query.from_user.username or 'None'}"
        )
        message_text = f"[callback: {update.callback_query.data}]"

    # Логируем ошибку с полной информацией для отладки
    logger.error(
        f"Ошибка обработки update:\n"
        f"  Тип ошибки: {error_type}\n"
        f"  Сообщение: {error_message}\n"
        f"  Пользователь: {user_info}\n"
        f"  Текст/данные: {message_text}\n"
        f"  Update ID: {update.update_id}",
        exc_info=exception,
    )

    # Список ошибок Telegram API, о которых не нужно уведомлять пользователя
    # (это технические ошибки инфраструктуры Telegram, а не бота)
    telegram_api_errors = [
        TelegramNetworkError.__name__,  # Сетевые проблемы
        TelegramRetryAfter.__name__,  # Rate limit от Telegram
        TelegramForbiddenError.__name__,  # Пользователь заблокировал бота
        TelegramBadRequest.__name__,  # Некорректный запрос к API
        TelegramNotFound.__name__,  # Ресурс не найден в Telegram
        TelegramEntityTooLarge.__name__,  # Слишком большой файл/сообщение
    ]

    # Если это не ошибка Telegram API, уведомляем пользователя
    if error_type not in telegram_api_errors:
        try:
            if update.message:
                await _notify_user_message(update.message, exception)
            elif update.callback_query:
                await _notify_user_callback(update.callback_query, exception)
        except Exception as notification_error:
            # Если не удалось отправить уведомление (например, бот заблокирован),
            # просто логируем это и продолжаем
            logger.error(
                f"Не удалось уведомить пользователя об ошибке: {notification_error}",
                exc_info=notification_error,
            )

    # Возвращаем True, чтобы aiogram считал ошибку обработанной
    return True


async def _notify_user_message(message: Message, exception: Exception) -> None:
    """
    Отправляет пользователю уведомление об ошибке через обычное сообщение.

    Использует дружелюбные тексты из лексикона для различных типов ошибок.

    Args:
        message: Сообщение от пользователя
        exception: Исключение, которое произошло
    """
    error_type = type(exception).__name__

    # Определяем тип ошибки и выбираем соответствующее сообщение
    if "Redis" in error_type or "Connection" in error_type:
        user_message = TextsRU.ERROR_REDIS_CONNECTION
    elif "Database" in error_type or "SQL" in error_type or "Operational" in error_type:
        user_message = TextsRU.ERROR_DATABASE
    else:
        user_message = TextsRU.ERROR_GENERIC.format(error_code=error_type)

    await message.answer(user_message)


async def _notify_user_callback(callback: CallbackQuery, exception: Exception) -> None:
    """
    Отправляет пользователю уведомление об ошибке через callback alert.

    Использует краткие дружелюбные тексты из лексикона для alert-окон.

    Args:
        callback: Callback-запрос от пользователя
        exception: Исключение, которое произошло
    """
    error_type = type(exception).__name__

    # Определяем тип ошибки и выбираем соответствующее краткое сообщение для alert
    if "Redis" in error_type or "Connection" in error_type:
        alert_text = TextsRU.ERROR_REDIS_CONNECTION_ALERT
    elif "Database" in error_type or "SQL" in error_type or "Operational" in error_type:
        alert_text = TextsRU.ERROR_DATABASE_ALERT
    else:
        alert_text = TextsRU.ERROR_GENERIC_ALERT.format(error_type=error_type)

    await callback.answer(alert_text, show_alert=True)
