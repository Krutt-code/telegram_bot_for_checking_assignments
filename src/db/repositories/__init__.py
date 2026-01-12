from .admins import AdminsRepository
from .answer_files import AnswersFilesRepository
from .answers import AnswersRepository
from .assigned_groups import AssignedGroupsRepository
from .groups import GroupsRepository
from .homework_files import HomeworkFilesRepository
from .homework_groups import HomeworkGroupsRepository
from .homeworks import HomeworksRepository
from .students import StudentsRepository
from .teachers import TeachersRepository
from .telegram_files import TelegramFilesRepository
from .telegram_users import TelegramUsersRepository
from .user_locks import UserLocksRepository

__all__ = [
    "AdminsRepository",
    "AnswersRepository",
    "AnswersFilesRepository",
    "AssignedGroupsRepository",
    "GroupsRepository",
    "HomeworksRepository",
    "HomeworkFilesRepository",
    "HomeworkGroupsRepository",
    "StudentsRepository",
    "TeachersRepository",
    "TelegramFilesRepository",
    "TelegramUsersRepository",
    "UserLocksRepository",
]
