from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.filters import CommandFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.navigation import NavigationHelper
from src.bot.session import UserSession
from src.bot.utils.group_invite import parse_join_group_payload, perform_join_group
from src.core.enums import CommandsEnum, ReplyKeyboardTypeEnum
from src.core.fsm_states import FullNameStates

start_router = Router()


async def get_role_keyboard(session: UserSession) -> ReplyKeyboardTypeEnum:
    if await session.is_admin():
        return ReplyKeyboardTypeEnum.ADMIN
    else:
        return ReplyKeyboardTypeEnum.ROLE


@start_router.message(CommandFilter(CommandsEnum.START))
async def start_handler(
    message: Message, state: FSMContext, session: UserSession
) -> None:
    """
    Обработчик команды /start.
    Выводит приветственное сообщение и предлагает выбрать роль.
    """
    # Очищаем историю навигации и состояние (точка входа)
    await NavigationHelper.register_entry_point(state)
    await state.clear()

    # Deep-link: /start <payload>
    payload = ""
    if message.text:
        parts = message.text.split(maxsplit=1)
        if len(parts) == 2:
            payload = parts[1].strip()

    join = parse_join_group_payload(payload)
    if join:
        # Если нет ФИО — просим заполнить, а join докрутим после сохранения ФИО
        has_full_name = await session.user_manager().has_real_full_name()
        if not has_full_name:
            await state.update_data(pending_join_group_id=join.group_id)
            await state.set_state(FullNameStates.waiting_for_full_name)
            await session.answer(TextsRU.FULL_NAME_REQUIRED)
            await session.answer(TextsRU.FULL_NAME_ENTER)
            return

        await perform_join_group(session=session, group_id=join.group_id)
        return

    role_keyboard = await get_role_keyboard(session)
    await session.answer(TextsRU.HELLO, reply_markup=role_keyboard)


@start_router.message(CommandFilter(CommandsEnum.ROLE))
async def role_handler(_: Message, state: FSMContext, session: UserSession) -> None:
    """
    Обработчик команды /role.
    Предлагает выбрать роль.
    """
    # Очищаем историю навигации и состояние (точка входа)
    await NavigationHelper.register_entry_point(state)
    await state.clear()

    role_keyboard = await get_role_keyboard(session)
    await session.answer(TextsRU.SELECT_ROLE, reply_markup=role_keyboard)
