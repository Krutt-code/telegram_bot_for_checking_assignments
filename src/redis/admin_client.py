from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.redis import RedisClient


class RedisAdminClient:
    """
    Хранит admin-флаг (привилегию) в redis.

    Ключи:
      - admin:{user_id} -> "1"
    """

    def __init__(self, redis_client: "RedisClient"):
        self.redis_client = redis_client

    def _prefix(self, user_id: int) -> str:
        return f"admin:{user_id}"

    async def is_admin(self, user_id: int) -> bool:
        value = await self.redis_client.get(self._prefix(user_id))
        return value == "1"

    async def set_admin(self, user_id: int, is_admin: bool) -> None:
        if is_admin:
            await self.redis_client.set(self._prefix(user_id), "1")
        else:
            await self.redis_client.delete(self._prefix(user_id))

    async def delete_admin(self, user_id: int) -> None:
        await self.redis_client.delete(self._prefix(user_id))

    async def get_all_cached_admin_ids(self) -> list[int]:
        """
        Возвращает список ID всех закешированных администраторов.

        Использует SCAN для безопасного получения всех ключей admin:*.
        """
        keys = await self.redis_client.scan_keys("admin:*")
        admin_ids = []
        for key in keys:
            # Извлекаем user_id из ключа вида b'admin:123'
            key_str = key.decode() if isinstance(key, bytes) else key
            try:
                user_id = int(key_str.split(":", 1)[1])
                admin_ids.append(user_id)
            except (IndexError, ValueError):
                continue
        return admin_ids
