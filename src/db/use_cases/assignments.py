from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import AnswersStatusEnum
from src.core.schemas import (
    AnswerCreateSchema,
    AnswerFileCreateSchema,
    TelegramFileCreateSchema,
)
from src.db.services import (
    AnswerFilesService,
    AnswersService,
    HomeworksService,
    TelegramFilesService,
)
from src.db.session import with_session


class AssignmentsUseCase:
    """
    Оркестратор для операций в “домашках”:
    - отправка ответа (answer + файлы)
    - проверка/оценивание (проверки + апдейт ответа)
    """

    answers: AnswersService = AnswersService()
    homeworks: HomeworksService = HomeworksService()
    telegram_files: TelegramFilesService = TelegramFilesService()
    answer_files: AnswerFilesService = AnswerFilesService()

    @with_session
    async def submit_answer(
        self,
        answer: AnswerCreateSchema,
        telegram_files: Optional[Iterable[TelegramFileCreateSchema]] = None,
        session: AsyncSession = None,
    ) -> int:
        """
        Атомарно создаёт ответ и (опционально) прикрепляет файлы.
        """
        answer_id = await self.answers.create(answer, session=session)

        if telegram_files:
            for tf in telegram_files:
                telegram_file_id = await self.telegram_files.create(tf, session=session)
                await self.answer_files.attach_file(
                    AnswerFileCreateSchema(
                        answer_id=answer_id, telegram_file_id=telegram_file_id
                    ),
                    session=session,
                )

        return answer_id

    @with_session
    async def grade_answer(
        self,
        *,
        teacher_id: int,
        answer_id: int,
        grade: Optional[int],
        teacher_comment: Optional[str] = None,
        status: AnswersStatusEnum = AnswersStatusEnum.REVIEWED,
        checked_at: Optional[datetime] = None,
        session: AsyncSession = None,
    ) -> bool:
        """
        Оценивание ответа с проверкой, что ответ принадлежит заданию этого преподавателя.
        Права доступа вы можете проверять в роутерах, но эту проверку полезно держать
        как “страховку” на уровне use-case.
        """
        answer = await self.answers.get_by_id(answer_id, session=session)
        if not answer:
            return False

        homework = await self.homeworks.get_by_id(answer.homework_id, session=session)
        if not homework or homework.teacher_id != teacher_id:
            raise PermissionError("Teacher has no access to this answer/homework")

        return await self.answers.grade(
            answer_id=answer_id,
            grade=grade,
            teacher_comment=teacher_comment,
            status=status,
            checked_at=checked_at,
            session=session,
        )
