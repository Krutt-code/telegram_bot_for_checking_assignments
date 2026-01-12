from __future__ import annotations

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CopyTextButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from src.bot.filters import CommandFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.navigation import NavigationManager
from src.bot.session import UserSession
from src.bot.utils.group_invite import pack_join_group_payload
from src.core.enums import CommandsEnum, ReplyKeyboardTypeEnum
from src.core.fsm_states import TeacherGroupDeleteStates, TeacherGroupEditStates

teacher_group_actions_router = Router()


@teacher_group_actions_router.message(
    CommandFilter(CommandsEnum.TEACHER_GROUP_GET_LINK)
)
async def teacher_group_get_link_handler(
    _: Message, state: FSMContext, session: UserSession
) -> None:
    # Логика ссылки: deep-link в бота, который добавит студента в группу.
    # Текст ответа можно не выносить в TextsRU (по требованию), главное — сама ссылка.
    group_id = await state.get_value("current_group_id", None)
    if not group_id:
        await session.answer(TextsRU.TRY_AGAIN)
        return

    me = await session.message.bot.get_me()
    payload = pack_join_group_payload(int(group_id))
    link = f"https://t.me/{me.username}?start={payload}"
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=TextsRU.TEACHER_GROUP_GET_LINK_BUTTON,
                    copy_text=CopyTextButton(text=link),
                )
            ]
        ]
    )
    await session.answer(TextsRU.TEACHER_GROUP_GET_LINK, reply_markup=kb)


@teacher_group_actions_router.message(CommandFilter(CommandsEnum.TEACHER_GROUP_DELETE))
async def teacher_group_delete_start_handler(
    _: Message, state: FSMContext, session: UserSession
) -> None:
    group_id = await state.get_value("current_group_id", None)
    group_name = await state.get_value("current_group_name", None)
    if not group_id or not group_name:
        await session.answer(TextsRU.TRY_AGAIN)
        return

    nav_manager = NavigationManager(state)
    await nav_manager.set_cancel_target(await nav_manager.get_previous())

    await state.set_state(TeacherGroupDeleteStates.waiting_for_confirm_name)
    await state.update_data(delete_group_id=group_id)

    await session.answer(
        TextsRU.TEACHER_GROUP_DELETE_CONFIRM.format(group_name=group_name)
    )


@teacher_group_actions_router.message(TeacherGroupDeleteStates.waiting_for_confirm_name)
async def teacher_group_delete_confirm_handler(
    message: Message, state: FSMContext, session: UserSession
) -> None:
    group_id = await state.get_value("delete_group_id", None)
    if not group_id:
        await session.answer(TextsRU.TRY_AGAIN)
        return

    result = await session.teacher_manager().delete_group(
        group_id=int(group_id),
        confirm_name=message.text or "",
    )
    if not result.ok:
        if result.error_code == "confirm_name_mismatch":
            await session.answer(TextsRU.TEACHER_GROUP_DELETE_NAME_MISMATCH)
        else:
            await session.answer(TextsRU.TRY_AGAIN)
        return

    nav_manager = NavigationManager(state)
    await nav_manager.clear_cancel_target()
    await nav_manager.clear_state_and_data_keep_navigation()
    await session.answer(TextsRU.TEACHER_GROUP_DELETE_SUCCESS)

    # Показываем обновлённый список групп
    groups_view = await session.teacher_manager().build_groups_page_view(page=1)
    if groups_view:
        await session.answer(
            TextsRU.SELECT_ACTION,
            reply_markup=ReplyKeyboardTypeEnum.TEACHER_GROUPS,
        )
        await session.answer(
            groups_view.text,
            reply_markup=groups_view.keyboard_type,
            keyboard_data=groups_view.keyboard_data,
        )


@teacher_group_actions_router.message(CommandFilter(CommandsEnum.TEACHER_GROUP_EDIT))
async def teacher_group_edit_start_handler(
    _: Message, state: FSMContext, session: UserSession
) -> None:
    group_id = await state.get_value("current_group_id", None)
    group_name = await state.get_value("current_group_name", None)
    if not group_id or not group_name:
        await session.answer(TextsRU.TRY_AGAIN)
        return

    nav_manager = NavigationManager(state)
    await nav_manager.set_cancel_target(await nav_manager.get_previous())

    await state.set_state(TeacherGroupEditStates.waiting_for_new_name)
    await state.update_data(edit_group_id=group_id)

    await session.answer(
        TextsRU.TEACHER_GROUP_EDIT_PROMPT.format(group_name=group_name)
    )


@teacher_group_actions_router.message(TeacherGroupEditStates.waiting_for_new_name)
async def teacher_group_edit_confirm_handler(
    message: Message, state: FSMContext, session: UserSession
) -> None:
    group_id = await state.get_value("edit_group_id", None)
    if not group_id:
        await session.answer(TextsRU.TRY_AGAIN)
        return

    result = await session.teacher_manager().rename_group(
        group_id=int(group_id),
        new_name=message.text or "",
    )
    if not result.ok:
        if result.error_code == "duplicate_name":
            await session.answer(TextsRU.TEACHER_GROUP_EDIT_DUPLICATE_NAME)
        elif result.error_code == "invalid_name":
            await session.answer(TextsRU.TEACHER_GROUP_EDIT_INVALID_NAME)
        else:
            await session.answer(TextsRU.TRY_AGAIN)
        return

    nav_manager = NavigationManager(state)
    await nav_manager.clear_cancel_target()
    await nav_manager.clear_state_and_data_keep_navigation()
    await session.answer(TextsRU.TEACHER_GROUP_EDIT_SUCCESS)

    # Перерисовываем экран группы
    view = await session.teacher_manager().build_group_students_page_view(
        group_id=int(group_id),
        page=1,
    )
    if view:
        await state.update_data(
            current_group_id=view.group_id, current_group_name=view.group_name
        )
        await session.answer(
            TextsRU.SELECT_ACTION,
            reply_markup=ReplyKeyboardTypeEnum.TEACHER_GROUP_VIEW,
        )
        await session.answer(
            view.text,
            reply_markup=view.keyboard_type,
            keyboard_data=view.keyboard_data,
        )
