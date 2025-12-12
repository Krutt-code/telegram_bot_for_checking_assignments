from sqlalchemy.ext.asyncio import AsyncSession

from src.core.schemas import AnswerFileCreateSchema
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
