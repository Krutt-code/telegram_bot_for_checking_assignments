from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.filters import CommandFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.navigation import NavigationHelper, NavigationManager
from src.bot.session import UserSession
from src.core.enums import CommandsEnum, ReplyKeyboardTypeEnum
from src.core.fsm_states import TeacherGroupCreateStates

teacher_groups_create_router = Router()


@teacher_groups_create_router.message(CommandFilter(CommandsEnum.TEACHER_GROUP_CREATE))
async def teacher_groups_create_handler(
    _: Message, state: FSMContext, session: UserSession
) -> None:
    """
    Создание новой группы.
    """
    nav_manager = NavigationManager(state)
    await nav_manager.set_cancel_target(await nav_manager.get_previous())

    await NavigationHelper.register_navigation_step(
        state,
        CommandsEnum.TEACHER_GROUP_CREATE,
        ReplyKeyboardTypeEnum.TEACHER_GROUP_CREATE,
        TextsRU.SELECT_ACTION,
    )

    await state.set_state(TeacherGroupCreateStates.waiting_for_group_name)
    await session.answer(TextsRU.TEACHER_GROUP_CREATE_TITLE)


@teacher_groups_create_router.message(TeacherGroupCreateStates.waiting_for_group_name)
async def teacher_groups_create_save_name(
    message: Message, state: FSMContext, session: UserSession
) -> None:
    """
    Принимаем название группы, создаём и привязываем к преподавателю.
    """
    result = await session.teacher_manager().create_group(name=message.text or "")
    if not result.ok:
        if result.error_code == "invalid_name":
            await session.answer(TextsRU.TEACHER_GROUP_CREATE_INVALID_NAME)
        elif result.error_code == "duplicate_name":
            await session.answer(TextsRU.TEACHER_GROUP_CREATE_DUPLICATE_NAME)
        elif result.error_code == "teacher_not_found":
            await session.answer(TextsRU.TEACHER_NOT_FOUND)
        else:
            await session.answer(TextsRU.TEACHER_GROUP_CREATE_FAILED)
        await session.answer(TextsRU.TRY_AGAIN)
        return

    nav_manager = NavigationManager(state)
    await nav_manager.clear_state_and_data_keep_navigation()

    await session.answer(
        TextsRU.TEACHER_GROUP_CREATE_SUCCESS.format(name=result.normalized_name)
    )

    # Возвращаемся в меню "Группы" и показываем обновлённый список
    previous_step = await nav_manager.pop_previous(
        default_keyboard=ReplyKeyboardTypeEnum.TEACHER_GROUPS,
        default_text=TextsRU.SELECT_ACTION,
    )
    await session.answer(
        (previous_step.text if previous_step else TextsRU.SELECT_ACTION),
        reply_markup=ReplyKeyboardTypeEnum.TEACHER_GROUPS,
    )

    view = await session.teacher_manager().build_groups_page_view(page=1)
    if view:
        await session.answer(
            view.text,
            reply_markup=view.keyboard_type,
            keyboard_data=view.keyboard_data,
        )
