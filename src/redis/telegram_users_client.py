from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from src.redis import RedisClient


class RedisTelegramUsersClient:
    """
    Кэш "telegram_user существует в БД" в Redis.

    Ключи:
      - tg_user_exists:{user_id} -> "1"
    """

    def __init__(self, redis_client: "RedisClient"):
        self.redis_client = redis_client

    def _prefix(self, user_id: int) -> str:
        return f"tg_user_exists:{user_id}"

    def _full_name_prefix(self, user_id: int) -> str:
        return f"tg_user_full_name_exists:{user_id}"

    async def get_entry(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Возвращает (exists_flag, profile_hash|None).
        Формат значения: "1|<hash>".
        """
        raw = await self.redis_client.get(self._prefix(user_id))
        if raw is None:
            return False, None
        if "|" in raw:
            exists, profile_hash = raw.split("|", 1)
            return exists == "1", profile_hash or None
        return raw == "1", None

    async def set_entry(
        self, user_id: int, *, profile_hash: Optional[str], ttl_seconds: int
    ) -> None:
        payload = f"1|{profile_hash or ''}"
        await self.redis_client.set(self._prefix(user_id), payload, expire=ttl_seconds)

    async def invalidate(self, user_id: int) -> None:
        await self.redis_client.delete(self._prefix(user_id))

    async def get_full_name_exists(self, user_id: int) -> Optional[bool]:
        """
        Возвращает флаг существования real_full_name или None, если в кэше нет.
        """
        raw = await self.redis_client.get(self._full_name_prefix(user_id))
        if raw is None:
            return None
        return raw == "1"

    async def set_full_name_exists(
        self, user_id: int, exists: bool, *, ttl_seconds: int
    ) -> None:
        payload = "1" if exists else "0"
        await self.redis_client.set(
            self._full_name_prefix(user_id), payload, expire=ttl_seconds
        )

    async def invalidate_full_name_exists(self, user_id: int) -> None:
        await self.redis_client.delete(self._full_name_prefix(user_id))
