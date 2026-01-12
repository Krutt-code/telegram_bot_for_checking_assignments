"""
Утилиты для отправки уведомлений администраторам о критических ошибках.
"""

from typing import Optional

from aiogram import Bot

from src.core.logger import get_logger
from src.services import AdminStorage

logger = get_logger(__name__)


async def notify_admins_about_error(
    bot: Bot,
    admin_storage: AdminStorage,
    error_type: str,
    error_message: str,
    details: Optional[str] = None,
) -> None:
    """
    Отправляет уведомление всем администраторам о критической ошибке.

    Args:
        bot: Экземпляр бота для отправки сообщений
        admin_storage: Хранилище для получения списка админов
        error_type: Тип ошибки (например, "Redis Connection Error")
        error_message: Краткое описание ошибки
        details: Дополнительные детали (опционально)
    """
    try:
        # Получаем список ID всех администраторов из кеша
        admin_ids = await admin_storage.get_all_admin_ids()

        if not admin_ids:
            logger.warning("Список администраторов пуст, уведомления не отправлены")
            return

        # Формируем сообщение
        notification_text = (
            f"🚨 <b>Критическая ошибка в боте</b>\n\n"
            f"<b>Тип:</b> <code>{error_type}</code>\n"
            f"<b>Сообщение:</b> {error_message}\n"
        )

        if details:
            notification_text += f"\n<b>Детали:</b>\n<code>{details}</code>"

        # Отправляем уведомления всем админам
        success_count = 0
        for admin_id in admin_ids:
            try:
                await bot.send_message(chat_id=admin_id, text=notification_text)
                success_count += 1
            except Exception as send_error:
                logger.error(
                    f"Не удалось отправить уведомление администратору {admin_id}: {send_error}"
                )

        logger.info(
            f"Уведомления о критической ошибке отправлены "
            f"{success_count}/{len(admin_ids)} администраторам"
        )

    except Exception as e:
        logger.error(f"Ошибка при попытке уведомить администраторов: {e}", exc_info=e)


async def notify_admins_service_unavailable(
    bot: Bot, admin_storage: AdminStorage, service_name: str
) -> None:
    """
    Отправляет уведомление администраторам о недоступности сервиса.

    Args:
        bot: Экземпляр бота
        admin_storage: Хранилище администраторов
        service_name: Название сервиса (Redis, MySQL, и т.д.)
    """
    await notify_admins_about_error(
        bot=bot,
        admin_storage=admin_storage,
        error_type=f"{service_name} Unavailable",
        error_message=f"Сервис {service_name} недоступен",
        details="Бот продолжает работу, но функциональность может быть ограничена",
    )


async def notify_admins_service_restored(
    bot: Bot, admin_storage: AdminStorage, service_name: str
) -> None:
    """
    Отправляет уведомление администраторам о восстановлении сервиса.

    Args:
        bot: Экземпляр бота
        admin_storage: Хранилище администраторов
        service_name: Название сервиса (Redis, MySQL, и т.д.)
    """
    try:
        admin_ids = await admin_storage.get_all_admin_ids()

        if not admin_ids:
            return

        notification_text = (
            f"✅ <b>Сервис восстановлен</b>\n\n"
            f"Сервис <code>{service_name}</code> снова доступен.\n"
            f"Бот работает в штатном режиме."
        )

        for admin_id in admin_ids:
            try:
                await bot.send_message(chat_id=admin_id, text=notification_text)
            except Exception:
                pass  # Игнорируем ошибки при отправке "хороших" новостей

        logger.info(
            f"Уведомления о восстановлении {service_name} отправлены администраторам"
        )

    except Exception as e:
        logger.error(f"Ошибка при отправке уведомлений о восстановлении: {e}")
