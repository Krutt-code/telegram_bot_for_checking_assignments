from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage

from src.bot.handlers import all_handlers_router
from src.bot.middlewares.app_context import AppContextMiddleware
from src.bot.middlewares.user_session import UserSessionMiddleware
from src.core.context import AppContext
from src.core.settings import settings


def create_bot() -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher(ctx: AppContext) -> Dispatcher:
    redis_conn = ctx.redis.redis
    if redis_conn is None:
        raise RuntimeError("Redis не инициализирован для FSM Storage")

    storage = RedisStorage(
        redis=redis_conn,
        key_builder=DefaultKeyBuilder(with_bot_id=True),
    )
    dp = Dispatcher(storage=storage)

    # Важно: оба middleware вешаем на update, чтобы работало и для Message и для CallbackQuery.
    # UserSessionMiddleware будет создавать session, используя ctx из data (если он есть).
    dp.update.middleware(AppContextMiddleware(ctx))
    dp.update.middleware(UserSessionMiddleware())

    dp.include_router(all_handlers_router)
    return dp
