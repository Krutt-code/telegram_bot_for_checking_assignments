from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from src.bot.managers.base import BaseUserManager, ensure_telegram_user_decorator
from src.core.enums import AnswersStatusEnum, UserRoleEnum
from src.core.schemas import TeacherCreateSchema
from src.db.services import TeachersService
from src.db.use_cases.assignments import AssignmentsUseCase

if TYPE_CHECKING:
    from src.bot.session import UserSession


class TeacherManager(BaseUserManager):
    """
    Менеджер “преподавателя”.
    """

    def __init__(
        self,
        user_session: "UserSession",
    ) -> None:
        super().__init__(user_session=user_session)
        self.teachers = TeachersService()
        self.assignments = AssignmentsUseCase()

    @ensure_telegram_user_decorator
    async def initialize(self) -> None:
        """
        Инициализируем студента, создаем запись, сохраняем роль
        """
        teacher = await self.teachers.get_by_user_id(self.session.user_id)
        if not teacher:
            teacher = await self.teachers.create(
                TeacherCreateSchema(user_id=self.session.user_id)
            )
        await self.session.set_role(UserRoleEnum.TEACHER)

    @ensure_telegram_user_decorator
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
