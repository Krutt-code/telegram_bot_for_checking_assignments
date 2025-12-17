from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from src.bot.lexicon.callback_data import CALLBACK_DATA
from src.bot.lexicon.texts import TextsRU
from src.bot.managers.base import BaseUserManager, ensure_telegram_user_decorator
from src.core.enums import AnswersStatusEnum, InlineKeyboardTypeEnum, UserRoleEnum
from src.core.schemas import (
    PaginatedListItemSchema,
    PaginatedListKeyboardSchema,
    PaginationStateSchema,
    TeacherCreateGroupResultSchema,
    TeacherCreateSchema,
    TeacherGroupCallbackSchema,
    TeacherGroupMutationResultSchema,
    TeacherGroupsPageViewSchema,
    TeacherGroupStudentCallbackSchema,
    TeacherGroupStudentMutationResultSchema,
    TeacherGroupStudentsPageViewSchema,
)
from src.db.services import AssignedGroupsService, TeachersService
from src.db.use_cases.assignments import AssignmentsUseCase
from src.db.use_cases.teacher_groups import TeacherGroupsUseCase
from src.utils.telegram_messages import get_a_teg

if TYPE_CHECKING:
    from src.bot.session import UserSession


class TeacherManager(BaseUserManager):
    """
    Менеджер “преподавателя”.
    """

    GROUPS_PAGINATION_KEY: str = "teacher_groups"
    GROUPS_PER_PAGE: int = 10
    GROUP_STUDENTS_PAGINATION_PREFIX: str = "teacher_group_students:"
    GROUP_STUDENTS_PER_PAGE: int = 10

    def __init__(
        self,
        user_session: "UserSession",
    ) -> None:
        super().__init__(user_session=user_session)
        self.teachers = TeachersService()
        self.assignments = AssignmentsUseCase()
        self.teacher_groups = TeacherGroupsUseCase()

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
    async def build_groups_page_view(
        self,
        *,
        page: int = 1,
        per_page: Optional[int] = None,
    ) -> Optional[TeacherGroupsPageViewSchema]:
        """
        Собрать страницу списка групп, закреплённых за текущим преподавателем.

        Возвращает None, если запись преподавателя в БД не найдена.
        """
        teacher = await self.teachers.get_by_user_id(self.session.user_id)
        if not teacher:
            return None

        per_page = per_page or self.GROUPS_PER_PAGE
        page_data = await AssignedGroupsService.get_groups_page_by_teacher_id(
            teacher.teacher_id, page=page, per_page=per_page
        )

        keyboard_data = PaginatedListKeyboardSchema(
            items=[
                PaginatedListItemSchema(
                    text=g.name,
                    callback_data=TeacherGroupCallbackSchema(
                        action="view", group_id=g.group_id
                    ).pack(),
                )
                for g in page_data.items
            ],
            pagination=PaginationStateSchema(
                key=self.GROUPS_PAGINATION_KEY,
                page=page_data.page,
                total_pages=page_data.total_pages,
            ),
        ).model_dump()

        text = (
            TextsRU.TEACHER_GROUPS_EMPTY
            if not page_data.items
            else TextsRU.TEACHER_GROUPS_TITLE
        )

        return TeacherGroupsPageViewSchema(
            text=text,
            keyboard_type=InlineKeyboardTypeEnum.TEACHER_GROUPS_REVIEW,
            keyboard_data=keyboard_data,
        )

    @ensure_telegram_user_decorator
    async def create_group(self, *, name: str) -> TeacherCreateGroupResultSchema:
        """
        Создать новую группу и привязать к текущему преподавателю (атомарно).
        """
        normalized = " ".join((name or "").strip().split())
        if not (1 <= len(normalized) <= 255):
            return TeacherCreateGroupResultSchema(ok=False, error_code="invalid_name")

        res = await self.teacher_groups.create_group_and_assign_to_teacher(
            user_id=self.session.user_id,
            group_name=normalized,
        )
        if not res.ok:
            return TeacherCreateGroupResultSchema(ok=False, error_code=res.error_code)

        return TeacherCreateGroupResultSchema(
            ok=True,
            group_id=res.group_id,
            normalized_name=normalized,
        )

    @ensure_telegram_user_decorator
    async def build_group_students_page_view(
        self,
        *,
        group_id: int,
        page: int = 1,
        per_page: Optional[int] = None,
    ) -> Optional[TeacherGroupStudentsPageViewSchema]:
        """
        Собрать страницу списка студентов выбранной группы (с проверкой доступа преподавателя).
        """
        per_page = per_page or self.GROUP_STUDENTS_PER_PAGE
        group = await self.teacher_groups.get_teacher_group(
            user_id=self.session.user_id,
            group_id=group_id,
        )
        if not group:
            return None

        page_data = await self.teacher_groups.get_students_page_for_teacher_group(
            user_id=self.session.user_id,
            group_id=group_id,
            page=page,
            per_page=per_page,
        )
        page_items = []
        if page_data.items:
            for s in page_data.items:
                page_items.append(
                    PaginatedListItemSchema(
                        text=f"🗑 {s.display_name}",
                        callback_data=TeacherGroupStudentCallbackSchema(
                            action="rm",
                            group_id=group_id,
                            student_id=s.student_id,
                            page=page_data.page,
                        ).pack(),
                    )
                )
        else:
            page_items.append(
                PaginatedListItemSchema(
                    text=TextsRU.TEACHER_GROUP_STUDENTS_EMPTY,
                    callback_data=CALLBACK_DATA["NOOP"],
                )
            )

        keyboard_data = PaginatedListKeyboardSchema(
            items=page_items,
            pagination=PaginationStateSchema(
                key=f"{self.GROUP_STUDENTS_PAGINATION_PREFIX}{group_id}",
                page=page_data.page,
                total_pages=page_data.total_pages,
            ),
        ).model_dump()

        lines: list[str] = []
        for i, s in enumerate(page_data.items, start=1):
            if s.tg_href:
                item = get_a_teg(s.tg_href, s.display_name)
            else:
                item = s.display_name
            lines.append(f"{i}. {item}")

        text = TextsRU.TEACHER_GROUP_STUDENTS_TITLE.format(
            group_name=group.name, students_list="\n".join(lines)
        )

        return TeacherGroupStudentsPageViewSchema(
            text=text,
            keyboard_type=InlineKeyboardTypeEnum.TEACHER_GROUP_STUDENTS_REVIEW,
            keyboard_data=keyboard_data,
            group_id=group_id,
            group_name=group.name,
        )

    @ensure_telegram_user_decorator
    async def remove_student_from_group(
        self,
        *,
        group_id: int,
        student_id: int,
    ) -> TeacherGroupStudentMutationResultSchema:
        return await self.teacher_groups.remove_student_from_teacher_group(
            user_id=self.session.user_id,
            group_id=group_id,
            student_id=student_id,
        )

    @ensure_telegram_user_decorator
    async def rename_group(
        self,
        *,
        group_id: int,
        new_name: str,
    ) -> TeacherGroupMutationResultSchema:
        normalized = " ".join((new_name or "").strip().split())
        if not (1 <= len(normalized) <= 255):
            return TeacherGroupMutationResultSchema(ok=False, error_code="invalid_name")
        return await self.teacher_groups.rename_teacher_group(
            user_id=self.session.user_id,
            group_id=group_id,
            new_name=normalized,
        )

    @ensure_telegram_user_decorator
    async def delete_group(
        self,
        *,
        group_id: int,
        confirm_name: str,
    ) -> TeacherGroupMutationResultSchema:
        normalized = " ".join((confirm_name or "").strip().split())
        return await self.teacher_groups.delete_teacher_group_with_confirm_name(
            user_id=self.session.user_id,
            group_id=group_id,
            confirm_name=normalized,
        )

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
