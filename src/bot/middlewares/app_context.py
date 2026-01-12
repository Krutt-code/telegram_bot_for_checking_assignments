from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware

from src.core.context import AppContext


class AppContextMiddleware(BaseMiddleware):
    """
    Прокидывает зависимости из AppContext в data, чтобы aiogram мог делать injection
    прямо в параметры хендлеров/фильтров.
    """

    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        data["ctx"] = self._ctx
        data["redis"] = self._ctx.redis
        data["users_client"] = self._ctx.users_client
        data["admin_storage"] = self._ctx.admin_storage
        data["role_storage"] = self._ctx.role_storage
        data["user_locks_storage"] = self._ctx.user_locks_storage
        return await handler(event, data)
