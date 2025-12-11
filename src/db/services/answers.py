from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import AnswersStatusEnum
from src.core.schemas import AnswerCreateSchema, AnswerSchema
from src.db.repositories import AnswersRepository
from src.db.session import with_session


class AnswersService:
    """
    Сервис для работы с ответами (answers).

    Важно: бизнес-операции, затрагивающие несколько таблиц (ответ + файлы + проверка прав),
    лучше размещать в use-case/оркестраторе (см. src/use_cases).
    """

    answers_repository: AnswersRepository = AnswersRepository

    @with_session
    async def create(
        self, schema: AnswerCreateSchema, session: AsyncSession = None
    ) -> int:
        return await self.answers_repository.create(schema, session=session)

    @with_session
    async def get_by_id(
        self, answer_id: int, session: AsyncSession = None
    ) -> Optional[AnswerSchema]:
        return await self.answers_repository.get_by_id(
            answer_id, session=session, load_relationships=["homework", "student"]
        )

    @with_session
    async def delete_by_id(self, answer_id: int, session: AsyncSession = None) -> bool:
        return await self.answers_repository.delete_by_id(answer_id, session=session)

    @with_session
    async def set_student_text(
        self,
        answer_id: int,
        student_answer: Optional[str] = None,
        session: AsyncSession = None,
    ) -> bool:
        return await self.answers_repository.update_values_by_id(
            answer_id,
            values={"student_answer": student_answer},
            session=session,
        )

    @with_session
    async def grade(
        self,
        answer_id: int,
        grade: Optional[int] = None,
        teacher_comment: Optional[str] = None,
        status: AnswersStatusEnum = AnswersStatusEnum.REVIEWED,
        checked_at: Optional[datetime] = None,
        session: AsyncSession = None,
    ) -> bool:
        checked_at = checked_at or datetime.now()
        return await self.answers_repository.update_values_by_id(
            answer_id,
            values={
                "grade": grade,
                "teacher_comment": teacher_comment,
                "status": status,
                "checked_at": checked_at,
            },
            session=session,
        )
