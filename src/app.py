from __future__ import annotations

import asyncio

from src.bot.bot import create_bot, create_dispatcher
from src.bot.keyboards.main_menu import set_main_menu
from src.core.context import AppContext
from src.core.logger import get_logger


async def main() -> None:
    """
    Основная точка входа приложения.

    - Создаёт AppContext (подключения/сервисы)
    - Запускает polling бота
    - Гарантированно закрывает ресурсы на выходе
    """
    logger = get_logger("app")

    ctx = await AppContext.create()

    # Загружаем заблокированных пользователей в Redis
    await ctx.user_locks_storage.load_all_banned_users()

    bot = create_bot()
    await set_main_menu(bot)
    dp = create_dispatcher(ctx)

    try:
        logger.info("Старт бота")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        logger.info("Остановка бота")
        await ctx.close()
        await bot.session.close()


def run() -> None:
    asyncio.run(main())
