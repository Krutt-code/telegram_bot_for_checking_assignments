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
