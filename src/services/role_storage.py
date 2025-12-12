from typing import Optional

from src.core.enums import UserRoleEnum
from src.redis import RedisClient, RedisRoleClient


class RoleStorage:
    """
    Хранит выбранную пользователем роль (student/teacher).

    Источник истины: Redis (можно сделать постоянным или с TTL — на ваш выбор).
    """

    def __init__(self, redis_client: RedisClient):
        self.redis_role_client = RedisRoleClient(redis_client)

    async def get_role(self, user_id: int) -> Optional[UserRoleEnum]:
        return await self.redis_role_client.get_role(user_id)

    async def set_role(self, user_id: int, role: UserRoleEnum) -> None:
        await self.redis_role_client.set_role(user_id, role)

    async def clear_role(self, user_id: int) -> None:
        await self.redis_role_client.delete_role(user_id)
