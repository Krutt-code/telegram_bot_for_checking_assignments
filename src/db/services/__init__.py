"""
Сервисы для работы с базой данных
"""

from .answer_files import AnswerFilesService
from .answers import AnswersService
from .assigned_groups import AssignedGroupsService
from .homework_files import HomeworkFilesService
from .homeworks import HomeworksService
from .students import StudentsService
from .teachers import TeachersService
from .telegram_files import TelegramFilesService
from .telegram_users import TelegramUsersService

__all__ = [
    "AnswerFilesService",
    "AnswersService",
    "HomeworksService",
    "HomeworkFilesService",
    "AssignedGroupsService",
    "StudentsService",
    "TeachersService",
    "TelegramFilesService",
    "TelegramUsersService",
]
