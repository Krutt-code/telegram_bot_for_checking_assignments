from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.filters.command import CommandFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.navigation import NavigationHelper, NavigationManager
from src.bot.session import UserSession
from src.bot.utils.group_invite import perform_join_group
from src.core.enums import CommandsEnum, ReplyKeyboardTypeEnum
from src.core.fsm_states import FullNameStates

full_name_router = Router()


@full_name_router.message(CommandFilter(CommandsEnum.FULL_NAME_PANEL))
async def full_name_panel(_: Message, state: FSMContext, session: UserSession) -> None:
    """
    Первый шаг сценария: просим ввести ФИО и ставим состояние в Redis FSM.
    Добавляет кнопку "Назад" для возврата в общие настройки.
    """
    # Запоминаем "куда вернуться" при отмене сценария.
    nav_manager = NavigationManager(state)
    await nav_manager.set_cancel_target(await nav_manager.get_previous())

    # Регистрируем шаг навигации (пришли из general_settings)
    await NavigationHelper.register_navigation_step(
        state,
        CommandsEnum.FULL_NAME_PANEL,
        ReplyKeyboardTypeEnum.FULL_NAME_PANEL,
        TextsRU.SELECT_ACTION,
    )

    user_manager = session.user_manager()
    full_name = await user_manager.get_real_full_name()
    if not full_name:
        await state.set_state(FullNameStates.waiting_for_full_name)
        await session.answer(TextsRU.FULL_NAME_ENTER)
        return
    await state.update_data(full_name=full_name)
    await session.answer(TextsRU.FULL_NAME_NOW.format(full_name=full_name))
    await session.answer(
        TextsRU.SELECT_ACTION,
        reply_markup=ReplyKeyboardTypeEnum.FULL_NAME_PANEL,
    )


@full_name_router.message(CommandFilter(CommandsEnum.SET_FULL_NAME))
async def set_full_name(_: Message, state: FSMContext, session: UserSession) -> None:
    """
    Обработчик команды "Установить ФИО".
    Запрашивает ввод ФИО и добавляет кнопку "Отмена".
    """
    await state.set_state(FullNameStates.waiting_for_full_name)
    await session.answer(TextsRU.FULL_NAME_ENTER)


@full_name_router.message(FullNameStates.waiting_for_full_name)
async def save_full_name(
    message: Message, state: FSMContext, session: UserSession
) -> None:
    """
    Обработчик сохранения ФИО.
    После успешного сохранения возвращает в меню общих настроек.
    """
    full_name = message.text
    # Проверяем что в имене хотя бы 2 слова, так как фио могут быть очень разнообразными
    if not (full_name and len(full_name.split()) >= 2):
        await session.answer(TextsRU.FULL_NAME_ERROR)
        await session.answer(TextsRU.TRY_AGAIN)
        return

    pending_join_group_id = await state.get_value("pending_join_group_id", None)
    nav_manager = NavigationManager(state)
    old_full_name = await state.get_value("full_name", None)
    await nav_manager.clear_state_and_data_keep_navigation()

    if old_full_name == full_name:
        await session.answer(TextsRU.FULL_NAME_NOT_CHANGED)
    else:
        # Сохраняем новое ФИО
        user_manager = session.user_manager()
        await user_manager.set_real_full_name(full_name)
        await session.answer(TextsRU.FULL_NAME_SUCCESS)

    # Если это было заполнение ФИО по ссылке-приглашению — сразу добавляем в группу
    if pending_join_group_id:
        await perform_join_group(session=session, group_id=int(pending_join_group_id))
        return

    # Возвращаемся в общие настройки
    previous_step = await nav_manager.pop_previous(
        default_keyboard=ReplyKeyboardTypeEnum.GENERAL_SETTINGS,
        default_text=TextsRU.SELECT_ACTION,
    )

    if previous_step:
        await session.answer(
            previous_step.text,
            reply_markup=previous_step.keyboard,
        )
    else:
        # Если истории нет, возвращаемся в общие настройки
        await session.answer(
            TextsRU.SELECT_ACTION, reply_markup=ReplyKeyboardTypeEnum.GENERAL_SETTINGS
        )
