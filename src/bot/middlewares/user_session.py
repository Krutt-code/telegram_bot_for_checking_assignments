from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, Update

from src.bot.session import UserSession
from src.redis import RedisTelegramUsersClient
from src.services import AdminStorage, RoleStorage, UserLocksStorage


class UserSessionMiddleware(BaseMiddleware):
    """
    Создаёт UserSession на каждый апдейт (Message/CallbackQuery) и кладёт в data,
    чтобы хендлеры могли принимать параметр `session: UserSession`.
    """

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        # Middleware навешан на dp.update, поэтому сюда чаще всего приходит Update.
        # Нам нужно достать из него Message/CallbackQuery, чтобы создать UserSession.
        obj: Message | CallbackQuery | None = None
        if isinstance(event, Update):
            obj = event.message or event.callback_query
        elif isinstance(event, (Message, CallbackQuery)):
            obj = event

        if obj is not None:
            # AppContextMiddleware может быть установлен в любом порядке относительно этого middleware,
            # поэтому берём зависимости либо напрямую из data, либо из ctx.
            if (
                "users_client" in data
                and "admin_storage" in data
                and "role_storage" in data
                and "user_locks_storage" in data
            ):
                users_client: RedisTelegramUsersClient = data["users_client"]
                admin_storage: AdminStorage = data["admin_storage"]
                role_storage: RoleStorage = data["role_storage"]
                user_locks_storage: UserLocksStorage = data["user_locks_storage"]
            else:
                ctx = data["ctx"]
                users_client = ctx.users_client
                admin_storage = ctx.admin_storage
                role_storage = ctx.role_storage
                user_locks_storage = ctx.user_locks_storage
            session_obj = UserSession(
                obj,
                users_client=users_client,
                admin_storage=admin_storage,
                role_storage=role_storage,
                user_locks_storage=user_locks_storage,
                state=data.get("state"),
            )
            # На всякий случай: если aiogram не положил FSMContext в data (редко),
            # то позже хендлеры могут привязать его вручную через session.bind_state(...).
            if isinstance(data.get("state"), FSMContext):
                session_obj.bind_state(data.get("state"))
            data["session"] = session_obj
        return await handler(event, data)
