from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.schemas import GroupSchema, StudentCreateSchema, StudentSchema
from src.db.models import StudentsModel
from src.db.repositories import StudentsRepository
from src.db.session import with_session


class StudentsService:
    """
    Сервис для работы со студентами.
    """

    students_repository: StudentsRepository = StudentsRepository()

    @classmethod
    @with_session
    async def create(
        cls, schema: StudentCreateSchema, session: AsyncSession = None
    ) -> int:
        return await cls.students_repository.create(schema, session=session)

    @classmethod
    @with_session
    async def get_by_id(
        cls, student_id: int, session: AsyncSession = None
    ) -> Optional[StudentSchema]:
        return await cls.students_repository.get_by_id(
            student_id, session=session, load_relationships=["user", "group"]
        )

    @classmethod
    @with_session
    async def get_by_user_id(
        cls, user_id: int, session: AsyncSession = None
    ) -> Optional[StudentSchema]:
        students = await cls.students_repository.get_all_where(
            where={"user_id": user_id},
            load_relationships=["user", "group"],
            session=session,
        )
        return students[0] if students else None

    @classmethod
    @with_session
    async def update(cls, schema: StudentSchema, session: AsyncSession = None) -> None:
        data = schema.model_dump(exclude_unset=True, exclude={"user", "group"})
        return await cls.students_repository.update_values_by_id(
            schema.student_id, data, session=session
        )

    @classmethod
    @with_session
    async def delete(cls, student: StudentSchema, session: AsyncSession = None) -> None:
        return await cls.students_repository.delete(
            where={"student_id": student.student_id}, session=session
        )

    @classmethod
    @with_session
    async def set_group(
        cls,
        student: StudentSchema,
        group_id: Optional[int],
        session: AsyncSession = None,
    ) -> None:
        return await cls.students_repository.update_values_by_id(
            student.student_id, {"group_id": group_id}, session=session
        )

    @classmethod
    @with_session
    async def set_group_by_user_id(
        cls, user_id: int, group_id: Optional[int], session: AsyncSession = None
    ) -> int:
        return await cls.students_repository.update_values(
            where={"user_id": user_id},
            values={"group_id": group_id},
            session=session,
        )

    @classmethod
    @with_session
    async def get_group_by_user_id(
        cls, user_id: int, session: AsyncSession = None
    ) -> Optional[GroupSchema]:
        student = await cls.get_by_user_id(user_id, session=session)
        return student.group if student else None

    @classmethod
    @with_session
    async def get_all_by_group_id(
        cls, group_id: int, session: AsyncSession = None
    ) -> list[StudentSchema]:
        return await cls.students_repository.get_all_where(
            where={StudentsModel.group_id: group_id},
            load_relationships=["user", "group"],
            session=session,
        )
