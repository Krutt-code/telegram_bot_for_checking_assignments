from src.db.repositories import UserLocksRepository
from src.redis import RedisClient, RedisUserLocksClient


class UserLocksStorage:
    """
    Управление блокировками пользователей.

    - Источник истины: MySQL (таблица user_locks)
    - Кэш: Redis
    """

    def __init__(self, redis_client: RedisClient):
        self.redis_locks_client = RedisUserLocksClient(redis_client)
        self.locks_repo = UserLocksRepository()

    async def is_banned(self, user_id: int) -> bool:
        """
        Проверяет, заблокирован ли пользователь.

        Сначала проверяет в кеше Redis, если не найдено - проверяет в БД.

        Args:
            user_id: ID пользователя

        Returns:
            True если пользователь заблокирован, иначе False
        """
        # Проверяем в кеше
        if await self.redis_locks_client.is_banned(user_id):
            return True

        # Проверяем в БД
        is_banned = await self.locks_repo.is_banned(user_id)
        if is_banned:
            # Кешируем результат
            lock_data = await self.locks_repo.get_by_id(user_id)
            if lock_data:
                await self.redis_locks_client.ban_user(user_id, lock_data.reason)
        return is_banned

    async def get_ban_reason(self, user_id: int) -> str | None:
        """
        Получает причину блокировки пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            Причина блокировки или None если не заблокирован
        """
        # Сначала пытаемся получить из кеша
        reason = await self.redis_locks_client.get_ban_reason(user_id)
        if reason:
            return reason

        # Если в кеше нет, проверяем БД
        lock_data = await self.locks_repo.get_by_id(user_id)
        if lock_data:
            # Кешируем
            await self.redis_locks_client.ban_user(user_id, lock_data.reason)
            return lock_data.reason

        return None

    async def ban_user(self, user_id: int, reason: str | None = None) -> None:
        """
        Блокирует пользователя.

        Args:
            user_id: ID пользователя
            reason: Причина блокировки
        """
        # Добавляем в БД
        await self.locks_repo.ban_user(user_id, reason)
        # Добавляем в кеш
        await self.redis_locks_client.ban_user(user_id, reason)

    async def unban_user(self, user_id: int) -> None:
        """
        Разблокирует пользователя.

        Args:
            user_id: ID пользователя
        """
        # Удаляем из БД
        await self.locks_repo.unban_user(user_id)
        # Удаляем из кеша
        await self.redis_locks_client.unban_user(user_id)

    async def load_all_banned_users(self) -> None:
        """
        Загружает всех заблокированных пользователей из БД в Redis.

        Используется при старте приложения для инициализации кеша.
        """
        # Получаем все блокировки из БД
        banned_ids = await self.locks_repo.get_all_banned_user_ids()

        # Загружаем каждого в кеш
        for user_id in banned_ids:
            lock_data = await self.locks_repo.get_by_id(user_id)
            if lock_data:
                await self.redis_locks_client.ban_user(user_id, lock_data.reason)
