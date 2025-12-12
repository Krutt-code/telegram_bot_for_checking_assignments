from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.redis import RedisClient


class RedisStateClient:
    """
    Клиент для работы с состояниями.
    """

    def __init__(self, redis_client: "RedisClient"):
        self.redis_client = redis_client

    def _prefix(self, user_id: int) -> str:
        return f"state:{user_id}"

    async def get_state(self, user_id: int) -> Optional[str]:
        return await self.redis_client.get(self._prefix(user_id))

    async def set_state(self, user_id: int, state: str) -> None:
        await self.redis_client.set(self._prefix(user_id), state)

    async def delete_state(self, user_id: int) -> None:
        await self.redis_client.delete(self._prefix(user_id))
