from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.enums import AnswersStatusEnum
from src.core.schemas import AnswerCreateSchema, AnswerSchema
from src.db.models import AnswersModel, HomeworksModel, StudentsModel, TeachersModel
from src.db.pagination import Page, paginate_select
from src.db.repositories import AnswersRepository
from src.db.session import with_session


class AnswersService:
    """
    Сервис для работы с ответами.
    """

    answers_repository: AnswersRepository = AnswersRepository

    @classmethod
    @with_session
    async def create(
        cls, schema: AnswerCreateSchema, session: AsyncSession = None
    ) -> int:
        return await cls.answers_repository.create(schema, session=session)

    @classmethod
    @with_session
    async def get_by_id(
        cls, answer_id: int, session: AsyncSession = None
    ) -> Optional[AnswerSchema]:
        return await cls.answers_repository.get_by_id(
            answer_id, session=session, load_relationships=["homework", "student"]
        )

    @classmethod
    @with_session
    async def delete_by_id(cls, answer_id: int, session: AsyncSession = None) -> bool:
        return await cls.answers_repository.delete_by_id(answer_id, session=session)

    @classmethod
    @with_session
    async def set_student_text(
        cls,
        answer_id: int,
        student_answer: Optional[str] = None,
        session: AsyncSession = None,
    ) -> bool:
        return await cls.answers_repository.update_values_by_id(
            answer_id,
            values={"student_answer": student_answer},
            session=session,
        )

    @classmethod
    @with_session
    async def grade(
        cls,
        answer_id: int,
        grade: Optional[int] = None,
        teacher_comment: Optional[str] = None,
        status: AnswersStatusEnum = AnswersStatusEnum.REVIEWED,
        checked_at: Optional[datetime] = None,
        session: AsyncSession = None,
    ) -> bool:
        checked_at = checked_at or datetime.now()
        return await cls.answers_repository.update_values_by_id(
            answer_id,
            values={
                "grade": grade,
                "teacher_comment": teacher_comment,
                "status": status,
                "checked_at": checked_at,
            },
            session=session,
        )

    @classmethod
    @with_session
    async def count_by_homework_id(
        cls, homework_id: int, session: AsyncSession = None
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(AnswersModel)
            .where(AnswersModel.homework_id == homework_id)
        )
        return int((await session.scalar(stmt)) or 0)

    @classmethod
    @with_session
    async def get_answers_page_by_student_id(
        cls,
        student_id: int,
        *,
        page: int = 1,
        per_page: int = 1,
        session: AsyncSession = None,
    ) -> Page[AnswerSchema]:
        """
        Пагинация ответов студента (1 ответ на страницу по умолчанию).
        Подгружает homework и teacher.user для отображения.
        """
        stmt = (
            select(AnswersModel)
            .join(
                HomeworksModel, AnswersModel.homework_id == HomeworksModel.homework_id
            )
            .where(AnswersModel.student_id == student_id)
            .options(
                joinedload(AnswersModel.homework)
                .joinedload(HomeworksModel.teacher)
                .joinedload(TeachersModel.user),
                joinedload(AnswersModel.student).joinedload(StudentsModel.user),
                joinedload(AnswersModel.student).joinedload(StudentsModel.group),
            )
            .order_by(AnswersModel.sent_at.desc(), AnswersModel.answer_id.desc())
        )
        count_stmt = (
            select(func.count())
            .select_from(AnswersModel)
            .where(AnswersModel.student_id == student_id)
        )
        page_models: Page = await paginate_select(
            session,
            stmt,
            page=page,
            per_page=per_page,
            count_stmt=count_stmt,
        )
        return page_models.map(AnswerSchema.model_validate)
