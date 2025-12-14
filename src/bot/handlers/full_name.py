from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from src.bot.filters.command import CommandFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.session import UserSession
from src.core.enums import CommandsEnum, ReplyKeyboardTypeEnum

full_name_router = Router()


class FullNameStates(StatesGroup):
    waiting_for_full_name = State()


@full_name_router.message(CommandFilter(CommandsEnum.FULL_NAME_PANEL))
async def full_name_panel(
    message: Message, state: FSMContext, session: UserSession
) -> None:
    """
    Первый шаг сценария: просим ввести ФИО и ставим состояние в Redis FSM.
    """
    user_manager = session.user_manager()
    full_name = await user_manager.get_real_full_name()
    if not full_name:
        await state.set_state(FullNameStates.waiting_for_full_name)
        await session.answer(TextsRU.FULL_NAME_ENTER)
        return
    await state.update_data(full_name=full_name)
    await session.answer(TextsRU.FULL_NAME_NOW.format(full_name=full_name))
    await session.answer(
        TextsRU.SELECT_ACTION, reply_markup=ReplyKeyboardTypeEnum.FULL_NAME_PANEL
    )


@full_name_router.message(CommandFilter(CommandsEnum.SET_FULL_NAME))
async def set_full_name(_: Message, state: FSMContext, session: UserSession) -> None:
    await state.set_state(FullNameStates.waiting_for_full_name)
    await session.answer(TextsRU.FULL_NAME_ENTER)


@full_name_router.message(
    CommandFilter(CommandsEnum.CANCEL), FullNameStates.waiting_for_full_name
)
async def cancel_full_name(_: Message, state: FSMContext, session: UserSession) -> None:
    await state.clear()
    message_ids = await session.answer(
        TextsRU.CANCEL, reply_markup=ReplyKeyboardTypeEnum.ROLE
    )
    await session.delete_messages(message_ids)


@full_name_router.message(FullNameStates.waiting_for_full_name)
async def save_full_name(
    message: Message, state: FSMContext, session: UserSession
) -> None:
    full_name = message.text
    # Проверяем что в имене хотя бы 2 слова, так как фио могут быть очень разнообразными
    if not (full_name and len(full_name.split()) >= 2):
        await session.answer(TextsRU.FULL_NAME_ERROR)
        await session.answer(TextsRU.TRY_AGAIN)
        return
    old_full_name = await state.get_value("full_name", None)
    if old_full_name == full_name:
        await session.answer(TextsRU.FULL_NAME_NOT_CHANGED)
        await state.clear()
        return
    user_manager = session.user_manager()
    await user_manager.set_real_full_name(full_name)
    await session.answer(
        TextsRU.FULL_NAME_SUCCESS, reply_markup=ReplyKeyboardTypeEnum.ROLE
    )
    await state.clear()
