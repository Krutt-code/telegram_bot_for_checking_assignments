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

    @classmethod
    @with_session
    async def create(
        cls, schema: TeacherCreateSchema, session: AsyncSession = None
    ) -> int:
        return await cls.teachers_repository.create(schema, session=session)

    @classmethod
    @with_session
    async def get_by_id(
        cls, teacher_id: int, session: AsyncSession = None
    ) -> Optional[TeacherSchema]:
        return await cls.teachers_repository.get_by_id(teacher_id, session=session)

    @classmethod
    @with_session
    async def get_by_user_id(
        cls, user_id: int, session: AsyncSession = None
    ) -> Optional[TeacherSchema]:
        teachers = await cls.teachers_repository.get_all_where(
            where={TeachersModel.user_id: user_id},
            load_relationships=["user"],
            session=session,
        )
        return teachers[0] if teachers else None

    @classmethod
    @with_session
    async def delete(cls, teacher: TeacherSchema, session: AsyncSession = None) -> None:
        return await cls.teachers_repository.delete_by_id(
            teacher.teacher_id, session=session
        )
