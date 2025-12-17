from __future__ import annotations

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.schemas import (
    AssignedGroupCreateSchema,
    GroupCreateSchema,
    GroupSchema,
    StudentSchema,
    TeacherGroupCreateUseCaseResultSchema,
    TeacherGroupInviteInfoSchema,
    TeacherGroupMutationResultSchema,
    TeacherGroupStudentMutationResultSchema,
)
from src.db.models import (
    AssignedGroupsModel,
    GroupsModel,
    StudentsModel,
    TeachersModel,
    TelegramUsersModel,
)
from src.db.pagination import Page, paginate_select
from src.db.repositories import AssignedGroupsRepository, GroupsRepository
from src.db.services import TeachersService
from src.db.session import with_session


class TeacherGroupsUseCase:
    """
    Use-case для операций над группами преподавателя, которые должны быть атомарными.
    """

    teachers: TeachersService = TeachersService()
    groups: GroupsRepository = GroupsRepository
    assigned_groups: AssignedGroupsRepository = AssignedGroupsRepository

    @classmethod
    @with_session
    async def create_group_and_assign_to_teacher(
        cls,
        *,
        user_id: int,
        group_name: str,
        session: AsyncSession = None,
    ) -> TeacherGroupCreateUseCaseResultSchema:
        """
        Атомарно:
        - находит teacher по user_id
        - проверяет, что у teacher нет группы с таким же названием
        - создаёт группу
        - создаёт связь teacher<->group (assigned_groups)
        """

        teacher = await cls.teachers.get_by_user_id(user_id, session=session)
        if not teacher:
            return TeacherGroupCreateUseCaseResultSchema(
                ok=False, error_code="teacher_not_found"
            )

        normalized = group_name.strip()

        exists_stmt = (
            select(GroupsModel.group_id)
            .join(
                AssignedGroupsModel,
                AssignedGroupsModel.group_id == GroupsModel.group_id,
            )
            .where(AssignedGroupsModel.teacher_id == teacher.teacher_id)
            .where(func.lower(GroupsModel.name) == func.lower(normalized))
            .limit(1)
        )
        exists = (await session.execute(exists_stmt)).scalars().first()
        if exists:
            return TeacherGroupCreateUseCaseResultSchema(
                ok=False, error_code="duplicate_name"
            )

        group_id = await cls.groups.create(
            GroupCreateSchema(name=normalized),
            session=session,
        )
        await cls.assigned_groups.create(
            AssignedGroupCreateSchema(teacher_id=teacher.teacher_id, group_id=group_id),
            session=session,
        )

        return TeacherGroupCreateUseCaseResultSchema(ok=True, group_id=group_id)

    @classmethod
    @with_session
    async def get_teacher_group(
        cls,
        *,
        user_id: int,
        group_id: int,
        session: AsyncSession = None,
    ) -> GroupSchema | None:
        """
        Вернуть группу, если она закреплена за преподавателем (по user_id).
        """
        teacher = await cls.teachers.get_by_user_id(user_id, session=session)
        if not teacher:
            return None

        stmt = (
            select(GroupsModel)
            .join(
                AssignedGroupsModel,
                AssignedGroupsModel.group_id == GroupsModel.group_id,
            )
            .where(AssignedGroupsModel.teacher_id == teacher.teacher_id)
            .where(GroupsModel.group_id == group_id)
            .limit(1)
        )
        model = (await session.execute(stmt)).scalars().first()
        return GroupSchema.model_validate(model) if model else None

    @classmethod
    @with_session
    async def get_students_page_for_teacher_group(
        cls,
        *,
        user_id: int,
        group_id: int,
        page: int = 1,
        per_page: int = 10,
        session: AsyncSession = None,
    ) -> Page[StudentSchema]:
        """
        Пагинация студентов группы, только если группа закреплена за преподавателем.
        """
        group = await cls.get_teacher_group(
            user_id=user_id, group_id=group_id, session=session
        )
        if not group:
            # Возвращаем пустую страницу, чтобы хендлер мог спокойно показать "нет доступа/не найдено"
            return Page(
                items=[],
                page=page,
                per_page=per_page,
                total_items=0,
                total_pages=1,
            )

        stmt = (
            select(StudentsModel)
            .where(StudentsModel.group_id == group_id)
            .order_by(StudentsModel.student_id.asc())
            .options(joinedload(StudentsModel.user), joinedload(StudentsModel.group))
        )
        count_stmt = (
            select(func.count())
            .select_from(StudentsModel)
            .where(StudentsModel.group_id == group_id)
        )
        page_models: Page = await paginate_select(
            session,
            stmt,
            page=page,
            per_page=per_page,
            count_stmt=count_stmt,
        )
        return page_models.map(StudentSchema.model_validate)

    @classmethod
    @with_session
    async def rename_teacher_group(
        cls,
        *,
        user_id: int,
        group_id: int,
        new_name: str,
        session: AsyncSession = None,
    ) -> TeacherGroupMutationResultSchema:
        teacher = await cls.teachers.get_by_user_id(user_id, session=session)
        if not teacher:
            return TeacherGroupMutationResultSchema(
                ok=False, error_code="teacher_not_found"
            )

        # Проверяем, что группа принадлежит преподавателю
        owned_stmt = (
            select(GroupsModel)
            .join(
                AssignedGroupsModel,
                AssignedGroupsModel.group_id == GroupsModel.group_id,
            )
            .where(AssignedGroupsModel.teacher_id == teacher.teacher_id)
            .where(GroupsModel.group_id == group_id)
            .limit(1)
        )
        group_model = (await session.execute(owned_stmt)).scalars().first()
        if not group_model:
            return TeacherGroupMutationResultSchema(
                ok=False, error_code="group_not_found"
            )

        # Проверка дубликата среди групп преподавателя (кроме текущей)
        dup_stmt = (
            select(GroupsModel.group_id)
            .join(
                AssignedGroupsModel,
                AssignedGroupsModel.group_id == GroupsModel.group_id,
            )
            .where(AssignedGroupsModel.teacher_id == teacher.teacher_id)
            .where(GroupsModel.group_id != group_id)
            .where(func.lower(GroupsModel.name) == func.lower(new_name))
            .limit(1)
        )
        dup = (await session.execute(dup_stmt)).scalars().first()
        if dup:
            return TeacherGroupMutationResultSchema(
                ok=False, error_code="duplicate_name"
            )

        await session.execute(
            update(GroupsModel)
            .where(GroupsModel.group_id == group_id)
            .values(name=new_name)
        )
        return TeacherGroupMutationResultSchema(ok=True)

    @classmethod
    @with_session
    async def delete_teacher_group_with_confirm_name(
        cls,
        *,
        user_id: int,
        group_id: int,
        confirm_name: str,
        session: AsyncSession = None,
    ) -> TeacherGroupMutationResultSchema:
        teacher = await cls.teachers.get_by_user_id(user_id, session=session)
        if not teacher:
            return TeacherGroupMutationResultSchema(
                ok=False, error_code="teacher_not_found"
            )

        owned_stmt = (
            select(GroupsModel)
            .join(
                AssignedGroupsModel,
                AssignedGroupsModel.group_id == GroupsModel.group_id,
            )
            .where(AssignedGroupsModel.teacher_id == teacher.teacher_id)
            .where(GroupsModel.group_id == group_id)
            .limit(1)
        )
        group_model = (await session.execute(owned_stmt)).scalars().first()
        if not group_model:
            return TeacherGroupMutationResultSchema(
                ok=False, error_code="group_not_found"
            )

        if (group_model.name or "").strip().lower() != (
            confirm_name or ""
        ).strip().lower():
            return TeacherGroupMutationResultSchema(
                ok=False, error_code="confirm_name_mismatch"
            )

        await session.execute(
            delete(GroupsModel).where(GroupsModel.group_id == group_id)
        )
        return TeacherGroupMutationResultSchema(ok=True)

    @classmethod
    @with_session
    async def remove_student_from_teacher_group(
        cls,
        *,
        user_id: int,
        group_id: int,
        student_id: int,
        session: AsyncSession = None,
    ) -> TeacherGroupStudentMutationResultSchema:
        """
        Удалить студента из группы (student.group_id -> NULL), если:
        - группа закреплена за преподавателем (по user_id)
        - студент действительно находится в этой группе
        """
        teacher = await cls.teachers.get_by_user_id(user_id, session=session)
        if not teacher:
            return TeacherGroupStudentMutationResultSchema(
                ok=False, error_code="teacher_not_found"
            )

        owned_group = (
            (
                await session.execute(
                    select(GroupsModel.group_id)
                    .join(
                        AssignedGroupsModel,
                        AssignedGroupsModel.group_id == GroupsModel.group_id,
                    )
                    .where(AssignedGroupsModel.teacher_id == teacher.teacher_id)
                    .where(GroupsModel.group_id == group_id)
                    .limit(1)
                )
            )
            .scalars()
            .first()
        )
        if not owned_group:
            return TeacherGroupStudentMutationResultSchema(
                ok=False, error_code="group_not_found"
            )

        exists_student = (
            (
                await session.execute(
                    select(StudentsModel.student_id)
                    .where(StudentsModel.student_id == student_id)
                    .limit(1)
                )
            )
            .scalars()
            .first()
        )
        if not exists_student:
            return TeacherGroupStudentMutationResultSchema(
                ok=False, error_code="student_not_found"
            )

        res = await session.execute(
            update(StudentsModel)
            .where(StudentsModel.student_id == student_id)
            .where(StudentsModel.group_id == group_id)
            .values(group_id=None)
        )
        if not res.rowcount:
            return TeacherGroupStudentMutationResultSchema(
                ok=False, error_code="student_not_in_group"
            )
        return TeacherGroupStudentMutationResultSchema(ok=True)

    @classmethod
    @with_session
    async def get_invite_info(
        cls,
        *,
        group_id: int,
        session: AsyncSession = None,
    ) -> TeacherGroupInviteInfoSchema | None:
        """
        Получить информацию для ссылки-приглашения: название группы и ФИО преподавателя.
        """
        stmt = (
            select(
                GroupsModel.group_id,
                GroupsModel.name,
                TelegramUsersModel.real_full_name,
                TelegramUsersModel.full_name,
            )
            .select_from(AssignedGroupsModel)
            .join(GroupsModel, GroupsModel.group_id == AssignedGroupsModel.group_id)
            .join(
                TeachersModel,
                TeachersModel.teacher_id == AssignedGroupsModel.teacher_id,
            )
            .join(
                TelegramUsersModel, TelegramUsersModel.user_id == TeachersModel.user_id
            )
            .where(GroupsModel.group_id == group_id)
            .limit(1)
        )
        row = (await session.execute(stmt)).first()
        if not row:
            return None
        gid, gname, real_full_name, full_name = row
        teacher_name = real_full_name or full_name or "преподаватель"
        return TeacherGroupInviteInfoSchema(
            group_id=int(gid),
            group_name=str(gname),
            teacher_full_name=str(teacher_name),
        )
