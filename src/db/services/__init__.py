"""
Сервисы для работы с базой данных
"""

from .answer_files import AnswerFilesService
from .answers import AnswersService
from .homeworks import HomeworksService
from .students import StudentsService
from .teachers import TeachersService
from .telegram_files import TelegramFilesService
from .telegram_users import TelegramUsersService

__all__ = [
    "AnswerFilesService",
    "AnswersService",
    "HomeworksService",
    "StudentsService",
    "TeachersService",
    "TelegramFilesService",
    "TelegramUsersService",
]
