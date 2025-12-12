from typing import TYPE_CHECKING, Optional

from src.core.enums import UserRoleEnum

if TYPE_CHECKING:
    from src.redis import RedisClient


class RedisRoleClient:
    """
    Хранит выбранную пользователем роль (активный режим) в redis.

    Ключи:
      - role:{user_id} -> "student" | "teacher"
    """

    def __init__(self, redis_client: "RedisClient"):
        self.redis_client = redis_client

    def _prefix(self, user_id: int) -> str:
        return f"role:{user_id}"

    async def get_role(self, user_id: int) -> Optional[UserRoleEnum]:
        value = await self.redis_client.get(self._prefix(user_id))
        return None if value is None else UserRoleEnum(value)

    async def set_role(self, user_id: int, role: UserRoleEnum) -> None:
        await self.redis_client.set(self._prefix(user_id), role.value)

    async def delete_role(self, user_id: int) -> None:
        await self.redis_client.delete(self._prefix(user_id))
