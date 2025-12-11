from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional

from aiogram.types import CallbackQuery, Message

from src.bot.managers.base import BaseUserManager
from src.core.schemas import AnswerCreateSchema, TelegramFileCreateSchema
from src.db.services import StudentsService
from src.db.use_cases.assignments import AssignmentsUseCase


class StudentManager(BaseUserManager):
    """
    Менеджер “студента” — удобный API для роутеров.
    Проверку прав доступа вы делаете в фильтрах/роутерах, здесь только действия.
    """

    def __init__(
        self,
        message: Optional[Message] = None,
        callback_query: Optional[CallbackQuery] = None,
    ) -> None:
        super().__init__(message=message, callback_query=callback_query)
        self.students = StudentsService()
        self.assignments = AssignmentsUseCase()

    async def set_group(self, group_id: int) -> int:
        """
        Поменять группу студента по telegram user_id.
        Возвращает количество обновлённых строк (0/1).
        """
        await self.ensure_telegram_user()
        return await self.students.set_group_by_user_id(self.session.user_id, group_id)

    async def submit_answer(
        self,
        *,
        homework_id: int,
        text: Optional[str] = None,
        sent_at: Optional[datetime] = None,
        telegram_files: Optional[Iterable[TelegramFileCreateSchema]] = None,
    ) -> int:
        """
        Создать ответ от текущего пользователя. Требует, чтобы студент уже существовал в БД.
        """
        await self.ensure_telegram_user()
        student = await self.students.get_by_user_id(self.session.user_id)
        if not student:
            raise ValueError(
                "Student record not found for this user_id. Register student first."
            )

        sent_at = sent_at or datetime.now()
        answer_id = await self.assignments.submit_answer(
            AnswerCreateSchema(
                homework_id=homework_id,
                student_id=student.student_id,
                student_answer=text,
                sent_at=sent_at,
            ),
            telegram_files=telegram_files,
        )
        return answer_id
