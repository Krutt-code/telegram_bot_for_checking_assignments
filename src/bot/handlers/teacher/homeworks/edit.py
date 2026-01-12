from __future__ import annotations

from datetime import datetime

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.filters.callback import CallbackFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.navigation import NavigationManager
from src.bot.session import UserSession
from src.core.enums import HomeworkMediaTypeEnum, InlineKeyboardTypeEnum
from src.core.fsm_states import TeacherHomeworkEditStates
from src.core.schemas import (
    InlineButtonSchema,
    PaginatedListKeyboardSchema,
    TeacherHomeworkCallbackSchema,
    TelegramFileCreateSchema,
)
from src.db.services import (
    AnswersService,
    AssignedGroupsService,
    HomeworkFilesService,
    HomeworkGroupsService,
    HomeworksService,
    TeachersService,
)

teacher_homework_edit_router = Router()

_EDIT_HOMEWORK_ID_KEY = "teacher_edit_homework_id"
_EDIT_SOURCE_MSG_ID_KEY = "teacher_edit_source_message_id"
_EDIT_TMP_FILES_KEY = "teacher_edit_tmp_files"
_EDIT_TMP_GROUP_IDS_KEY = "teacher_edit_tmp_group_ids"


def _format_dt(dt: datetime | None) -> str:
    if not dt:
        return ""
    try:
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return str(dt)


def _review_keyboard_data(*, homework_id: int, page: int, total_pages: int) -> dict:
    return PaginatedListKeyboardSchema(
        items=[],
        extra_buttons=[
            InlineButtonSchema(
                text=TextsRU.TEACHER_HOMEWORK_EDIT_BUTTON,
                callback_data=TeacherHomeworkCallbackSchema(
                    action="edit_menu", homework_id=homework_id
                ).pack(),
            ),
            InlineButtonSchema(
                text=TextsRU.TEACHER_HOMEWORK_DELETE_BUTTON,
                callback_data=TeacherHomeworkCallbackSchema(
                    action="delete", homework_id=homework_id
                ).pack(),
            ),
        ],
        pagination={
            "key": "teacher_homeworks",
            "page": page,
            "total_pages": total_pages,
            "hide_if_single_page": True,
        },
    ).model_dump()


async def _refresh_homework_card(
    *,
    state: FSMContext,
    session: UserSession,
    homework_id: int,
    message_id: int,
) -> None:
    hw = await HomeworksService.get_by_id(homework_id)
    if not hw:
        return
    groups = await HomeworkGroupsService.get_groups_by_homework_id(homework_id)
    answers_count = await AnswersService.count_by_homework_id(homework_id)
    groups_txt = (
        ", ".join([g.name for g in groups])
        if groups
        else TextsRU.TEACHER_HOMEWORK_GROUPS_EMPTY
    )
    text = TextsRU.TEACHER_HOMEWORK_VIEW.format(
        title=hw.title,
        end_at=_format_dt(hw.end_at),
        start_at=_format_dt(hw.start_at),
        text=hw.text,
        groups=groups_txt,
        answers_count=answers_count,
    )
    page = int(await state.get_value("teacher_homeworks_current_page", 1) or 1)
    total_pages = int(await state.get_value("teacher_homeworks_total_pages", 1) or 1)
    await session.edit_message(
        text,
        message_id=message_id,
        reply_markup=InlineKeyboardTypeEnum.TEACHER_HOMEWORK_REVIEW,
        keyboard_data=_review_keyboard_data(
            homework_id=homework_id, page=page, total_pages=total_pages
        ),
    )


@teacher_homework_edit_router.callback_query(
    CallbackFilter(TeacherHomeworkCallbackSchema, action="edit_title")
)
async def teacher_homework_edit_title_start(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherHomeworkCallbackSchema,
) -> None:
    await session.answer_callback_query()
    nav_manager = NavigationManager(state)
    await nav_manager.set_cancel_target(await nav_manager.get_previous())
    await state.update_data({_EDIT_HOMEWORK_ID_KEY: callback_data.homework_id})
    await state.update_data({_EDIT_SOURCE_MSG_ID_KEY: session.message.message_id})
    await state.set_state(TeacherHomeworkEditStates.waiting_for_title)
    await session.answer(TextsRU.TEACHER_HOMEWORK_EDIT_TITLE_PROMPT)


@teacher_homework_edit_router.message(
    StateFilter(TeacherHomeworkEditStates.waiting_for_title)
)
async def teacher_homework_edit_title_save(
    message: Message, state: FSMContext, session: UserSession
) -> None:
    homework_id = await state.get_value(_EDIT_HOMEWORK_ID_KEY, None)
    if not homework_id:
        await session.answer(TextsRU.TRY_AGAIN)
        return
    title = (message.text or "").strip()
    if not title:
        await session.answer(TextsRU.TEACHER_HOMEWORK_EDIT_TITLE_EMPTY)
        return
    ok = await HomeworksService.update_title_by_id(int(homework_id), title=title)
    if not ok:
        await session.answer(TextsRU.TRY_AGAIN)
        return
    nav_manager = NavigationManager(state)
    source_mid = await state.get_value(_EDIT_SOURCE_MSG_ID_KEY, None)
    await nav_manager.clear_cancel_target()
    await nav_manager.clear_state_and_data_keep_navigation()
    await session.answer(TextsRU.TEACHER_HOMEWORK_EDIT_SUCCESS)
    if source_mid:
        await _refresh_homework_card(
            state=state,
            session=session,
            homework_id=int(homework_id),
            message_id=int(source_mid),
        )


@teacher_homework_edit_router.callback_query(
    CallbackFilter(TeacherHomeworkCallbackSchema, action="edit_text")
)
async def teacher_homework_edit_text_start(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherHomeworkCallbackSchema,
) -> None:
    await session.answer_callback_query()
    nav_manager = NavigationManager(state)
    await nav_manager.set_cancel_target(await nav_manager.get_previous())
    await state.update_data({_EDIT_HOMEWORK_ID_KEY: callback_data.homework_id})
    await state.update_data({_EDIT_SOURCE_MSG_ID_KEY: session.message.message_id})
    await state.set_state(TeacherHomeworkEditStates.waiting_for_text)
    await session.answer(TextsRU.TEACHER_HOMEWORK_EDIT_TEXT_PROMPT)


@teacher_homework_edit_router.message(
    StateFilter(TeacherHomeworkEditStates.waiting_for_text)
)
async def teacher_homework_edit_text_save(
    message: Message, state: FSMContext, session: UserSession
) -> None:
    homework_id = await state.get_value(_EDIT_HOMEWORK_ID_KEY, None)
    if not homework_id:
        await session.answer(TextsRU.TRY_AGAIN)
        return
    text = (message.text or "").strip()
    if not text:
        await session.answer(TextsRU.TEACHER_HOMEWORK_EDIT_TEXT_EMPTY)
        return
    ok = await HomeworksService.update_text_by_id(int(homework_id), text=text)
    if not ok:
        await session.answer(TextsRU.TRY_AGAIN)
        return
    nav_manager = NavigationManager(state)
    source_mid = await state.get_value(_EDIT_SOURCE_MSG_ID_KEY, None)
    await nav_manager.clear_cancel_target()
    await nav_manager.clear_state_and_data_keep_navigation()
    await session.answer(TextsRU.TEACHER_HOMEWORK_EDIT_SUCCESS)
    if source_mid:
        await _refresh_homework_card(
            state=state,
            session=session,
            homework_id=int(homework_id),
            message_id=int(source_mid),
        )


@teacher_homework_edit_router.callback_query(
    CallbackFilter(TeacherHomeworkCallbackSchema, action="edit_files")
)
async def teacher_homework_edit_files_start(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherHomeworkCallbackSchema,
) -> None:
    await session.answer_callback_query()
    nav_manager = NavigationManager(state)
    await nav_manager.set_cancel_target(await nav_manager.get_previous())
    await state.update_data(
        {
            _EDIT_HOMEWORK_ID_KEY: callback_data.homework_id,
            _EDIT_SOURCE_MSG_ID_KEY: session.message.message_id,
            _EDIT_TMP_FILES_KEY: [],
        }
    )
    await state.set_state(TeacherHomeworkEditStates.waiting_for_files)
    await session.answer(TextsRU.TEACHER_HOMEWORK_EDIT_FILES_PROMPT)


@teacher_homework_edit_router.message(
    StateFilter(TeacherHomeworkEditStates.waiting_for_files)
)
async def teacher_homework_edit_files_collect(
    message: Message, state: FSMContext, session: UserSession
) -> None:
    if (message.text or "").strip() == "/done":
        homework_id = await state.get_value(_EDIT_HOMEWORK_ID_KEY, None)
        source_mid = await state.get_value(_EDIT_SOURCE_MSG_ID_KEY, None)
        files_raw = await state.get_value(_EDIT_TMP_FILES_KEY, []) or []
        if not homework_id:
            await session.answer(TextsRU.TRY_AGAIN)
            return
        await HomeworkFilesService.delete_by_homework_id(int(homework_id))
        await HomeworkFilesService.attach_telegram_files(
            homework_id=int(homework_id),
            telegram_files=[
                TelegramFileCreateSchema.model_validate(x) for x in files_raw
            ],
        )
        nav_manager = NavigationManager(state)
        await nav_manager.clear_cancel_target()
        await nav_manager.clear_state_and_data_keep_navigation()
        await session.answer(TextsRU.TEACHER_HOMEWORK_EDIT_SUCCESS)
        if source_mid:
            await _refresh_homework_card(
                state=state,
                session=session,
                homework_id=int(homework_id),
                message_id=int(source_mid),
            )
        return

    files = await state.get_value(_EDIT_TMP_FILES_KEY, []) or []
    if message.photo:
        ph = message.photo[-1]
        files.append(
            TelegramFileCreateSchema(
                file_id=ph.file_id,
                unique_file_id=ph.file_unique_id,
                file_type=HomeworkMediaTypeEnum.PHOTO.value,
                owner_user_id=session.user_id,
                caption=message.caption,
                mime_type=None,
            ).model_dump()
        )
    elif message.document:
        doc = message.document
        files.append(
            TelegramFileCreateSchema(
                file_id=doc.file_id,
                unique_file_id=doc.file_unique_id,
                file_type=HomeworkMediaTypeEnum.DOCUMENT.value,
                owner_user_id=session.user_id,
                caption=message.caption,
                mime_type=doc.mime_type,
            ).model_dump()
        )
    elif message.video:
        vid = message.video
        files.append(
            TelegramFileCreateSchema(
                file_id=vid.file_id,
                unique_file_id=vid.file_unique_id,
                file_type=HomeworkMediaTypeEnum.VIDEO.value,
                owner_user_id=session.user_id,
                caption=message.caption,
                mime_type=vid.mime_type,
            ).model_dump()
        )
    else:
        await session.answer(TextsRU.TEACHER_HOMEWORK_CREATE_FILES_PHOTO_ONLY)
        return
    await state.update_data({_EDIT_TMP_FILES_KEY: files})
    await session.answer(
        TextsRU.TEACHER_HOMEWORK_EDIT_FILES_ADDED.format(count=len(files))
    )


def _groups_keyboard(*, groups: list, selected_ids: set[int], done_action: str) -> dict:
    extra = []
    for g in groups:
        prefix = (
            TextsRU.TEACHER_HOMEWORK_GROUP_SELECTED_PREFIX
            if g.group_id in selected_ids
            else TextsRU.TEACHER_HOMEWORK_GROUP_UNSELECTED_PREFIX
        )
        extra.append(
            InlineButtonSchema(
                text=f"{prefix} {g.name}",
                callback_data=TeacherHomeworkCallbackSchema(
                    action="grp", homework_id=g.group_id
                ).pack(),
            )
        )
    extra.append(
        InlineButtonSchema(
            text=TextsRU.TEACHER_HOMEWORK_GROUPS_DONE_BUTTON,
            callback_data=TeacherHomeworkCallbackSchema(
                action=done_action, homework_id=0
            ).pack(),
        )
    )
    return PaginatedListKeyboardSchema(items=[], extra_buttons=extra).model_dump()


@teacher_homework_edit_router.callback_query(
    CallbackFilter(TeacherHomeworkCallbackSchema, action="edit_groups")
)
async def teacher_homework_edit_groups_start(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherHomeworkCallbackSchema,
) -> None:
    await session.answer_callback_query()
    teacher = await TeachersService.get_by_user_id(session.user_id)
    if not teacher:
        await session.answer(TextsRU.TEACHER_NOT_FOUND)
        return
    current_groups = await HomeworkGroupsService.get_groups_by_homework_id(
        callback_data.homework_id
    )
    selected = set([g.group_id for g in current_groups])
    await state.update_data(
        {
            _EDIT_HOMEWORK_ID_KEY: callback_data.homework_id,
            _EDIT_SOURCE_MSG_ID_KEY: session.message.message_id,
            _EDIT_TMP_GROUP_IDS_KEY: list(sorted(selected)),
        }
    )
    await state.set_state(TeacherHomeworkEditStates.selecting_groups)
    groups = await AssignedGroupsService.get_all_groups_by_teacher_id(
        teacher.teacher_id
    )
    await session.edit_message(
        session.message.text or "",
        message_id=session.message.message_id,
        reply_markup=InlineKeyboardTypeEnum.TEACHER_HOMEWORK_GROUPS_SELECT,
        keyboard_data=_groups_keyboard(
            groups=groups, selected_ids=selected, done_action="edit_groups_done"
        ),
    )


@teacher_homework_edit_router.callback_query(
    StateFilter(TeacherHomeworkEditStates.selecting_groups),
    CallbackFilter(TeacherHomeworkCallbackSchema, action="grp"),
)
async def teacher_homework_edit_groups_toggle(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherHomeworkCallbackSchema,
) -> None:
    await session.answer_callback_query()
    teacher = await TeachersService.get_by_user_id(session.user_id)
    if not teacher:
        return
    gid = int(callback_data.homework_id)
    selected = set(await state.get_value(_EDIT_TMP_GROUP_IDS_KEY, []) or [])
    if gid in selected:
        selected.remove(gid)
    else:
        selected.add(gid)
    await state.update_data({_EDIT_TMP_GROUP_IDS_KEY: list(sorted(selected))})
    groups = await AssignedGroupsService.get_all_groups_by_teacher_id(
        teacher.teacher_id
    )
    await session.edit_message(
        session.message.text or "",
        message_id=session.message.message_id,
        reply_markup=InlineKeyboardTypeEnum.TEACHER_HOMEWORK_GROUPS_SELECT,
        keyboard_data=_groups_keyboard(
            groups=groups, selected_ids=selected, done_action="edit_groups_done"
        ),
    )


@teacher_homework_edit_router.callback_query(
    StateFilter(TeacherHomeworkEditStates.selecting_groups),
    CallbackFilter(TeacherHomeworkCallbackSchema, action="edit_groups_done"),
)
async def teacher_homework_edit_groups_done(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherHomeworkCallbackSchema,
) -> None:
    await session.answer_callback_query()
    homework_id = await state.get_value(_EDIT_HOMEWORK_ID_KEY, None)
    source_mid = await state.get_value(_EDIT_SOURCE_MSG_ID_KEY, None)
    selected = await state.get_value(_EDIT_TMP_GROUP_IDS_KEY, []) or []
    if not homework_id:
        await session.answer(TextsRU.TRY_AGAIN)
        return
    if not selected:
        await session.answer(TextsRU.TEACHER_HOMEWORK_EDIT_GROUPS_EMPTY)
        return
    await HomeworkGroupsService.set_groups_for_homework(
        homework_id=int(homework_id), group_ids=[int(x) for x in selected]
    )
    nav_manager = NavigationManager(state)
    await nav_manager.clear_cancel_target()
    await nav_manager.clear_state_and_data_keep_navigation()
    await session.answer(TextsRU.TEACHER_HOMEWORK_EDIT_SUCCESS)
    if source_mid:
        await _refresh_homework_card(
            state=state,
            session=session,
            homework_id=int(homework_id),
            message_id=int(source_mid),
        )
