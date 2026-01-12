"""
Обработчики для проверки и оценивания ответов студентов.

Функциональность:
- Просмотр непроверенных ответов с пагинацией
- Просмотр проверенных ответов с пагинацией
- Выставление оценки (0-100 баллов)
- Добавление комментария
- Отправка оценки студенту
- Редактирование оценки
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.filters.callback import CallbackFilter
from src.bot.lexicon.texts import TextsRU
from src.bot.navigation import NavigationManager
from src.bot.session import UserSession
from src.core.enums import (
    AnswersStatusEnum,
    HomeworkMediaTypeEnum,
    InlineKeyboardTypeEnum,
    ReplyKeyboardTypeEnum,
)
from src.core.fsm_states import TeacherAnswerGradingStates
from src.core.logger import get_logger
from src.core.schemas import (
    InlineButtonSchema,
    PaginatedListKeyboardSchema,
    PaginationCallbackSchema,
    PaginationStateSchema,
    TeacherGradingCallbackSchema,
    TeacherGradingListCallbackSchema,
)
from src.db.services import AnswerFilesService, AnswersService, HomeworksService

teacher_grading_router = Router()
logger = get_logger(__name__)

_PAGINATION_KEY_CHECK = "teacher_grading_check"
_PAGINATION_KEY_REVIEWED = "teacher_grading_reviewed"
_PER_PAGE = 1

# Ключи для хранения данных в FSMContext
_STATE_EDITING_MESSAGE_ID = "grading_editing_message_id"
_STATE_CURRENT_ANSWER_ID = "grading_current_answer_id"
_STATE_CURRENT_HOMEWORK_ID = "grading_current_homework_id"
_STATE_CURRENT_PAGE = "grading_current_page"
_STATE_TOTAL_PAGES = "grading_total_pages"
_STATE_TEMP_GRADE = "grading_temp_grade"
_STATE_TEMP_COMMENT = "grading_temp_comment"
_STATE_IS_SENT = "grading_is_sent"
_STATE_MODE = "grading_mode"  # "check" или "reviewed"
_STATE_PHOTO_MSG_IDS = "grading_photo_message_ids"


def _format_dt(dt: Optional[datetime]) -> str:
    """Форматирование даты и времени"""
    if not dt:
        return ""
    try:
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return str(dt)


async def _delete_previous_photos(state: FSMContext, session: UserSession) -> None:
    """Удаление предыдущих фото из чата"""
    data = await state.get_data()
    msg_ids = data.get(_STATE_PHOTO_MSG_IDS) or []
    if not isinstance(msg_ids, list) or not msg_ids:
        return
    for mid in msg_ids:
        try:
            await session.delete_message(int(mid))
        except Exception:
            pass
    await state.update_data({_STATE_PHOTO_MSG_IDS: []})


async def _send_answer_files(
    *,
    state: FSMContext,
    session: UserSession,
    answer_id: int,
) -> None:
    """Отправка файлов, прикрепленных к ответу"""
    await _delete_previous_photos(state, session)

    files = await AnswerFilesService.get_files_by_answer_id(answer_id)
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
    await state.update_data({_STATE_PHOTO_MSG_IDS: media_ids})


def _build_answer_text(
    answer, temp_grade: Optional[int] = None, temp_comment: Optional[str] = None
) -> str:
    """Формирование текста для отображения ответа с визуальной индикацией"""
    student_name = (
        answer.student.user.real_full_name
        if answer.student and answer.student.user
        else "Неизвестно"
    )
    group_name = (
        answer.student.group.name
        if answer.student and answer.student.group
        else "Без группы"
    )
    answer_text = answer.student_answer or TextsRU.TEACHER_GRADING_ANSWER_NO_TEXT
    sent_at = _format_dt(answer.sent_at)

    # Визуальная индикация наличия оценки и комментария
    if temp_grade is not None:
        grade_status = TextsRU.TEACHER_GRADING_GRADE_STATUS_SET.format(grade=temp_grade)
    else:
        grade_status = TextsRU.TEACHER_GRADING_GRADE_STATUS_NOT_SET

    if temp_comment:
        # Обрезаем длинный комментарий для предпросмотра
        comment_preview = (
            temp_comment[:50] + "..." if len(temp_comment) > 50 else temp_comment
        )
        comment_status = TextsRU.TEACHER_GRADING_COMMENT_STATUS_SET.format(
            comment_preview=comment_preview
        )
    else:
        comment_status = TextsRU.TEACHER_GRADING_COMMENT_STATUS_NOT_SET

    return TextsRU.TEACHER_GRADING_ANSWER_VIEW.format(
        student_name=student_name,
        group_name=group_name,
        answer_text=answer_text,
        sent_at=sent_at,
        grade_status=grade_status,
        comment_status=comment_status,
    )


def _build_reviewed_answer_text(answer) -> str:
    """Формирование текста для отображения проверенного ответа"""
    student_name = (
        answer.student.user.real_full_name
        if answer.student and answer.student.user
        else "Неизвестно"
    )
    group_name = (
        answer.student.group.name
        if answer.student and answer.student.group
        else "Без группы"
    )
    answer_text = answer.student_answer or TextsRU.TEACHER_GRADING_ANSWER_NO_TEXT
    grade = answer.grade if answer.grade is not None else 0
    comment = answer.teacher_comment or TextsRU.TEACHER_GRADING_NO_COMMENT
    checked_at = _format_dt(answer.checked_at)

    return TextsRU.TEACHER_GRADING_REVIEWED_VIEW.format(
        student_name=student_name,
        group_name=group_name,
        answer_text=answer_text,
        grade=grade,
        comment=comment,
        checked_at=checked_at,
    )


def _build_grading_keyboard(
    *,
    homework_id: int,
    answer_id: int,
    page: int,
    total_pages: int,
    has_grade: bool = False,
    has_comment: bool = False,
    is_sent: bool = False,
) -> dict:
    """Клавиатура для проверки ответа с визуальной индикацией"""
    extra_buttons = []

    # Кнопка установки оценки (с галочкой если есть)
    grade_text = (
        f"✅ {TextsRU.TEACHER_GRADING_SET_GRADE_BUTTON}"
        if has_grade
        else TextsRU.TEACHER_GRADING_SET_GRADE_BUTTON
    )
    extra_buttons.append(
        InlineButtonSchema(
            text=grade_text,
            callback_data=TeacherGradingCallbackSchema(
                action="set_grade",
                homework_id=homework_id,
                answer_id=answer_id,
            ).pack(),
        )
    )

    # Кнопка комментария (с галочкой если есть)
    comment_text = (
        f"✅ {TextsRU.TEACHER_GRADING_SET_COMMENT_BUTTON}"
        if has_comment
        else TextsRU.TEACHER_GRADING_SET_COMMENT_BUTTON
    )
    extra_buttons.append(
        InlineButtonSchema(
            text=comment_text,
            callback_data=TeacherGradingCallbackSchema(
                action="set_comment",
                homework_id=homework_id,
                answer_id=answer_id,
            ).pack(),
        )
    )

    # Кнопка очистки (если есть что очищать и еще не отправлено)
    if (has_grade or has_comment) and not is_sent:
        extra_buttons.append(
            InlineButtonSchema(
                text=TextsRU.TEACHER_GRADING_CLEAR_BUTTON,
                callback_data=TeacherGradingCallbackSchema(
                    action="clear_grade",
                    homework_id=homework_id,
                    answer_id=answer_id,
                ).pack(),
            )
        )

    # Кнопка отправки
    send_text = (
        TextsRU.TEACHER_GRADING_SENT_BUTTON
        if is_sent
        else TextsRU.TEACHER_GRADING_SEND_BUTTON
    )
    extra_buttons.append(
        InlineButtonSchema(
            text=send_text,
            callback_data=TeacherGradingCallbackSchema(
                action="send_grade",
                homework_id=homework_id,
                answer_id=answer_id,
            ).pack(),
        )
    )

    return PaginatedListKeyboardSchema(
        items=[],
        extra_buttons=extra_buttons,
        pagination=PaginationStateSchema(
            key=_PAGINATION_KEY_CHECK,
            page=page,
            total_pages=total_pages,
            hide_if_single_page=False,
        ),
    ).model_dump()


def _build_reviewed_keyboard(
    *,
    homework_id: int,
    answer_id: int,
    page: int,
    total_pages: int,
) -> dict:
    """Клавиатура для просмотра проверенного ответа"""
    extra_buttons = [
        InlineButtonSchema(
            text=TextsRU.TEACHER_GRADING_EDIT_GRADE_BUTTON,
            callback_data=TeacherGradingCallbackSchema(
                action="edit_grade",
                homework_id=homework_id,
                answer_id=answer_id,
            ).pack(),
        ),
        InlineButtonSchema(
            text=TextsRU.TEACHER_GRADING_EDIT_COMMENT_BUTTON,
            callback_data=TeacherGradingCallbackSchema(
                action="edit_comment",
                homework_id=homework_id,
                answer_id=answer_id,
            ).pack(),
        ),
    ]

    return PaginatedListKeyboardSchema(
        items=[],
        extra_buttons=extra_buttons,
        pagination=PaginationStateSchema(
            key=_PAGINATION_KEY_REVIEWED,
            page=page,
            total_pages=total_pages,
            hide_if_single_page=False,
        ),
    ).model_dump()


# ==================== Обработчики для кнопок "Проверить" и "Оцененные" ====================


@teacher_grading_router.callback_query(
    CallbackFilter(TeacherGradingListCallbackSchema, action="check_answers")
)
async def show_answers_to_check_handler(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherGradingListCallbackSchema,
) -> None:
    """Показать непроверенные ответы на задание"""
    await session.answer_callback_query()

    # Устанавливаем cancel_target для возврата к списку заданий
    nav_manager = NavigationManager(state)
    await nav_manager.set_cancel_target(await nav_manager.get_previous())

    # Сначала удаляем все предыдущие фото/файлы (от задания)
    await _delete_previous_photos(state, session)

    # Получаем ответы со статусом SENT
    page_data = await AnswersService.get_answers_page_by_homework_id(
        homework_id=callback_data.homework_id,
        status=AnswersStatusEnum.SENT,
        page=1,
        per_page=_PER_PAGE,
    )

    if not page_data.items:
        await session.edit_message(
            TextsRU.TEACHER_GRADING_NO_ANSWERS_TO_CHECK,
            message_id=session.message.message_id,
            reply_markup=None,
        )
        return

    answer = page_data.items[0]

    # Сохраняем данные в state
    await state.update_data(
        {
            _STATE_EDITING_MESSAGE_ID: session.message.message_id,
            _STATE_CURRENT_ANSWER_ID: answer.answer_id,
            _STATE_CURRENT_HOMEWORK_ID: callback_data.homework_id,
            _STATE_CURRENT_PAGE: page_data.page,
            _STATE_TOTAL_PAGES: page_data.total_pages,
            _STATE_MODE: "check",
            _STATE_IS_SENT: False,
            _STATE_TEMP_GRADE: None,
            _STATE_TEMP_COMMENT: None,
        }
    )

    # Отправляем файлы ответа
    await _send_answer_files(state=state, session=session, answer_id=answer.answer_id)

    # Отправляем сообщение с ответом
    await session.edit_message(
        _build_answer_text(answer, temp_grade=None, temp_comment=None),
        message_id=session.message.message_id,
        reply_markup=InlineKeyboardTypeEnum.TEACHER_GRADING_CHECK,
        keyboard_data=_build_grading_keyboard(
            homework_id=callback_data.homework_id,
            answer_id=answer.answer_id,
            page=page_data.page,
            total_pages=page_data.total_pages,
            has_grade=False,
            has_comment=False,
            is_sent=False,
        ),
    )


@teacher_grading_router.callback_query(
    CallbackFilter(TeacherGradingListCallbackSchema, action="reviewed_answers")
)
async def show_reviewed_answers_handler(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherGradingListCallbackSchema,
) -> None:
    """Показать проверенные ответы на задание"""
    await session.answer_callback_query()

    # Устанавливаем cancel_target для возврата к списку заданий
    nav_manager = NavigationManager(state)
    await nav_manager.set_cancel_target(await nav_manager.get_previous())

    # Сначала удаляем все предыдущие фото/файлы (от задания)
    await _delete_previous_photos(state, session)

    # Получаем ответы со статусом REVIEWED
    page_data = await AnswersService.get_answers_page_by_homework_id(
        homework_id=callback_data.homework_id,
        status=AnswersStatusEnum.REVIEWED,
        page=1,
        per_page=_PER_PAGE,
    )

    if not page_data.items:
        await session.edit_message(
            TextsRU.TEACHER_GRADING_NO_REVIEWED_ANSWERS,
            message_id=session.message.message_id,
            reply_markup=None,
        )
        return

    answer = page_data.items[0]

    # Сохраняем данные в state
    await state.update_data(
        {
            _STATE_EDITING_MESSAGE_ID: session.message.message_id,
            _STATE_CURRENT_ANSWER_ID: answer.answer_id,
            _STATE_CURRENT_HOMEWORK_ID: callback_data.homework_id,
            _STATE_CURRENT_PAGE: page_data.page,
            _STATE_TOTAL_PAGES: page_data.total_pages,
            _STATE_MODE: "reviewed",
        }
    )

    # Отправляем файлы ответа
    await _send_answer_files(state=state, session=session, answer_id=answer.answer_id)

    # Отправляем сообщение с проверенным ответом
    await session.edit_message(
        _build_reviewed_answer_text(answer),
        message_id=session.message.message_id,
        reply_markup=InlineKeyboardTypeEnum.TEACHER_GRADING_REVIEWED,
        keyboard_data=_build_reviewed_keyboard(
            homework_id=callback_data.homework_id,
            answer_id=answer.answer_id,
            page=page_data.page,
            total_pages=page_data.total_pages,
        ),
    )


# ==================== Пагинация ====================


@teacher_grading_router.callback_query(
    CallbackFilter(PaginationCallbackSchema, key=_PAGINATION_KEY_CHECK)
)
async def grading_check_pagination_handler(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: PaginationCallbackSchema,
) -> None:
    """Пагинация по непроверенным ответам"""
    await session.answer_callback_query()

    data = await state.get_data()
    homework_id = data.get(_STATE_CURRENT_HOMEWORK_ID)
    editing_message_id = data.get(_STATE_EDITING_MESSAGE_ID, session.message.message_id)

    if not homework_id:
        await session.answer(TextsRU.TRY_AGAIN)
        return

    page_data = await AnswersService.get_answers_page_by_homework_id(
        homework_id=int(homework_id),
        status=AnswersStatusEnum.SENT,
        page=callback_data.page,
        per_page=_PER_PAGE,
    )

    if not page_data.items:
        await session.edit_message(
            TextsRU.TEACHER_GRADING_NO_ANSWERS_TO_CHECK,
            message_id=editing_message_id,
            reply_markup=None,
        )
        await _delete_previous_photos(state, session)
        return

    answer = page_data.items[0]

    # Обновляем данные в state (сохраняем editing_message_id, сбрасываем временные данные)
    await state.update_data(
        {
            _STATE_CURRENT_ANSWER_ID: answer.answer_id,
            _STATE_CURRENT_PAGE: page_data.page,
            _STATE_TOTAL_PAGES: page_data.total_pages,
            _STATE_EDITING_MESSAGE_ID: editing_message_id,
            _STATE_IS_SENT: False,
            _STATE_TEMP_GRADE: None,
            _STATE_TEMP_COMMENT: None,
        }
    )

    # Отправляем файлы ответа
    await _send_answer_files(state=state, session=session, answer_id=answer.answer_id)

    # Обновляем сообщение (сбрасываем временные данные для нового ответа)
    await session.edit_message(
        _build_answer_text(answer, temp_grade=None, temp_comment=None),
        message_id=editing_message_id,
        reply_markup=InlineKeyboardTypeEnum.TEACHER_GRADING_CHECK,
        keyboard_data=_build_grading_keyboard(
            homework_id=int(homework_id),
            answer_id=answer.answer_id,
            page=page_data.page,
            total_pages=page_data.total_pages,
            has_grade=False,
            has_comment=False,
            is_sent=False,
        ),
    )


@teacher_grading_router.callback_query(
    CallbackFilter(PaginationCallbackSchema, key=_PAGINATION_KEY_REVIEWED)
)
async def grading_reviewed_pagination_handler(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: PaginationCallbackSchema,
) -> None:
    """Пагинация по проверенным ответам"""
    await session.answer_callback_query()

    data = await state.get_data()
    homework_id = data.get(_STATE_CURRENT_HOMEWORK_ID)
    editing_message_id = data.get(_STATE_EDITING_MESSAGE_ID, session.message.message_id)

    if not homework_id:
        await session.answer(TextsRU.TRY_AGAIN)
        return

    page_data = await AnswersService.get_answers_page_by_homework_id(
        homework_id=int(homework_id),
        status=AnswersStatusEnum.REVIEWED,
        page=callback_data.page,
        per_page=_PER_PAGE,
    )

    if not page_data.items:
        await session.edit_message(
            TextsRU.TEACHER_GRADING_NO_REVIEWED_ANSWERS,
            message_id=editing_message_id,
            reply_markup=None,
        )
        await _delete_previous_photos(state, session)
        return

    answer = page_data.items[0]

    # Обновляем данные в state (сохраняем editing_message_id)
    await state.update_data(
        {
            _STATE_CURRENT_ANSWER_ID: answer.answer_id,
            _STATE_CURRENT_PAGE: page_data.page,
            _STATE_TOTAL_PAGES: page_data.total_pages,
            _STATE_EDITING_MESSAGE_ID: editing_message_id,
        }
    )

    # Отправляем файлы ответа
    await _send_answer_files(state=state, session=session, answer_id=answer.answer_id)

    # Обновляем сообщение
    await session.edit_message(
        _build_reviewed_answer_text(answer),
        message_id=editing_message_id,
        reply_markup=InlineKeyboardTypeEnum.TEACHER_GRADING_REVIEWED,
        keyboard_data=_build_reviewed_keyboard(
            homework_id=int(homework_id),
            answer_id=answer.answer_id,
            page=page_data.page,
            total_pages=page_data.total_pages,
        ),
    )


# ==================== Установка оценки ====================


@teacher_grading_router.callback_query(
    CallbackFilter(TeacherGradingCallbackSchema, action="set_grade")
)
async def set_grade_start_handler(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherGradingCallbackSchema,
) -> None:
    """Начало установки оценки"""
    await session.answer_callback_query()

    await state.set_state(TeacherAnswerGradingStates.waiting_for_grade)
    await state.update_data(
        {
            _STATE_CURRENT_ANSWER_ID: callback_data.answer_id,
            _STATE_CURRENT_HOMEWORK_ID: callback_data.homework_id,
        }
    )

    await session.answer(TextsRU.TEACHER_GRADING_ENTER_GRADE)


@teacher_grading_router.message(TeacherAnswerGradingStates.waiting_for_grade)
async def set_grade_process_handler(
    message: Message,
    state: FSMContext,
    session: UserSession,
) -> None:
    """Обработка введенной оценки"""
    try:
        grade = int(message.text.strip())
        if not (0 <= grade <= 100):
            logger.info("grade: %s", grade)
            await session.answer(TextsRU.TEACHER_GRADING_INVALID_GRADE)
            return
    except (ValueError, AttributeError):
        await session.answer(TextsRU.TEACHER_GRADING_INVALID_GRADE)
        return

    # Сохраняем оценку во временное хранилище
    await state.update_data({_STATE_TEMP_GRADE: grade})
    # Очищаем только FSM состояние, НЕ данные
    await state.set_state(None)

    # Получаем данные из state
    data = await state.get_data()
    editing_message_id = data.get(_STATE_EDITING_MESSAGE_ID)
    answer_id = data.get(_STATE_CURRENT_ANSWER_ID)
    homework_id = data.get(_STATE_CURRENT_HOMEWORK_ID)
    page = data.get(_STATE_CURRENT_PAGE, 1)
    total_pages = data.get(_STATE_TOTAL_PAGES, 1)
    is_sent = data.get(_STATE_IS_SENT, False)
    temp_comment = data.get(_STATE_TEMP_COMMENT)

    if not answer_id or not homework_id:
        return

    answer = await AnswersService.get_by_id(int(answer_id))
    if not answer:
        return

    # Обновляем существующее сообщение (НЕ отправляем файлы заново)
    await session.edit_message(
        _build_answer_text(answer, temp_grade=grade, temp_comment=temp_comment),
        message_id=editing_message_id,
        reply_markup=InlineKeyboardTypeEnum.TEACHER_GRADING_CHECK,
        keyboard_data=_build_grading_keyboard(
            homework_id=int(homework_id),
            answer_id=int(answer_id),
            page=int(page),
            total_pages=int(total_pages),
            has_grade=True,
            has_comment=bool(temp_comment),
            is_sent=is_sent,
        ),
    )

    # Показываем уведомление
    await session.answer(TextsRU.TEACHER_GRADING_GRADE_SET.format(grade=grade))


# ==================== Установка комментария ====================


@teacher_grading_router.callback_query(
    CallbackFilter(TeacherGradingCallbackSchema, action="set_comment")
)
async def set_comment_start_handler(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherGradingCallbackSchema,
) -> None:
    """Начало установки комментария"""
    await session.answer_callback_query()

    await state.set_state(TeacherAnswerGradingStates.waiting_for_comment)
    await state.update_data(
        {
            _STATE_CURRENT_ANSWER_ID: callback_data.answer_id,
            _STATE_CURRENT_HOMEWORK_ID: callback_data.homework_id,
        }
    )

    await session.answer(
        TextsRU.TEACHER_GRADING_ENTER_COMMENT,
        reply_markup=ReplyKeyboardTypeEnum.TEACHER_GRADING_COMMENT,
    )


@teacher_grading_router.message(TeacherAnswerGradingStates.waiting_for_comment)
async def set_comment_process_handler(
    message: Message,
    state: FSMContext,
    session: UserSession,
) -> None:
    """Обработка введенного комментария"""
    comment = message.text.strip() if message.text else None

    if comment == TextsRU.TEACHER_GRADING_COMMENT_SKIP:
        comment = None

    # Сохраняем комментарий во временное хранилище
    await state.update_data({_STATE_TEMP_COMMENT: comment})
    # Очищаем только FSM состояние, НЕ данные
    await state.set_state(None)

    # Получаем данные из state
    data = await state.get_data()
    editing_message_id = data.get(_STATE_EDITING_MESSAGE_ID)
    answer_id = data.get(_STATE_CURRENT_ANSWER_ID)
    homework_id = data.get(_STATE_CURRENT_HOMEWORK_ID)
    page = data.get(_STATE_CURRENT_PAGE, 1)
    total_pages = data.get(_STATE_TOTAL_PAGES, 1)
    temp_grade = data.get(_STATE_TEMP_GRADE)
    is_sent = data.get(_STATE_IS_SENT, False)

    if not answer_id or not homework_id:
        return

    answer = await AnswersService.get_by_id(int(answer_id))
    if not answer:
        return

    # Обновляем существующее сообщение (НЕ отправляем файлы заново)
    await session.edit_message(
        _build_answer_text(answer, temp_grade=temp_grade, temp_comment=comment),
        message_id=editing_message_id,
        reply_markup=InlineKeyboardTypeEnum.TEACHER_GRADING_CHECK,
        keyboard_data=_build_grading_keyboard(
            homework_id=int(homework_id),
            answer_id=int(answer_id),
            page=int(page),
            total_pages=int(total_pages),
            has_grade=temp_grade is not None,
            has_comment=bool(comment),
            is_sent=is_sent,
        ),
    )

    # Показываем уведомление
    if comment:
        await session.answer(TextsRU.TEACHER_GRADING_COMMENT_SET)
    else:
        await session.answer(TextsRU.TEACHER_GRADING_COMMENT_SKIPPED)


# ==================== Отправка оценки ====================


@teacher_grading_router.callback_query(
    CallbackFilter(TeacherGradingCallbackSchema, action="send_grade")
)
async def send_grade_handler(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherGradingCallbackSchema,
    bot: Bot,
) -> None:
    """Отправка оценки студенту"""
    await session.answer_callback_query()
    logger.info(f"send_grade_handler: {callback_data}")

    data = await state.get_data()
    temp_grade = data.get(_STATE_TEMP_GRADE)
    temp_comment = data.get(_STATE_TEMP_COMMENT)
    is_sent = data.get(_STATE_IS_SENT, False)
    editing_message_id = data.get(_STATE_EDITING_MESSAGE_ID, session.message.message_id)
    logger.info(
        "temp_grade: %s, temp_comment: %s, is_sent: %s",
        temp_grade,
        temp_comment,
        is_sent,
    )

    # Проверяем, что оценка установлена
    if temp_grade is None:
        await session.answer_callback_query(
            TextsRU.TEACHER_GRADING_SEND_ERROR, show_alert=True
        )
        return

    # Если уже отправлено, игнорируем
    if is_sent:
        await session.answer_callback_query(
            TextsRU.TEACHER_GRADING_ALREADY_SENT, show_alert=True
        )
        return

    # Получаем ответ и задание
    answer = await AnswersService.get_by_id(callback_data.answer_id)
    if not answer:
        await session.answer(TextsRU.TRY_AGAIN)
        return

    homework = await HomeworksService.get_by_id(callback_data.homework_id)
    if not homework:
        await session.answer(TextsRU.TRY_AGAIN)
        return

    # Сохраняем оценку в БД
    await AnswersService.grade(
        answer_id=callback_data.answer_id,
        grade=temp_grade,
        teacher_comment=temp_comment,
        status=AnswersStatusEnum.REVIEWED,
        checked_at=datetime.now(),
    )

    # Отправляем уведомление студенту
    comment_text = temp_comment or TextsRU.TEACHER_GRADING_NO_COMMENT
    try:
        await bot.send_message(
            chat_id=answer.student.user_id,
            text=TextsRU.TEACHER_GRADING_STUDENT_NOTIFICATION.format(
                homework_title=homework.title,
                grade=temp_grade,
                comment=comment_text,
            ),
        )
    except Exception:
        pass  # Не критично, если не удалось отправить уведомление

    await session.answer_callback_query(
        TextsRU.TEACHER_GRADING_SEND_SUCCESS, show_alert=True
    )

    # Проверяем, есть ли еще непроверенные ответы
    next_page_data = await AnswersService.get_answers_page_by_homework_id(
        homework_id=callback_data.homework_id,
        status=AnswersStatusEnum.SENT,
        page=1,
        per_page=_PER_PAGE,
    )

    if next_page_data.items:
        # Есть следующий непроверенный ответ - показываем его
        next_answer = next_page_data.items[0]

        # Обновляем данные в state для следующего ответа
        await state.update_data(
            {
                _STATE_CURRENT_ANSWER_ID: next_answer.answer_id,
                _STATE_CURRENT_PAGE: next_page_data.page,
                _STATE_TOTAL_PAGES: next_page_data.total_pages,
                _STATE_MODE: "check",
                _STATE_IS_SENT: False,
                _STATE_TEMP_GRADE: None,
                _STATE_TEMP_COMMENT: None,
                _STATE_EDITING_MESSAGE_ID: editing_message_id,
            }
        )

        # Отправляем файлы следующего ответа
        await _send_answer_files(
            state=state, session=session, answer_id=next_answer.answer_id
        )

        # Обновляем сообщение следующим ответом
        await session.edit_message(
            _build_answer_text(next_answer, temp_grade=None, temp_comment=None),
            message_id=editing_message_id,
            reply_markup=InlineKeyboardTypeEnum.TEACHER_GRADING_CHECK,
            keyboard_data=_build_grading_keyboard(
                homework_id=callback_data.homework_id,
                answer_id=next_answer.answer_id,
                page=next_page_data.page,
                total_pages=next_page_data.total_pages,
                has_grade=False,
                has_comment=False,
                is_sent=False,
            ),
        )
    else:
        # Нет больше непроверенных ответов - показываем уведомление
        await _delete_previous_photos(state, session)
        await session.answer(
            TextsRU.TEACHER_GRADING_ALL_CHECKED,
            reply_markup=None,
        )
        await session.remove()
        # Очищаем состояние и данные, но сохраняем навигацию
        nav_manager = NavigationManager(state)
        await nav_manager.clear_cancel_target()
        await nav_manager.clear_state_and_data_keep_navigation()
        previous_step = await nav_manager.pop_previous(
            default_keyboard=ReplyKeyboardTypeEnum.TEACHER,
            default_text=TextsRU.SELECT_ACTION,
        )
        if previous_step:
            await session.answer(
                previous_step.text or TextsRU.SELECT_ACTION,
                reply_markup=previous_step.keyboard,
            )


# ==================== Редактирование оценки ====================


@teacher_grading_router.callback_query(
    CallbackFilter(TeacherGradingCallbackSchema, action="edit_grade")
)
async def edit_grade_start_handler(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherGradingCallbackSchema,
) -> None:
    """Начало редактирования оценки"""
    await session.answer_callback_query()

    # Используем отдельное состояние для редактирования
    await state.set_state(TeacherAnswerGradingStates.editing_grade)

    # Сохраняем ID текущего сообщения для последующего редактирования
    data = await state.get_data()
    await state.update_data(
        {
            _STATE_CURRENT_ANSWER_ID: callback_data.answer_id,
            _STATE_CURRENT_HOMEWORK_ID: callback_data.homework_id,
            _STATE_EDITING_MESSAGE_ID: session.message.message_id,
            _STATE_MODE: "edit",
            # Сохраняем текущую страницу и общее количество страниц
            _STATE_CURRENT_PAGE: data.get(_STATE_CURRENT_PAGE, 1),
            _STATE_TOTAL_PAGES: data.get(_STATE_TOTAL_PAGES, 1),
        }
    )

    await session.answer(TextsRU.TEACHER_GRADING_ENTER_GRADE)


@teacher_grading_router.message(TeacherAnswerGradingStates.editing_grade)
async def edit_grade_process_handler(
    message: Message,
    state: FSMContext,
    session: UserSession,
    bot: Bot,
) -> None:
    """Обработка новой оценки при редактировании"""
    try:
        grade = int(message.text.strip())
        if not (0 <= grade <= 100):
            await session.answer(TextsRU.TEACHER_GRADING_INVALID_GRADE)
            return
    except (ValueError, AttributeError):
        await session.answer(TextsRU.TEACHER_GRADING_INVALID_GRADE)
        return
    nav_manager = NavigationManager(state)

    data = await state.get_data()
    answer_id = data.get(_STATE_CURRENT_ANSWER_ID)
    homework_id = data.get(_STATE_CURRENT_HOMEWORK_ID)
    editing_message_id = data.get(_STATE_EDITING_MESSAGE_ID)
    current_page = data.get(_STATE_CURRENT_PAGE, 1)

    if not answer_id or not homework_id or not editing_message_id:
        await session.answer(TextsRU.TRY_AGAIN)
        await nav_manager.clear_cancel_target()
        await nav_manager.clear_state_and_data_keep_navigation()
        return

    # Получаем ответ и задание
    answer = await AnswersService.get_by_id(int(answer_id))
    if not answer:
        await session.answer(TextsRU.TRY_AGAIN)
        await nav_manager.clear_cancel_target()
        await nav_manager.clear_state_and_data_keep_navigation()
        return

    homework = await HomeworksService.get_by_id(int(homework_id))
    if not homework:
        await session.answer(TextsRU.TRY_AGAIN)
        await nav_manager.clear_cancel_target()
        await nav_manager.clear_state_and_data_keep_navigation()
        return

    # Сохраняем новую оценку (комментарий оставляем прежним)
    await AnswersService.grade(
        answer_id=int(answer_id),
        grade=grade,
        teacher_comment=answer.teacher_comment,
        status=AnswersStatusEnum.REVIEWED,
        checked_at=datetime.now(),
    )

    # Отправляем уведомление студенту об изменении
    comment_text = answer.teacher_comment or TextsRU.TEACHER_GRADING_NO_COMMENT
    try:
        await bot.send_message(
            chat_id=answer.student.user_id,
            text=TextsRU.TEACHER_GRADING_EDIT_NOTIFICATION.format(
                homework_title=homework.title,
                grade=grade,
                comment=comment_text,
            ),
        )
    except Exception:
        pass

    # Получаем обновленные данные страницы
    page_data = await AnswersService.get_answers_page_by_homework_id(
        homework_id=int(homework_id),
        status=AnswersStatusEnum.REVIEWED,
        page=int(current_page),
        per_page=_PER_PAGE,
    )

    if not page_data.items:
        await _delete_previous_photos(state, session)
        await nav_manager.clear_cancel_target()
        await nav_manager.clear_state_and_data_keep_navigation()
        previous_step = await nav_manager.pop_previous(
            default_keyboard=ReplyKeyboardTypeEnum.TEACHER_GRADING_CHECK,
            default_text=TextsRU.SELECT_ACTION,
        )
        if previous_step:
            await session.answer(
                previous_step.text or TextsRU.SELECT_ACTION,
                reply_markup=previous_step.keyboard,
            )
        return

    # Получаем обновленный ответ
    updated_answer = page_data.items[0]

    # Обновляем state с новыми данными
    await state.update_data(
        {
            _STATE_CURRENT_ANSWER_ID: updated_answer.answer_id,
            _STATE_CURRENT_PAGE: page_data.page,
            _STATE_TOTAL_PAGES: page_data.total_pages,
            _STATE_EDITING_MESSAGE_ID: editing_message_id,
            _STATE_MODE: "reviewed",
        }
    )

    # Очищаем состояние FSM
    await nav_manager.clear_cancel_target()
    await nav_manager.clear_state_and_data_keep_navigation()

    # Отправляем файлы ответа
    await _send_answer_files(
        state=state, session=session, answer_id=updated_answer.answer_id
    )

    # Редактируем существующее сообщение с обновленными данными
    await session.edit_message(
        _build_reviewed_answer_text(updated_answer),
        message_id=editing_message_id,
        reply_markup=InlineKeyboardTypeEnum.TEACHER_GRADING_REVIEWED,
        keyboard_data=_build_reviewed_keyboard(
            homework_id=int(homework_id),
            answer_id=updated_answer.answer_id,
            page=page_data.page,
            total_pages=page_data.total_pages,
        ),
    )

    # Показываем уведомление
    await session.answer(TextsRU.TEACHER_GRADING_GRADE_SET.format(grade=grade))


# ==================== Редактирование комментария ====================


@teacher_grading_router.callback_query(
    CallbackFilter(TeacherGradingCallbackSchema, action="edit_comment")
)
async def edit_comment_start_handler(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherGradingCallbackSchema,
) -> None:
    """Начало редактирования комментария"""
    await session.answer_callback_query()

    # Используем отдельное состояние для редактирования комментария
    await state.set_state(TeacherAnswerGradingStates.editing_comment)

    # Сохраняем ID текущего сообщения для последующего редактирования
    data = await state.get_data()
    await state.update_data(
        {
            _STATE_CURRENT_ANSWER_ID: callback_data.answer_id,
            _STATE_CURRENT_HOMEWORK_ID: callback_data.homework_id,
            _STATE_EDITING_MESSAGE_ID: session.message.message_id,
            _STATE_MODE: "edit",
            # Сохраняем текущую страницу и общее количество страниц
            _STATE_CURRENT_PAGE: data.get(_STATE_CURRENT_PAGE, 1),
            _STATE_TOTAL_PAGES: data.get(_STATE_TOTAL_PAGES, 1),
        }
    )

    await session.answer(
        TextsRU.TEACHER_GRADING_ENTER_COMMENT,
        reply_markup=ReplyKeyboardTypeEnum.TEACHER_GRADING_COMMENT,
    )


@teacher_grading_router.message(TeacherAnswerGradingStates.editing_comment)
async def edit_comment_process_handler(
    message: Message,
    state: FSMContext,
    session: UserSession,
    bot: Bot,
) -> None:
    """Обработка нового комментария при редактировании"""
    comment = message.text.strip() if message.text else None
    nav_manager = NavigationManager(state)

    if comment == TextsRU.TEACHER_GRADING_COMMENT_SKIP:
        comment = None

    data = await state.get_data()
    answer_id = data.get(_STATE_CURRENT_ANSWER_ID)
    homework_id = data.get(_STATE_CURRENT_HOMEWORK_ID)
    editing_message_id = data.get(_STATE_EDITING_MESSAGE_ID)
    current_page = data.get(_STATE_CURRENT_PAGE, 1)

    if not answer_id or not homework_id or not editing_message_id:
        await session.answer(TextsRU.TRY_AGAIN)
        await nav_manager.clear_cancel_target()
        await nav_manager.clear_state_and_data_keep_navigation()
        return

    # Получаем ответ и задание
    answer = await AnswersService.get_by_id(int(answer_id))
    if not answer:
        await session.answer(TextsRU.TRY_AGAIN)
        await nav_manager.clear_cancel_target()
        await nav_manager.clear_state_and_data_keep_navigation()
        return

    homework = await HomeworksService.get_by_id(int(homework_id))
    if not homework:
        await session.answer(TextsRU.TRY_AGAIN)
        await nav_manager.clear_cancel_target()
        await nav_manager.clear_state_and_data_keep_navigation()
        return

    # Сохраняем новый комментарий (оценку оставляем прежней)
    await AnswersService.grade(
        answer_id=int(answer_id),
        grade=answer.grade,
        teacher_comment=comment,
        status=AnswersStatusEnum.REVIEWED,
        checked_at=datetime.now(),
    )

    # Отправляем уведомление студенту об изменении
    comment_text = comment or TextsRU.TEACHER_GRADING_NO_COMMENT
    try:
        await bot.send_message(
            chat_id=answer.student.user_id,
            text=TextsRU.TEACHER_GRADING_COMMENT_EDIT_NOTIFICATION.format(
                homework_title=homework.title,
                grade=answer.grade,
                comment=comment_text,
            ),
        )
    except Exception:
        pass

    # Получаем обновленные данные страницы
    page_data = await AnswersService.get_answers_page_by_homework_id(
        homework_id=int(homework_id),
        status=AnswersStatusEnum.REVIEWED,
        page=int(current_page),
        per_page=_PER_PAGE,
    )

    if not page_data.items:
        await _delete_previous_photos(state, session)
        await nav_manager.clear_cancel_target()
        await nav_manager.clear_state_and_data_keep_navigation()
        await session.edit_message(
            TextsRU.TEACHER_GRADING_NO_REVIEWED_ANSWERS,
            message_id=editing_message_id,
            reply_markup=None,
        )
        return

    # Получаем обновленный ответ
    updated_answer = page_data.items[0]

    # Обновляем state с новыми данными
    await state.update_data(
        {
            _STATE_CURRENT_ANSWER_ID: updated_answer.answer_id,
            _STATE_CURRENT_PAGE: page_data.page,
            _STATE_TOTAL_PAGES: page_data.total_pages,
            _STATE_EDITING_MESSAGE_ID: editing_message_id,
            _STATE_MODE: "reviewed",
        }
    )

    # Очищаем состояние FSM
    await nav_manager.clear_cancel_target()
    await nav_manager.clear_state_and_data_keep_navigation()

    # Отправляем файлы ответа
    await _send_answer_files(
        state=state, session=session, answer_id=updated_answer.answer_id
    )

    # Редактируем существующее сообщение с обновленными данными
    await session.edit_message(
        _build_reviewed_answer_text(updated_answer),
        message_id=editing_message_id,
        reply_markup=InlineKeyboardTypeEnum.TEACHER_GRADING_REVIEWED,
        keyboard_data=_build_reviewed_keyboard(
            homework_id=int(homework_id),
            answer_id=updated_answer.answer_id,
            page=page_data.page,
            total_pages=page_data.total_pages,
        ),
    )

    # Показываем уведомление
    await session.answer(TextsRU.TEACHER_GRADING_COMMENT_UPDATED)


# ==================== Очистка оценки ====================


@teacher_grading_router.callback_query(
    CallbackFilter(TeacherGradingCallbackSchema, action="clear_grade")
)
async def clear_grade_handler(
    _: CallbackQuery,
    state: FSMContext,
    session: UserSession,
    callback_data: TeacherGradingCallbackSchema,
) -> None:
    """Очистка временных данных оценки и комментария"""
    await session.answer_callback_query()

    data = await state.get_data()
    editing_message_id = data.get(_STATE_EDITING_MESSAGE_ID, session.message.message_id)

    # Проверяем, что мы в режиме проверки
    if data.get(_STATE_MODE) != "check":
        return

    # Проверяем, что это правильный ответ
    if data.get(_STATE_CURRENT_ANSWER_ID) != callback_data.answer_id:
        return

    # Проверяем, что оценка не отправлена
    if data.get(_STATE_IS_SENT):
        await session.answer_callback_query(
            TextsRU.TEACHER_GRADING_ALREADY_SENT, show_alert=True
        )
        return

    # Очищаем временные данные
    await state.update_data({_STATE_TEMP_GRADE: None, _STATE_TEMP_COMMENT: None})

    # Получаем ответ для обновления
    answer = await AnswersService.get_by_id(callback_data.answer_id)
    if not answer:
        await session.edit_message(
            TextsRU.TEACHER_GRADING_ANSWER_NOT_FOUND,
            message_id=editing_message_id,
        )
        return

    # Обновляем сообщение
    await session.edit_message(
        _build_answer_text(answer, temp_grade=None, temp_comment=None),
        message_id=editing_message_id,
        reply_markup=InlineKeyboardTypeEnum.TEACHER_GRADING_CHECK,
        keyboard_data=_build_grading_keyboard(
            homework_id=data[_STATE_CURRENT_HOMEWORK_ID],
            answer_id=data[_STATE_CURRENT_ANSWER_ID],
            page=data[_STATE_CURRENT_PAGE],
            total_pages=data[_STATE_TOTAL_PAGES],
            has_grade=False,
            has_comment=False,
            is_sent=False,
        ),
    )

    # Показываем уведомление
    await session.answer_callback_query(
        TextsRU.TEACHER_GRADING_CLEARED, show_alert=True
    )
