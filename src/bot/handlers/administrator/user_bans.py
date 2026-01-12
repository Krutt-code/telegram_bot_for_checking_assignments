"""
Хендлеры для блокировки и разблокировки пользователей.
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.filters.command import CommandFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.navigation import NavigationHelper, NavigationManager
from src.bot.session import UserSession
from src.core.enums import CommandsEnum
from src.core.fsm_states import AdminBanUserStates, AdminUnbanUserStates
from src.services import UserLocksStorage

user_bans_router = Router()


@user_bans_router.message(CommandFilter(CommandsEnum.ADMIN_BAN_USER))
async def start_ban_user(
    message: Message, session: UserSession, state: FSMContext
) -> None:
    """
    Начинает процесс блокировки пользователя.

    Args:
        message: Сообщение от администратора
        session: Сессия пользователя
        state: FSM контекст
    """
    # Устанавливаем cancel_target для возврата в админ-панель
    nav_manager = NavigationManager(state)
    await nav_manager.set_cancel_target(await nav_manager.get_previous())

    await NavigationHelper.register_navigation_step(
        state,
        CommandsEnum.ADMIN_BAN_USER,
        keyboard=None,
        text=TextsRU.SELECT_ACTION,
    )
    await state.set_state(AdminBanUserStates.waiting_for_user_id)
    await session.answer(TextsRU.ADMIN_BAN_USER_PROMPT)


@user_bans_router.message(AdminBanUserStates.waiting_for_user_id, F.text)
async def process_ban_user_id(
    message: Message, session: UserSession, state: FSMContext
) -> None:
    """
    Обрабатывает ввод ID пользователя для блокировки.

    Args:
        message: Сообщение с ID пользователя
        session: Сессия пользователя
        state: FSM контекст
    """
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await session.answer(TextsRU.ADMIN_BAN_USER_INVALID_ID)
        return

    # Проверяем, не пытается ли администратор заблокировать самого себя
    if user_id == message.from_user.id:
        await session.answer(TextsRU.ADMIN_BAN_USER_SELF_BAN)
        return

    # Сохраняем ID в состояние
    await state.update_data(ban_user_id=user_id)
    await state.set_state(AdminBanUserStates.waiting_for_reason)
    await session.answer(TextsRU.ADMIN_BAN_USER_REASON_PROMPT.format(user_id=user_id))


@user_bans_router.message(AdminBanUserStates.waiting_for_reason, F.text)
async def process_ban_reason(
    message: Message,
    session: UserSession,
    state: FSMContext,
    user_locks_storage: UserLocksStorage,
) -> None:
    """
    Обрабатывает ввод причины блокировки и блокирует пользователя.

    Args:
        message: Сообщение с причиной блокировки
        session: Сессия пользователя
        state: FSM контекст
        user_locks_storage: Хранилище блокировок пользователей
    """
    reason = message.text.strip()
    data = await state.get_data()
    user_id = data.get("ban_user_id")

    if not user_id:
        await session.answer(TextsRU.ADMIN_BAN_USER_FAILED)
        nav_manager = NavigationManager(state)
        await nav_manager.clear_cancel_target()
        await nav_manager.clear_state_and_data_keep_navigation()
        return

    try:
        # Блокируем пользователя
        await user_locks_storage.ban_user(user_id, reason)
        await session.answer(TextsRU.ADMIN_BAN_USER_SUCCESS.format(user_id=user_id))
    except Exception:
        await session.answer(TextsRU.ADMIN_BAN_USER_FAILED)
    finally:
        nav_manager = NavigationManager(state)
        await nav_manager.clear_cancel_target()
        await nav_manager.clear_state_and_data_keep_navigation()


@user_bans_router.message(CommandFilter(CommandsEnum.ADMIN_UNBAN_USER))
async def start_unban_user(
    message: Message, session: UserSession, state: FSMContext
) -> None:
    """
    Начинает процесс разблокировки пользователя.

    Args:
        message: Сообщение от администратора
        session: Сессия пользователя
        state: FSM контекст
    """
    # Устанавливаем cancel_target для возврата в админ-панель
    nav_manager = NavigationManager(state)
    await nav_manager.set_cancel_target(await nav_manager.get_previous())

    await NavigationHelper.register_navigation_step(
        state,
        CommandsEnum.ADMIN_UNBAN_USER,
        keyboard=None,
        text=TextsRU.SELECT_ACTION,
    )
    await state.set_state(AdminUnbanUserStates.waiting_for_user_id)
    await session.answer(TextsRU.ADMIN_UNBAN_USER_PROMPT)


@user_bans_router.message(AdminUnbanUserStates.waiting_for_user_id, F.text)
async def process_unban_user_id(
    message: Message,
    session: UserSession,
    state: FSMContext,
    user_locks_storage: UserLocksStorage,
) -> None:
    """
    Обрабатывает ввод ID пользователя для разблокировки.

    Args:
        message: Сообщение с ID пользователя
        session: Сессия пользователя
        state: FSM контекст
        user_locks_storage: Хранилище блокировок пользователей
    """
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await session.answer(TextsRU.ADMIN_UNBAN_USER_INVALID_ID)
        return

    try:
        # Проверяем, заблокирован ли пользователь
        is_banned = await user_locks_storage.is_banned(user_id)
        if not is_banned:
            await session.answer(
                TextsRU.ADMIN_UNBAN_USER_NOT_BANNED.format(user_id=user_id)
            )
            nav_manager = NavigationManager(state)
            await nav_manager.clear_cancel_target()
            await nav_manager.clear_state_and_data_keep_navigation()
            return

        # Разблокируем пользователя
        await user_locks_storage.unban_user(user_id)
        await session.answer(TextsRU.ADMIN_UNBAN_USER_SUCCESS.format(user_id=user_id))
    except Exception:
        await session.answer(TextsRU.ADMIN_UNBAN_USER_FAILED)
    finally:
        nav_manager = NavigationManager(state)
        await nav_manager.clear_cancel_target()
        await nav_manager.clear_state_and_data_keep_navigation()
