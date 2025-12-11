from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.schemas import AnswerCreateSchema, StudentCreateSchema, StudentSchema
from src.db.models import StudentsModel
from src.db.repositories import StudentsRepository
from src.db.session import with_session


class StudentsService:
    """
    Сервис для работы со студентами
    """

    students_repository: StudentsRepository = StudentsRepository

    @with_session
    async def create(
        self, schema: StudentCreateSchema, session: AsyncSession = None
    ) -> int:
        return await self.students_repository.create(schema, session=session)

    @with_session
    async def get_by_id(
        self, student_id: int, session: AsyncSession = None
    ) -> Optional[StudentSchema]:
        return await self.students_repository.get_by_id(
            student_id, session=session, load_relationships=["user", "group"]
        )

    @with_session
    async def get_by_user_id(
        self, user_id: int, session: AsyncSession = None
    ) -> Optional[StudentSchema]:
        students = await self.students_repository.get_all_where(
            where={"user_id": user_id},
            load_relationships=["user", "group"],
            session=session,
        )
        return students[0] if students else None

    @with_session
    async def update(self, schema: StudentSchema, session: AsyncSession = None) -> None:
        return await self.students_repository.update_by_id(
            schema.student_id, schema, session=session
        )

    @with_session
    async def delete(
        self, student: StudentSchema, session: AsyncSession = None
    ) -> None:
        return await self.students_repository.delete(
            where={"student_id": student.student_id}, session=session
        )

    @with_session
    async def set_group(
        self, student: StudentSchema, group_id: int, session: AsyncSession = None
    ) -> None:
        student.group_id = group_id
        return await self.students_repository.update_by_id(
            student.student_id, student, session=session
        )

    @with_session
    async def set_group_by_user_id(
        self, user_id: int, group_id: int, session: AsyncSession = None
    ) -> int:
        return await self.students_repository.update_values(
            where={"user_id": user_id},
            values={"group_id": group_id},
            session=session,
        )

    @with_session
    async def get_all_by_group_id(
        self, group_id: int, session: AsyncSession = None
    ) -> list[StudentSchema]:
        return await self.students_repository.get_all_where(
            where={StudentsModel.group_id: group_id},
            load_relationships=["user", "group"],
            session=session,
        )
