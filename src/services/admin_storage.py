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

    async def get_all_admin_ids(self) -> list[int]:
        """
        Возвращает список ID всех администраторов.

        Сначала пытается получить из кеша Redis, если кеш пуст -
        запрашивает из БД и кеширует результат.
        """
        # Пытаемся получить из кеша
        cached_ids = await self.redis_admin_client.get_all_cached_admin_ids()

        if cached_ids:
            return cached_ids

        # Если в кеше пусто, запрашиваем из БД
        admin_ids = await self.admins_repo.get_all_admin_ids()

        # Кешируем результат
        for admin_id in admin_ids:
            await self.redis_admin_client.set_admin(admin_id, True)

        return admin_ids
