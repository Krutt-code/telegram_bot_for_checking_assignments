from __future__ import annotations

from datetime import datetime
from typing import Optional

from aiogram.types import CallbackQuery, Message

from src.bot.managers.base import BaseUserManager
from src.core.enums import AnswersStatusEnum
from src.db.services import TeachersService
from src.db.use_cases.assignments import AssignmentsUseCase


class TeacherManager(BaseUserManager):
    """
    Менеджер “преподавателя”.
    """

    def __init__(
        self,
        message: Optional[Message] = None,
        callback_query: Optional[CallbackQuery] = None,
    ) -> None:
        super().__init__(message=message, callback_query=callback_query)
        self.teachers = TeachersService()
        self.assignments = AssignmentsUseCase()

    async def grade_answer(
        self,
        *,
        answer_id: int,
        grade: Optional[int],
        teacher_comment: Optional[str] = None,
        status: AnswersStatusEnum = AnswersStatusEnum.REVIEWED,
        checked_at: Optional[datetime] = None,
    ) -> bool:
        """
        Оценить ответ. Требует, чтобы преподаватель уже существовал в БД.
        """
        await self.ensure_telegram_user()
        teacher = await self.teachers.get_by_user_id(self.session.user_id)
        if not teacher:
            raise ValueError(
                "Teacher record not found for this user_id. Register teacher first."
            )

        return await self.assignments.grade_answer(
            teacher_id=teacher.teacher_id,
            answer_id=answer_id,
            grade=grade,
            teacher_comment=teacher_comment,
            status=status,
            checked_at=checked_at,
        )
