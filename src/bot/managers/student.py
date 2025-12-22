from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Iterable, Optional

from src.bot.managers.base import BaseUserManager, ensure_telegram_user_decorator
from src.core.enums import UserRoleEnum
from src.core.schemas import (
    AnswerCreateSchema,
    AssignedGroupSchema,
    GroupSchema,
    StudentCreateSchema,
    TeacherSchema,
    TelegramFileCreateSchema,
)
from src.db.services import AssignedGroupsService, StudentsService
from src.db.use_cases.assignments import AssignmentsUseCase

if TYPE_CHECKING:
    from src.bot.session import UserSession


class StudentManager(BaseUserManager):
    """
    Менеджер “студента” — удобный API для роутеров.
    Проверку прав доступа вы делаете в фильтрах/роутерах, здесь только действия.
    """

    def __init__(
        self,
        user_session: "UserSession",
    ) -> None:
        super().__init__(user_session=user_session)
        self.students = StudentsService()
        self.assigned_groups = AssignedGroupsService()
        self.assignments = AssignmentsUseCase()

    @ensure_telegram_user_decorator
    async def initialize(self, group_id: Optional[int] = None) -> None:
        """
        Инициализируем студента, создаем запись, сохраняем роль
        """
        student = await self.students.get_by_user_id(self.session.user_id)
        if not student:
            student = await self.students.create(
                StudentCreateSchema(user_id=self.session.user_id, group_id=group_id)
            )
        elif group_id and student.group_id != group_id:
            await self.students.set_group(student, group_id=group_id)
        await self.session.set_role(UserRoleEnum.STUDENT)

    @ensure_telegram_user_decorator
    async def get_group(self) -> Optional[GroupSchema]:
        """
        Получить группу студента.
        """
        return await self.students.get_group_by_user_id(self.session.user_id)

    @ensure_telegram_user_decorator
    async def set_group(self, group_id: int) -> int:
        """
        Поменять группу студента по telegram user_id.
        Возвращает количество обновлённых строк (0/1).
        """
        return await self.students.set_group_by_user_id(self.session.user_id, group_id)

    @ensure_telegram_user_decorator
    async def leave_group(self) -> int:
        """
        Выйти из группы (сбросить group_id = NULL) по telegram user_id.
        Возвращает количество обновлённых строк.
        """
        return await self.students.set_group_by_user_id(self.session.user_id, None)

    @ensure_telegram_user_decorator
    async def get_teacher(self) -> Optional[TeacherSchema]:
        """
        Получить преподователя студента.
        """
        group = await self.students.get_group_by_user_id(self.session.user_id)
        if not group:
            return None
        assigned_group = await self.assigned_groups.get_by_group_id(group.group_id)
        if not assigned_group:
            return None
        return assigned_group.teacher

    @ensure_telegram_user_decorator
    async def get_assigned_group(self) -> Optional[AssignedGroupSchema]:
        """
        Получить назначенную группу студента и преподователя.
        """
        group = await self.students.get_group_by_user_id(self.session.user_id)
        if not group:
            return None
        return await self.assigned_groups.get_by_group_id(group.group_id)

    @ensure_telegram_user_decorator
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
