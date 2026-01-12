from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.redis import RedisClient


class RedisUserLocksClient:
    """
    Хранит информацию о заблокированных пользователях в Redis.

    Ключи:
      - user_lock:{user_id} -> reason (причина блокировки)
    """

    def __init__(self, redis_client: "RedisClient"):
        self.redis_client = redis_client

    def _prefix(self, user_id: int) -> str:
        return f"user_lock:{user_id}"

    async def is_banned(self, user_id: int) -> bool:
        """
        Проверяет, заблокирован ли пользователь.

        Args:
            user_id: ID пользователя

        Returns:
            True если пользователь заблокирован, иначе False
        """
        value = await self.redis_client.get(self._prefix(user_id))
        return value is not None

    async def get_ban_reason(self, user_id: int) -> str | None:
        """
        Получает причину блокировки пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            Причина блокировки или None если не заблокирован
        """
        return await self.redis_client.get(self._prefix(user_id))

    async def ban_user(self, user_id: int, reason: str | None = None) -> None:
        """
        Добавляет пользователя в список заблокированных.

        Args:
            user_id: ID пользователя
            reason: Причина блокировки (опционально)
        """
        ban_reason = reason if reason else "Не указана"
        await self.redis_client.set(self._prefix(user_id), ban_reason)

    async def unban_user(self, user_id: int) -> None:
        """
        Удаляет пользователя из списка заблокированных.

        Args:
            user_id: ID пользователя
        """
        await self.redis_client.delete(self._prefix(user_id))

    async def get_all_banned_user_ids(self) -> list[int]:
        """
        Возвращает список ID всех заблокированных пользователей.

        Использует SCAN для безопасного получения всех ключей user_lock:*.

        Returns:
            Список ID заблокированных пользователей
        """
        keys = await self.redis_client.scan_keys("user_lock:*")
        banned_ids = []
        for key in keys:
            # Извлекаем user_id из ключа вида b'user_lock:123'
            key_str = key.decode() if isinstance(key, bytes) else key
            try:
                user_id = int(key_str.split(":", 1)[1])
                banned_ids.append(user_id)
            except (IndexError, ValueError):
                continue
        return banned_ids
