from __future__ import annotations

from datetime import datetime
from typing import Optional

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.filters import CommandFilter
from src.bot.filters.callback import CallbackFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.navigation import NavigationHelper
from src.bot.session import UserSession
from src.core.enums import (
    AnswersStatusEnum,
    CommandsEnum,
    HomeworkMediaTypeEnum,
    InlineKeyboardTypeEnum,
    ReplyKeyboardTypeEnum,
)
from src.core.schemas import (
    InlineButtonSchema,
    PaginatedListKeyboardSchema,
    PaginationCallbackSchema,
    PaginationStateSchema,
    TeacherGradingListCallbackSchema,
    TeacherHomeworkCallbackSchema,
)
from src.db.services import (
    AnswersService,
    HomeworkFilesService,
    HomeworkGroupsService,
    HomeworksService,
    TeachersService,
)

teacher_homeworks_review_router = Router()

_PAGINATION_KEY = "teacher_homeworks"
_PER_PAGE = 1
_STATE_PHOTO_MSG_IDS_KEY = "teacher_homeworks_photo_message_ids"
_STATE_CURRENT_PAGE_KEY = "teacher_homeworks_current_page"
_STATE_TOTAL_PAGES_KEY = "teacher_homeworks_total_pages"


def _format_dt(dt: Optional[datetime]) -> str:
    if not dt:
        return ""
    try:
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return str(dt)


async def _delete_previous_photos(state: FSMContext, session: UserSession) -> None:
    data = await state.get_data()
    msg_ids = data.get(_STATE_PHOTO_MSG_IDS_KEY) or []
    if not isinstance(msg_ids, list) or not msg_ids:
        return
    for mid in msg_ids:
        try:
            await session.delete_message(int(mid))
        except Exception:
            pass
    await state.update_data({_STATE_PHOTO_MSG_IDS_KEY: []})


async def _send_homework_photos(
    *,
    state: FSMContext,
    session: UserSession,
    homework_id: int,
) -> None:
    await _delete_previous_photos(state, session)
    files = await HomeworkFilesService.get_files_by_homework_id(homework_id)
    media_ids: list[int] = []
    for f in files:
        tf = f.telegram_file
        if not tf:
            continue
        try:
            if tf.file_type == HomeworkMediaTypeEnum.PHOTO.value:
                msg = await session.message.answer_photo(photo=tf.file_id)
                media_ids.append(msg.message_id)
            elif tf.file_type == HomeworkMediaTypeEnum.DOCUMENT.value:
                msg = await session.message.answer_document(
                    document=tf.file_id, caption=tf.caption
                )
                media_ids.append(msg.message_id)
            elif tf.file_type == HomeworkMediaTypeEnum.VIDEO.value:
                msg = await session.message.answer_video(
                    video=tf.file_id, caption=tf.caption
                )
                media_ids.append(msg.message_id)
        except Exception:
            continue
    await state.update_data({_STATE_PHOTO_MSG_IDS_KEY: media_ids})


async def _build_homework_view_text(
    *, homework, groups_names: list[str], answers_count: int
) -> str:
    groups = (
        ", ".join(groups_names)
        if groups_names
        else TextsRU.TEACHER_HOMEWORK_GROUPS_EMPTY
    )
    return TextsRU.TEACHER_HOMEWORK_VIEW.format(
        title=homework.title,
        end_at=_format_dt(homework.end_at),
        start_at=_format_dt(homework.start_at),
        text=homework.text,
        groups=groups,
        answers_count=answers_count,
    )


async def _build_homework_view_keyboard(
    *, page: int, total_pages: int, homework_id: int
) -> dict:

    # Проверяем наличие ответов для проверки и проверенных ответов
    sent_count = await AnswersService.count_by_homework_id_and_status(
        homework_id, AnswersStatusEnum.SENT
    )
    reviewed_count = await AnswersService.count_by_homework_id_and_status(
        homework_id, AnswersStatusEnum.REVIEWED
    )

    extra_buttons = []

    # Добавляем кнопку "Проверить" если есть непроверенные ответы
    if sent_count > 0:
        extra_buttons.append(
            InlineButtonSchema(
                text=TextsRU.TEACHER_GRADING_CHECK_BUTTON,
                callback_data=TeacherGradingListCallbackSchema(
                    action="check_answers",
                    homework_id=homework_id,
                ).pack(),
            )
        )

    # Добавляем кнопку "Оцененные" если есть проверенные ответы
    if reviewed_count > 0:
        extra_buttons.append(
            InlineButtonSchema(
                text=TextsRU.TEACHER_GRADING_REVIEWED_BUTTON,
                callback_data=TeacherGradingListCallbackSchema(
                    action="reviewed_answers",
                    homework_id=homework_id,
                ).pack(),
            )
        )

    # Стандартные кнопки редактирования и удаления
    extra_buttons.extend(
        [
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
        ]
    )

    return PaginatedListKeyboardSchema(
        items=[],
        extra_buttons=extra_buttons,
        pagination=PaginationStateSchema(
            key=_PAGINATION_KEY, page=page, total_pages=total_pages
        ),
    ).model_dump()


@teacher_homeworks_review_router.message(CommandFilter(CommandsEnum.TEACHER_HOMEWORKS))
async def teacher_homeworks_review_handler(
    _: Message, state: FSMContext, session: UserSession
) -> None:
    await NavigationHelper.register_navigation_step(
        state,
        CommandsEnum.TEACHER_HOMEWORKS,
        ReplyKeyboardTypeEnum.TEACHER_HOMEWORKS,
        TextsRU.SELECT_ACTION,
    )

    teacher = await TeachersService.get_by_user_id(session.user_id)
    if not teacher:
        await session.answer(TextsRU.TEACHER_NOT_FOUND)
        return

    # reply-меню действий
    await session.answer(
        TextsRU.SELECT_ACTION, reply_markup=ReplyKeyboardTypeEnum.TEACHER_HOMEWORKS
    )

    page_data = await HomeworksService.get_homeworks_page_by_teacher_id(
        teacher.teacher_id, page=1, per_page=_PER_PAGE
    )
    if not page_data.items:
        await session.answer(
            TextsRU.TEACHER_HOMEWORKS_EMPTY,
            reply_markup=ReplyKeyboardTypeEnum.TEACHER_HOMEWORKS,
        )
        return
    await state.update_data(
        {
            _STATE_CURRENT_PAGE_KEY: page_data.page,
            _STATE_TOTAL_PAGES_KEY: page_data.total_pages,
        }
    )

    hw = page_data.items[0]
    groups = await HomeworkGroupsService.get_groups_by_homework_id(hw.homework_id)
    answers_count = await AnswersService.count_by_homework_id(hw.homework_id)

    await _send_homework_photos(
        state=state, session=session, homework_id=hw.homework_id
    )
    await session.answer(
        await _build_homework_view_text(
            homework=hw,
            groups_names=[g.name for g in groups],
            answers_count=answers_count,
        ),
        reply_markup=InlineKeyboardTypeEnum.TEACHER_HOMEWORK_REVIEW,
        keyboard_data=await _build_homework_view_keyboard(
            page=page_data.page,
            total_pages=page_data.total_pages,
            homework_id=hw.homework_id,
        ),
    )


@teacher_homeworks_review_router.callback_query(
    CallbackFilter(PaginationCallbackSchema, key=_PAGINATION_KEY)
)
async def teacher_homeworks_pagination_handler(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: PaginationCallbackSchema,
) -> None:
    await session.answer_callback_query()

    teacher = await TeachersService.get_by_user_id(session.user_id)
    if not teacher:
        await session.answer(TextsRU.TEACHER_NOT_FOUND)
        return

    page_data = await HomeworksService.get_homeworks_page_by_teacher_id(
        teacher.teacher_id, page=callback_data.page, per_page=_PER_PAGE
    )
    if not page_data.items:
        await session.edit_message(
            TextsRU.TEACHER_HOMEWORKS_EMPTY,
            message_id=session.message.message_id,
            reply_markup=None,
        )
        await _delete_previous_photos(state, session)
        return
    await state.update_data(
        {
            _STATE_CURRENT_PAGE_KEY: page_data.page,
            _STATE_TOTAL_PAGES_KEY: page_data.total_pages,
        }
    )

    hw = page_data.items[0]
    groups = await HomeworkGroupsService.get_groups_by_homework_id(hw.homework_id)
    answers_count = await AnswersService.count_by_homework_id(hw.homework_id)

    await _send_homework_photos(
        state=state, session=session, homework_id=hw.homework_id
    )
    await session.edit_message(
        await _build_homework_view_text(
            homework=hw,
            groups_names=[g.name for g in groups],
            answers_count=answers_count,
        ),
        message_id=session.message.message_id,
        reply_markup=InlineKeyboardTypeEnum.TEACHER_HOMEWORK_REVIEW,
        keyboard_data=await _build_homework_view_keyboard(
            page=page_data.page,
            total_pages=page_data.total_pages,
            homework_id=hw.homework_id,
        ),
    )
