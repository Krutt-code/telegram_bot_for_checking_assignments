from datetime import datetime
from typing import Optional

from sqlalchemy import TEXT, VARCHAR, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase as BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.enums import AnswersStatusEnum


class Base(BaseModel):
    """Базовый класс для всех моделей"""

    pass


class TelegramUsersModel(Base):
    __tablename__ = "telegram_users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(VARCHAR(63), default=None)
    full_name: Mapped[Optional[str]] = mapped_column(VARCHAR(127), default=None)
    real_full_name: Mapped[Optional[str]] = mapped_column(VARCHAR(127), default=None)


class AdminsModel(Base):
    __tablename__ = "admins"

    user_id: Mapped[int] = mapped_column(
        ForeignKey(TelegramUsersModel.user_id, ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        unique=True,
        index=True,
    )


class TeachersModel(Base):
    __tablename__ = "teachers"

    teacher_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(TelegramUsersModel.user_id, ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    # Relationships
    user: Mapped[TelegramUsersModel] = relationship(
        "TelegramUsersModel", foreign_keys=[user_id], lazy="select"
    )


class GroupsModel(Base):
    __tablename__ = "groups"

    group_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(VARCHAR(255), index=True)


class StudentsModel(Base):
    __tablename__ = "students"

    student_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(TelegramUsersModel.user_id, ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
        index=True,
    )
    group_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(GroupsModel.group_id, ondelete="SET NULL", onupdate="SET NULL"),
        index=True,
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    # Relationships
    user: Mapped[TelegramUsersModel] = relationship(
        "TelegramUsersModel", foreign_keys=[user_id], lazy="select"
    )
    group: Mapped[GroupsModel] = relationship(
        "GroupsModel", foreign_keys=[group_id], lazy="select"
    )


class HomeworksModel(Base):
    __tablename__ = "homeworks"

    homework_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey(TeachersModel.teacher_id, ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    title: Mapped[str] = mapped_column(TEXT)
    text: Mapped[str] = mapped_column(TEXT)
    start_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)
    end_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    # Relationships
    teacher: Mapped[TeachersModel] = relationship(
        "TeachersModel", foreign_keys=[teacher_id], lazy="select"
    )


class AnswersModel(Base):
    __tablename__ = "answers"

    answer_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    homework_id: Mapped[int] = mapped_column(
        ForeignKey(HomeworksModel.homework_id, ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey(StudentsModel.student_id, ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    student_answer: Mapped[Optional[str]] = mapped_column(TEXT, default=None)
    status: Mapped[AnswersStatusEnum] = mapped_column(
        TEXT, server_default=AnswersStatusEnum.SENT.value
    )
    grade: Mapped[Optional[int]] = mapped_column(default=None)
    teacher_comment: Mapped[Optional[str]] = mapped_column(TEXT, default=None)
    sent_at: Mapped[datetime] = mapped_column(DateTime)
    checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)

    # Relationships
    homework: Mapped[HomeworksModel] = relationship(
        "HomeworksModel", foreign_keys=[homework_id], lazy="select"
    )
    student: Mapped[StudentsModel] = relationship(
        "StudentsModel", foreign_keys=[student_id], lazy="select"
    )


class TelegramFilesModel(Base):
    __tablename__ = "telegram_files"

    telegram_file_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_id: Mapped[str] = mapped_column(TEXT)
    unique_file_id: Mapped[str] = mapped_column(TEXT)
    file_type: Mapped[str] = mapped_column(TEXT)
    owner_user_id: Mapped[int] = mapped_column(
        ForeignKey(TelegramUsersModel.user_id, ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    caption: Mapped[Optional[str]] = mapped_column(TEXT, default=None)
    mime_type: Mapped[Optional[str]] = mapped_column(TEXT, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    # Relationships
    owner_user: Mapped[TelegramUsersModel] = relationship(
        "TelegramUsersModel", foreign_keys=[owner_user_id], lazy="select"
    )


class AnswersFilesModel(Base):
    __tablename__ = "answer_files"

    answer_file_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    answer_id: Mapped[int] = mapped_column(
        ForeignKey(AnswersModel.answer_id, ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    telegram_file_id: Mapped[int] = mapped_column(
        ForeignKey(
            TelegramFilesModel.telegram_file_id, ondelete="CASCADE", onupdate="CASCADE"
        ),
        index=True,
    )

    # Relationships
    telegram_file: Mapped[TelegramFilesModel] = relationship(
        "TelegramFilesModel", foreign_keys=[telegram_file_id], lazy="select"
    )


class AssignedGroupsModel(Base):
    __tablename__ = "assigned_groups"

    assigned_group_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey(TeachersModel.teacher_id, ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey(GroupsModel.group_id, ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    # Relationships
    teacher: Mapped[TeachersModel] = relationship(
        "TeachersModel", foreign_keys=[teacher_id], lazy="select"
    )
    group: Mapped[GroupsModel] = relationship(
        "GroupsModel", foreign_keys=[group_id], lazy="select"
    )


class HomeworkGroupsModel(Base):
    __tablename__ = "homework_groups"

    homework_group_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    homework_id: Mapped[int] = mapped_column(
        ForeignKey(HomeworksModel.homework_id, ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey(GroupsModel.group_id, ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)


class HomeworkFilesModel(Base):
    __tablename__ = "homework_files"

    homeworks_file_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    homework_id: Mapped[int] = mapped_column(
        ForeignKey(HomeworksModel.homework_id, ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    telegram_file_id: Mapped[int] = mapped_column(
        ForeignKey(
            TelegramFilesModel.telegram_file_id, ondelete="CASCADE", onupdate="CASCADE"
        ),
        index=True,
    )

    # Relationships
    telegram_file: Mapped[TelegramFilesModel] = relationship(
        "TelegramFilesModel", foreign_keys=[telegram_file_id], lazy="select"
    )
