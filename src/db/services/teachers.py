from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.schemas import TeacherCreateSchema, TeacherSchema
from src.db.models import TeachersModel
from src.db.repositories import TeachersRepository
from src.db.session import with_session


class TeachersService:
    """
    Сервис для работы с учителями
    """

    teachers_repository: TeachersRepository = TeachersRepository

    @with_session
    async def create(
        self, schema: TeacherCreateSchema, session: AsyncSession = None
    ) -> int:
        return await self.teachers_repository.create(schema, session=session)

    @with_session
    async def get_by_id(
        self, teacher_id: int, session: AsyncSession = None
    ) -> Optional[TeacherSchema]:
        return await self.teachers_repository.get_by_id(teacher_id, session=session)

    @with_session
    async def get_by_user_id(
        self, user_id: int, session: AsyncSession = None
    ) -> Optional[TeacherSchema]:
        teachers = await self.teachers_repository.get_all_where(
            where={TeachersModel.user_id: user_id},
            load_relationships=["user"],
            session=session,
        )
        return teachers[0] if teachers else None

    @with_session
    async def delete(
        self, teacher: TeacherSchema, session: AsyncSession = None
    ) -> None:
        return await self.teachers_repository.delete_by_id(
            teacher.teacher_id, session=session
        )
