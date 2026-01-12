"""
Класы фильтра проверки доступа.
"""

from typing import TYPE_CHECKING, Union

from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.lexicon.texts import TextsRU
from src.core.enums import UserRoleEnum
from src.core.fsm_states import FullNameStates
from src.services import AdminStorage, RoleStorage, UserLocksStorage

if TYPE_CHECKING:
    from src.bot.session import UserSession


class IsStudentFilter(BaseFilter):
    async def __call__(
        self, event: Union[Message, CallbackQuery], role_storage: RoleStorage
    ) -> bool:
        user_id = event.from_user.id
        return await role_storage.get_role(user_id) == UserRoleEnum.STUDENT


class IsTeacherFilter(BaseFilter):
    async def __call__(
        self, event: Union[Message, CallbackQuery], role_storage: RoleStorage
    ) -> bool:
        user_id = event.from_user.id
        return await role_storage.get_role(user_id) == UserRoleEnum.TEACHER


class IsAdminFilter(BaseFilter):
    async def __call__(
        self, event: Union[Message, CallbackQuery], admin_storage: AdminStorage
    ) -> bool:
        user_id = event.from_user.id
        return await admin_storage.is_admin(user_id)


class HasRealFullNameFilter(BaseFilter):
    """
    Проверяет, что у пользователя заполнено real_full_name.
    Если нет — отправляет подсказку и блокирует хендлер.
    """

    async def __call__(
        self,
        event: Union[Message, CallbackQuery],
        session: "UserSession",
        state: FSMContext,
    ) -> bool:

        has_full_name = await session.user_manager().has_real_full_name()
        if has_full_name:
            return True

        await state.set_state(FullNameStates.waiting_for_full_name)
        await session.answer(TextsRU.FULL_NAME_REQUIRED)
        await session.answer(TextsRU.FULL_NAME_ENTER)
        return False


class IsBannedFilter(BaseFilter):
    """
    Проверяет, что пользователь заблокирован.
    Используется для обработчика заблокированных пользователей.
    """

    async def __call__(
        self, event: Union[Message, CallbackQuery], user_locks_storage: UserLocksStorage
    ) -> bool:
        user_id = event.from_user.id
        # Возвращаем True если заблокирован (обрабатываем)
        # Возвращаем False если не заблокирован (пропускаем)
        return await user_locks_storage.is_banned(user_id)
