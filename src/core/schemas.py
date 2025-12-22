from __future__ import annotations

from datetime import datetime
from typing import ClassVar, Optional, Self

from pydantic import BaseModel, ConfigDict, Field

from src.core.enums import (
    AnswersStatusEnum,
    CommandsEnum,
    InlineKeyboardTypeEnum,
    ReplyKeyboardTypeEnum,
)

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

    @property
    def display_name(self) -> str:
        """
        Имя для отображения в списках (приоритет: real_full_name -> full_name -> @username -> student_id).
        """
        if self.user is None:
            return f"student_id={self.student_id}"
        if self.user.real_full_name:
            return self.user.real_full_name
        if self.user.full_name:
            return self.user.full_name
        if self.user.username:
            return f"@{self.user.username}"
        return f"student_id={self.student_id}"

    @property
    def tg_href(self) -> Optional[str]:
        """
        Ссылка (href) на пользователя для HTML-разметки Telegram.
        """
        if self.user is None:
            return None
        if self.user.username:
            username = self.user.username.lstrip("@")
            return f"https://t.me/{username}"
        # Fallback: deep-link по user_id (может работать не во всех клиентах)
        return f"tg://openmessage?user_id={self.user_id}"


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


# --- Callback data схемы ---


class CallbackSchemaBase(BaseModel):
    """
    Базовая схема callback_data вида: <PREFIX>:<field1>:<field2>:...

    Поля сериализуются в порядке объявления в модели.
    """

    PREFIX: ClassVar[str]
    SEP: ClassVar[str] = ":"

    def pack(self) -> str:
        values = [self.PREFIX]
        for name in self.model_fields.keys():
            val = getattr(self, name)
            values.append(str(int(val)) if isinstance(val, (bool, int)) else str(val))
        return self.SEP.join(values)

    @classmethod
    def parse(cls, raw: str) -> Optional[Self]:
        if not raw:
            return None
        parts = raw.split(cls.SEP)
        if not parts or parts[0] != cls.PREFIX:
            return None

        field_names = list(cls.model_fields.keys())
        if len(parts) != 1 + len(field_names):
            return None

        data: dict = {}
        for i, name in enumerate(field_names, start=1):
            field = cls.model_fields[name]
            t = field.annotation
            v = parts[i]
            try:
                if t is int:
                    data[name] = int(v)
                elif t is bool:
                    data[name] = v == "1" or v.lower() == "true"
                else:
                    data[name] = v
            except Exception:
                return None
        try:
            return cls(**data)
        except Exception:
            return None


class PaginationCallbackSchema(CallbackSchemaBase):
    """
    Универсальная схема пагинации.
    Формат: pg:<key>:<page>
    """

    key: str
    page: int

    PREFIX: ClassVar[str] = "pg"


class TeacherGroupCallbackSchema(CallbackSchemaBase):
    """
    Callback для действий над группами преподавателя.

    Формат: tgrp:<action>:<group_id>
    """

    action: str
    group_id: int

    PREFIX: ClassVar[str] = "tgrp"


class TeacherGroupStudentCallbackSchema(CallbackSchemaBase):
    """
    Callback для действий над студентами в группе преподавателя.

    Формат: tgst:<action>:<group_id>:<student_id>:<page>
    """

    action: str
    group_id: int
    student_id: int
    page: int

    PREFIX: ClassVar[str] = "tgst"


class StudentGroupExitCallbackSchema(CallbackSchemaBase):
    """
    Callback для выхода студента из группы.

    Формат: sgx:<action>
    """

    action: str

    PREFIX: ClassVar[str] = "sgx"


class StudentHomeworkCallbackSchema(CallbackSchemaBase):
    """
    Callback для действий над заданием студента.

    Формат: shw:<action>:<homework_id>
    """

    action: str
    homework_id: int

    PREFIX: ClassVar[str] = "shw"


class TeacherHomeworkCallbackSchema(CallbackSchemaBase):
    """
    Callback для действий над заданием преподавателя.

    Формат: thw:<action>:<homework_id>
    """

    action: str
    homework_id: int

    PREFIX: ClassVar[str] = "thw"


class InlineButtonSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    text: str
    callback_data: str


class PaginationStateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    page: int = 1
    total_pages: int = 1
    hide_if_single_page: bool = True


class PaginatedListItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    text: str
    callback_data: str


class PaginatedListKeyboardSchema(BaseModel):
    """
    Универсальные данные для inline-списка с пагинацией.

    items: строки списка (каждая строка = одна кнопка)
    extra_buttons: кнопки ниже списка (каждая кнопка отдельной строкой)
    pagination: данные пагинации (опционально)
    """

    model_config = ConfigDict(from_attributes=True)

    items: list[PaginatedListItemSchema] = []
    extra_buttons: list[InlineButtonSchema] = []
    pagination: Optional[PaginationStateSchema] = None


class NoopCallbackSchema(CallbackSchemaBase):
    """
    Пустой callback для неинтерактивных inline-кнопок (например, элементы списка).

    Формат: noop:<x>
    """

    x: int = 0
    PREFIX: ClassVar[str] = "noop"


class TeacherGroupsPageViewSchema(BaseModel):
    """
    View model для страницы списка групп преподавателя.
    """

    model_config = ConfigDict(from_attributes=True)

    text: str
    keyboard_type: InlineKeyboardTypeEnum
    keyboard_data: dict


class TeacherGroupStudentsPageViewSchema(BaseModel):
    """
    View model для страницы списка студентов выбранной группы преподавателя.
    """

    model_config = ConfigDict(from_attributes=True)

    text: str
    keyboard_type: InlineKeyboardTypeEnum
    keyboard_data: dict
    group_id: int
    group_name: str


class TeacherCreateGroupResultSchema(BaseModel):
    """
    Результат команды создания группы (уровень менеджера).
    """

    model_config = ConfigDict(from_attributes=True)

    ok: bool
    group_id: Optional[int] = None
    normalized_name: Optional[str] = None
    error_code: Optional[str] = (
        None  # "invalid_name" | "duplicate_name" | "teacher_not_found"
    )


class TeacherGroupMutationResultSchema(BaseModel):
    """
    Результат операций rename/delete группы (уровень менеджера/use-case).
    """

    model_config = ConfigDict(from_attributes=True)

    ok: bool
    error_code: Optional[str] = (
        None  # "teacher_not_found" | "group_not_found" | "duplicate_name" | "confirm_name_mismatch"
    )


class TeacherGroupStudentMutationResultSchema(BaseModel):
    """
    Результат операций над студентом в группе преподавателя.
    """

    model_config = ConfigDict(from_attributes=True)

    ok: bool
    error_code: Optional[str] = (
        None  # "teacher_not_found" | "group_not_found" | "student_not_found" | "student_not_in_group"
    )


class TeacherGroupInviteInfoSchema(BaseModel):
    """
    Данные для приглашения в группу: кто преподаватель и какая группа.
    """

    model_config = ConfigDict(from_attributes=True)

    group_id: int
    group_name: str
    teacher_full_name: str


class TeacherGroupCreateUseCaseResultSchema(BaseModel):
    """
    Результат use-case создания+привязки группы (уровень БД).
    """

    model_config = ConfigDict(from_attributes=True)

    ok: bool
    group_id: Optional[int] = None
    error_code: Optional[str] = None  # "teacher_not_found" | "duplicate_name"


# endregion: Смешанные схемы данных
