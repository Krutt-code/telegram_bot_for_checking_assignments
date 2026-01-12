from __future__ import annotations

import asyncio
from dataclasses import dataclass

from src.core.logger import get_logger
from src.core.settings import settings
from src.redis import RedisClient, RedisTelegramUsersClient
from src.services import AdminStorage, RoleStorage

# Константы для переподключения Redis
REDIS_MAX_RETRIES = 5
REDIS_RETRY_DELAY = 2  # секунды (будет увеличиваться экспоненциально)

logger = get_logger("app_context")


@dataclass(slots=True)
class AppContext:
    """
    Контейнер зависимостей приложения (инфраструктура/сервисы).

    Идея: создать один раз на старте и прокинуть в aiogram через middleware,
    чтобы хендлеры/фильтры получали зависимости через injection, без "протаскивания".
    """

    redis: RedisClient
    users_client: RedisTelegramUsersClient
    admin_storage: AdminStorage
    role_storage: RoleStorage

    @classmethod
    async def create(cls) -> "AppContext":
        redis = RedisClient(settings.actual_redis_url)
        await cls._connect_redis_with_retry(redis)
        return cls(
            redis=redis,
            users_client=RedisTelegramUsersClient(redis),
            admin_storage=AdminStorage(redis),
            role_storage=RoleStorage(redis),
        )

    @staticmethod
    async def _connect_redis_with_retry(redis: RedisClient) -> None:
        """
        Подключается к Redis с несколькими попытками.

        Args:
            redis: Клиент Redis для подключения

        Raises:
            Exception: Если все попытки подключения исчерпаны
        """
        for attempt in range(1, REDIS_MAX_RETRIES + 1):
            try:
                logger.info(
                    f"Попытка подключения к Redis ({attempt}/{REDIS_MAX_RETRIES})..."
                )
                await redis.connect()
                logger.info("✅ Успешное подключение к Redis")
                return
            except Exception as e:
                error_msg = f"❌ Ошибка подключения к Redis (попытка {attempt}/{REDIS_MAX_RETRIES}): {e}"

                if attempt == REDIS_MAX_RETRIES:
                    logger.critical(
                        f"{error_msg}\n"
                        f"Исчерпаны все попытки подключения к Redis. "
                        f"Проверьте доступность Redis и правильность настроек REDIS_URL.",
                        exc_info=e,
                    )
                    raise

                # Экспоненциальная задержка: 2, 4, 8, 16 секунд
                delay = REDIS_RETRY_DELAY * (2 ** (attempt - 1))
                logger.warning(f"{error_msg}. Повторная попытка через {delay} сек...")
                await asyncio.sleep(delay)

    async def close(self) -> None:
        await self.redis.close()
