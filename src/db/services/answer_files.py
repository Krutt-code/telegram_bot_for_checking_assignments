from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.schemas import AnswerFileCreateSchema, AnswerFileSchema
from src.db.repositories import AnswersFilesRepository
from src.db.session import with_session


class AnswerFilesService:
    """
    Сервис для связей answer_files (файлы, прикреплённые к ответу).
    """

    answers_files_repository: AnswersFilesRepository = AnswersFilesRepository

    @classmethod
    @with_session
    async def attach_file(
        cls, schema: AnswerFileCreateSchema, session: AsyncSession = None
    ) -> int:
        return await cls.answers_files_repository.create(schema, session=session)

    @classmethod
    @with_session
    async def get_files_by_answer_id(
        cls, answer_id: int, session: AsyncSession = None
    ) -> List[AnswerFileSchema]:
        """Получить все файлы, прикрепленные к ответу"""
        files = await cls.answers_files_repository.get_all_where(
            where={"answer_id": answer_id},
            load_relationships=["telegram_file"],
            session=session,
        )
        return [AnswerFileSchema.model_validate(f) for f in files]
