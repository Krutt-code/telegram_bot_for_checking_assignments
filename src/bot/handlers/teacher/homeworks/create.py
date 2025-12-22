from __future__ import annotations

from datetime import datetime
from typing import Optional

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.filters import CommandFilter
from src.bot.filters.callback import CallbackFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.navigation import NavigationManager
from src.bot.session import UserSession
from src.core.enums import CommandsEnum, HomeworkMediaTypeEnum, InlineKeyboardTypeEnum
from src.core.fsm_states import TeacherHomeworkCreateStates
from src.core.schemas import (
    HomeworkCreateSchema,
    InlineButtonSchema,
    PaginatedListKeyboardSchema,
    TeacherHomeworkCallbackSchema,
    TelegramFileCreateSchema,
)
from src.db.services import (
    AssignedGroupsService,
    HomeworkFilesService,
    HomeworkGroupsService,
    HomeworksService,
    TeachersService,
)

teacher_homework_create_router = Router()

_TMP_FILES_KEY = "teacher_homework_tmp_files"
_TMP_GROUP_IDS_KEY = "teacher_homework_tmp_group_ids"


def _parse_deadline(raw: str) -> Optional[datetime]:
    raw = (raw or "").strip()
    if not raw:
        return None
    # ожидаем: "ДД.ММ.ГГГГ ЧЧ:ММ"
    for fmt in ("%d.%m.%Y %H:%M", "%d.%m.%Y"):
        try:
            dt = datetime.strptime(raw, fmt)
            if fmt == "%d.%m.%Y":
                dt = dt.replace(hour=23, minute=59)
            return dt
        except Exception:
            continue
    return None


def _groups_keyboard(*, groups: list, selected_ids: set[int]) -> dict:
    items = []
    for g in groups:
        prefix = (
            TextsRU.TEACHER_HOMEWORK_GROUP_SELECTED_PREFIX
            if g.group_id in selected_ids
            else TextsRU.TEACHER_HOMEWORK_GROUP_UNSELECTED_PREFIX
        )
        items.append(
            InlineButtonSchema(
                text=f"{prefix} {g.name}",
                callback_data=TeacherHomeworkCallbackSchema(
                    action="grp", homework_id=g.group_id
                ).pack(),
            )
        )
    # paginated_list_inline expects items as list[PaginatedListItemSchema], but it also accepts InlineButtonSchema-like dicts.
    return PaginatedListKeyboardSchema(
        items=[],
        extra_buttons=[
            InlineButtonSchema(text=b.text, callback_data=b.callback_data)
            for b in items
        ]
        + [
            InlineButtonSchema(
                text=TextsRU.TEACHER_HOMEWORK_GROUPS_DONE_BUTTON,
                callback_data=TeacherHomeworkCallbackSchema(
                    action="groups_done", homework_id=0
                ).pack(),
            )
        ],
    ).model_dump()


def _confirm_keyboard() -> dict:
    return PaginatedListKeyboardSchema(
        items=[],
        extra_buttons=[
            InlineButtonSchema(
                text=TextsRU.TEACHER_HOMEWORK_CONFIRM_CREATE_BUTTON,
                callback_data=TeacherHomeworkCallbackSchema(
                    action="create_confirm", homework_id=0
                ).pack(),
            ),
            InlineButtonSchema(
                text=TextsRU.TEACHER_HOMEWORK_CANCEL_CREATE_BUTTON,
                callback_data=TeacherHomeworkCallbackSchema(
                    action="create_cancel", homework_id=0
                ).pack(),
            ),
        ],
    ).model_dump()


@teacher_homework_create_router.message(
    CommandFilter(CommandsEnum.TEACHER_HOMEWORK_CREATE)
)
async def teacher_homework_create_start(
    _: Message, state: FSMContext, session: UserSession
) -> None:
    nav_manager = NavigationManager(state)
    await nav_manager.set_cancel_target(await nav_manager.get_previous())

    await state.set_state(TeacherHomeworkCreateStates.waiting_for_title)
    await state.update_data({_TMP_FILES_KEY: [], _TMP_GROUP_IDS_KEY: []})
    await session.answer(TextsRU.TEACHER_HOMEWORK_CREATE_TITLE_PROMPT)


@teacher_homework_create_router.message(TeacherHomeworkCreateStates.waiting_for_title)
async def teacher_homework_create_title(
    message: Message, state: FSMContext, session: UserSession
) -> None:
    title = (message.text or "").strip()
    if not title:
        await session.answer(TextsRU.TEACHER_HOMEWORK_CREATE_TITLE_EMPTY)
        return
    await state.update_data(title=title)
    await state.set_state(TeacherHomeworkCreateStates.waiting_for_text)
    await session.answer(TextsRU.TEACHER_HOMEWORK_CREATE_TEXT_PROMPT)


@teacher_homework_create_router.message(TeacherHomeworkCreateStates.waiting_for_text)
async def teacher_homework_create_text(
    message: Message, state: FSMContext, session: UserSession
) -> None:
    text = (message.text or "").strip()
    if not text:
        await session.answer(TextsRU.TEACHER_HOMEWORK_CREATE_TEXT_EMPTY)
        return
    await state.update_data(text=text)
    await state.set_state(TeacherHomeworkCreateStates.waiting_for_deadline)
    await session.answer(TextsRU.TEACHER_HOMEWORK_CREATE_DEADLINE_PROMPT)


@teacher_homework_create_router.message(
    TeacherHomeworkCreateStates.waiting_for_deadline
)
async def teacher_homework_create_deadline(
    message: Message, state: FSMContext, session: UserSession
) -> None:
    dt = _parse_deadline(message.text or "")
    if not dt:
        await session.answer(TextsRU.TEACHER_HOMEWORK_CREATE_DEADLINE_INVALID)
        return
    if dt <= datetime.now():
        await session.answer(TextsRU.TEACHER_HOMEWORK_CREATE_DEADLINE_PAST)
        return
    await state.update_data(end_at=dt.isoformat())
    await state.set_state(TeacherHomeworkCreateStates.waiting_for_files)
    await session.answer(TextsRU.TEACHER_HOMEWORK_CREATE_FILES_PROMPT)


@teacher_homework_create_router.message(TeacherHomeworkCreateStates.waiting_for_files)
async def teacher_homework_create_files(
    message: Message, state: FSMContext, session: UserSession
) -> None:
    """
    Собираем фото как вложения к заданию. Командой /done завершаем шаг и переходим к выбору групп.
    """
    # allow finish via command text
    if (message.text or "").strip() == "/done":
        await state.set_state(TeacherHomeworkCreateStates.selecting_groups)
        teacher = await TeachersService.get_by_user_id(session.user_id)
        if not teacher:
            await session.answer(TextsRU.TEACHER_NOT_FOUND)
            return
        groups = await AssignedGroupsService.get_all_groups_by_teacher_id(
            teacher.teacher_id
        )
        selected = set(await state.get_value(_TMP_GROUP_IDS_KEY, []) or [])
        await session.answer(
            TextsRU.TEACHER_HOMEWORK_CREATE_GROUPS_PROMPT,
            reply_markup=InlineKeyboardTypeEnum.TEACHER_HOMEWORK_GROUPS_SELECT,
            keyboard_data=_groups_keyboard(groups=groups, selected_ids=selected),
        )
        return

    files = await state.get_value(_TMP_FILES_KEY, []) or []
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
    await state.update_data({_TMP_FILES_KEY: files})
    await session.answer(
        TextsRU.TEACHER_HOMEWORK_CREATE_FILES_ADDED.format(count=len(files))
    )


@teacher_homework_create_router.callback_query(
    StateFilter(TeacherHomeworkCreateStates.selecting_groups),
    CallbackFilter(TeacherHomeworkCallbackSchema, action="grp"),
)
async def teacher_homework_create_toggle_group(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherHomeworkCallbackSchema,
) -> None:
    await session.answer_callback_query()
    gid = int(callback_data.homework_id)
    selected = set(await state.get_value(_TMP_GROUP_IDS_KEY, []) or [])
    if gid in selected:
        selected.remove(gid)
    else:
        selected.add(gid)
    await state.update_data({_TMP_GROUP_IDS_KEY: list(sorted(selected))})

    teacher = await TeachersService.get_by_user_id(session.user_id)
    if not teacher:
        return
    groups = await AssignedGroupsService.get_all_groups_by_teacher_id(
        teacher.teacher_id
    )
    await session.edit_message(
        TextsRU.TEACHER_HOMEWORK_CREATE_GROUPS_PROMPT,
        message_id=session.message.message_id,
        reply_markup=InlineKeyboardTypeEnum.TEACHER_HOMEWORK_GROUPS_SELECT,
        keyboard_data=_groups_keyboard(groups=groups, selected_ids=selected),
    )


@teacher_homework_create_router.callback_query(
    StateFilter(TeacherHomeworkCreateStates.selecting_groups),
    CallbackFilter(TeacherHomeworkCallbackSchema, action="groups_done"),
)
async def teacher_homework_create_groups_done(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherHomeworkCallbackSchema,
) -> None:
    await session.answer_callback_query()
    selected = await state.get_value(_TMP_GROUP_IDS_KEY, []) or []
    if not selected:
        await session.answer(TextsRU.TEACHER_HOMEWORK_CREATE_GROUPS_EMPTY)
        return

    data = await state.get_data()
    title = data.get("title", "")
    text = data.get("text", "")
    end_at = datetime.fromisoformat(data.get("end_at"))
    await state.set_state(TeacherHomeworkCreateStates.confirming)
    await session.edit_message(
        TextsRU.TEACHER_HOMEWORK_PREVIEW.format(
            title=title,
            text=text,
            end_at=end_at.strftime("%d.%m.%Y %H:%M"),
            groups_count=len(selected),
        ),
        message_id=session.message.message_id,
        reply_markup=InlineKeyboardTypeEnum.TEACHER_HOMEWORK_CONFIRM,
        keyboard_data=_confirm_keyboard(),
    )


@teacher_homework_create_router.callback_query(
    StateFilter(TeacherHomeworkCreateStates.confirming),
    CallbackFilter(TeacherHomeworkCallbackSchema, action="create_cancel"),
)
async def teacher_homework_create_cancel(
    _: CallbackQuery, state: FSMContext, session: UserSession
) -> None:
    await session.answer_callback_query()
    nav_manager = NavigationManager(state)
    await nav_manager.clear_state_and_data_keep_navigation()
    await session.answer(TextsRU.CANCEL)


@teacher_homework_create_router.callback_query(
    StateFilter(TeacherHomeworkCreateStates.confirming),
    CallbackFilter(TeacherHomeworkCallbackSchema, action="create_confirm"),
)
async def teacher_homework_create_confirm(
    _: CallbackQuery, state: FSMContext, session: UserSession
) -> None:
    await session.answer_callback_query()
    teacher = await TeachersService.get_by_user_id(session.user_id)
    if not teacher:
        await session.answer(TextsRU.TEACHER_NOT_FOUND)
        return

    data = await state.get_data()
    title = data.get("title", "")
    text = data.get("text", "")
    end_at = datetime.fromisoformat(data.get("end_at"))
    files_raw = data.get(_TMP_FILES_KEY, []) or []
    group_ids = data.get(_TMP_GROUP_IDS_KEY, []) or []

    homework_id = await HomeworksService.create(
        HomeworkCreateSchema(
            teacher_id=teacher.teacher_id,
            title=title,
            text=text,
            start_at=datetime.now(),
            end_at=end_at,
            created_at=datetime.now(),
        )
    )
    await HomeworkGroupsService.set_groups_for_homework(
        homework_id=homework_id, group_ids=[int(x) for x in group_ids]
    )
    await HomeworkFilesService.attach_telegram_files(
        homework_id=homework_id,
        telegram_files=[TelegramFileCreateSchema.model_validate(x) for x in files_raw],
    )

    nav_manager = NavigationManager(state)
    await nav_manager.clear_state_and_data_keep_navigation()
    await session.answer(TextsRU.TEACHER_HOMEWORK_CREATE_SUCCESS)
