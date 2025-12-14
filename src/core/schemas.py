from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.core.enums import AnswersStatusEnum, CommandsEnum, ReplyKeyboardTypeEnum

# region: Схемы таблиц базы данных


class TelegramFileCreateSchema(BaseModel):
    """Схема для создания файла Telegram"""

    model_config = ConfigDict(from_attributes=True)

    file_id: str
    unique_file_id: str
    file_type: str
    owner_user_id: int
    caption: Optional[str] = None
    mime_type: Optional[str] = None


class TelegramFileSchema(BaseModel):
    """Схема для чтения файла Telegram"""

    model_config = ConfigDict(from_attributes=True)

    telegram_file_id: int
    file_id: str
    unique_file_id: str
    file_type: str
    owner_user_id: int
    caption: Optional[str] = None
    mime_type: Optional[str] = None
    # Relationships
    owner_user: Optional["TelegramUserSchema"] = None


class AnswerFileCreateSchema(BaseModel):
    """Схема для создания файла ответа"""

    model_config = ConfigDict(from_attributes=True)

    answer_id: int
    telegram_file_id: int


class AnswerFileSchema(BaseModel):
    """Схема для чтения файла ответа"""

    model_config = ConfigDict(from_attributes=True)

    answer_file_id: int
    answer_id: int
    telegram_file_id: int
    # Relationships
    telegram_file: Optional["TelegramFileSchema"] = None


class HomeworkFileCreateSchema(BaseModel):
    """Схема для создания файла задания"""

    model_config = ConfigDict(from_attributes=True)

    homework_id: int
    telegram_file_id: int


class HomeworkFileSchema(BaseModel):
    """Схема для чтения файла задания"""

    model_config = ConfigDict(from_attributes=True)

    homeworks_file_id: int
    homework_id: int
    telegram_file_id: int
    # Relationships
    telegram_file: Optional["TelegramFileSchema"] = None


class AssignedGroupCreateSchema(BaseModel):
    """Схема для создания назначенной группы"""

    model_config = ConfigDict(from_attributes=True)

    teacher_id: int
    group_id: int


class AssignedGroupSchema(BaseModel):
    """Схема для чтения назначенной группы"""

    model_config = ConfigDict(from_attributes=True)

    assigned_group_id: int
    teacher_id: int
    group_id: int
    created_at: Optional[datetime] = None
    # Relationships
    teacher: Optional["TeacherSchema"] = None
    group: Optional["GroupSchema"] = None


class HomeworkGroupCreateSchema(BaseModel):
    """Схема для создания группы задания"""

    model_config = ConfigDict(from_attributes=True)

    homework_id: int
    group_id: int
    sent_at: Optional[datetime] = None


class HomeworkGroupSchema(BaseModel):
    """Схема для чтения группы задания"""

    model_config = ConfigDict(from_attributes=True)

    homework_group_id: int
    homework_id: int
    group_id: int
    created_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None


class TelegramUserCreateSchema(BaseModel):
    """Схема для создания пользователя Telegram"""

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None
    real_full_name: Optional[str] = None


class TelegramUserSchema(BaseModel):
    """Схема для чтения пользователя Telegram"""

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None
    real_full_name: Optional[str] = None


class TeacherCreateSchema(BaseModel):
    """Схема для создания преподавателя"""

    model_config = ConfigDict(from_attributes=True)

    user_id: int


class TeacherSchema(BaseModel):
    """Схема для чтения преподавателя"""

    model_config = ConfigDict(from_attributes=True)

    teacher_id: int
    user_id: int
    created_at: datetime
    # Relationships
    user: Optional["TelegramUserSchema"] = None


class GroupCreateSchema(BaseModel):
    """Схема для создания группы"""

    model_config = ConfigDict(from_attributes=True)

    name: str


class GroupSchema(BaseModel):
    """Схема для чтения группы"""

    model_config = ConfigDict(from_attributes=True)

    group_id: int
    name: str


class StudentCreateSchema(BaseModel):
    """Схема для создания студента"""

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    group_id: Optional[int] = None


class StudentSchema(BaseModel):
    """Схема для чтения студента"""

    model_config = ConfigDict(from_attributes=True)

    student_id: int
    user_id: int
    group_id: Optional[int] = None
    # Relationships
    user: Optional["TelegramUserSchema"] = None
    group: Optional["GroupSchema"] = None


class HomeworkCreateSchema(BaseModel):
    """Схема для создания задания"""

    model_config = ConfigDict(from_attributes=True)

    teacher_id: int
    title: str
    text: str
    start_at: Optional[datetime] = None
    end_at: datetime
    created_at: datetime


class HomeworkSchema(BaseModel):
    """Схема для чтения задания"""

    model_config = ConfigDict(from_attributes=True)

    homework_id: int
    teacher_id: int
    title: str
    text: str
    start_at: Optional[datetime] = None
    end_at: datetime
    # Relationships
    teacher: Optional["TeacherSchema"] = None


class AnswerCreateSchema(BaseModel):
    """Схема для создания ответа"""

    model_config = ConfigDict(from_attributes=True)

    homework_id: int
    student_id: int
    student_answer: Optional[str] = None
    status: AnswersStatusEnum = Field(default=AnswersStatusEnum.SENT)
    sent_at: datetime


class AnswerSchema(BaseModel):
    """Схема для чтения ответа"""

    model_config = ConfigDict(from_attributes=True)

    answer_id: int
    homework_id: int
    student_id: int
    student_answer: Optional[str] = None
    status: AnswersStatusEnum
    grade: Optional[int] = None
    teacher_comment: Optional[str] = None
    sent_at: datetime
    checked_at: Optional[datetime] = None
    # Relationships
    homework: Optional["HomeworkSchema"] = None
    student: Optional["StudentSchema"] = None


class AdminSchema(BaseModel):
    """Схема для чтения администратора"""

    model_config = ConfigDict(from_attributes=True)

    user_id: int


# endregion: Схемы таблиц базы данных
# region: Смешанные схемы данных


# --- Навигация бота ---


class NavigationStepSchema(BaseModel):
    """
    Шаг навигации в боте.
    """

    model_config = ConfigDict(from_attributes=True)

    command: CommandsEnum
    keyboard: Optional[ReplyKeyboardTypeEnum] = None
    text: Optional[str] = None


# endregion: Смешанные схемы данных
