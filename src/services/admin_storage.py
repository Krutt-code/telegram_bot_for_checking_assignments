from src.db.repositories import AdminsRepository
from src.redis import RedisAdminClient, RedisClient


class AdminStorage:
    """
    Проверка admin-привилегии.

    - Источник истины: MySQL (таблица admins)
    - Кэш: Redis
    """

    def __init__(self, redis_client: RedisClient):
        self.redis_admin_client = RedisAdminClient(redis_client)
        self.admins_repo = AdminsRepository()

    async def is_admin(self, user_id: int) -> bool:
        if await self.redis_admin_client.is_admin(user_id):
            return True
        is_admin = await self.admins_repo.is_admin(user_id)
        if is_admin:
            await self.redis_admin_client.set_admin(user_id, True)
        return is_admin

    async def invalidate(self, user_id: int) -> None:
        await self.redis_admin_client.delete_admin(user_id)
