from datetime import datetime
from typing import Optional

from sqlalchemy import TEXT, VARCHAR, ForeignKey
from sqlalchemy.orm import DeclarativeBase as BaseModel
from sqlalchemy.orm import Mapped, mapped_column

from src.database.enums import (
    AnswerMediaTypeEnum,
    AnswersStatusEnum,
    HomeworkMediaTypeEnum,
)


class TelegramUsersModel(BaseModel):
    __tablename__ = "telegram_users"

    user_id: Mapped[int] = mapped_column(int, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(VARCHAR(255), default=None)
    full_name: Mapped[Optional[str]] = mapped_column(VARCHAR(255), default=None)


class AdminsModel(BaseModel):
    __tablename__ = "admins"

    user_id: Mapped[int] = mapped_column(
        ForeignKey(TelegramUsersModel.user_id), unique=True, index=True
    )


class TeachersModel(BaseModel):
    __tablename__ = "teachers"

    teacher_id: Mapped[int] = mapped_column(int, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(TelegramUsersModel.user_id), unique=True, index=True
    )
    full_name: Mapped[Optional[str]] = mapped_column(VARCHAR(511), default=None)
    created: Mapped[datetime] = mapped_column(datetime, default_factory=datetime.now)


class GroupsModel(BaseModel):
    __tablename__ = "groups"

    group_id: Mapped[int] = mapped_column(int, primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(255))


class StudentsModel(BaseModel):
    __tablename__ = "students"

    student_id: Mapped[int] = mapped_column(int, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(TelegramUsersModel.user_id), unique=True, index=True
    )
    group_id: Mapped[int] = mapped_column(ForeignKey(GroupsModel.group_id), index=True)
    updated: Mapped[datetime]
    created: Mapped[datetime]


class HomeworksModel(BaseModel):
    __tablename__ = "homeworks"

    homework_id: Mapped[int] = mapped_column(int, primary_key=True)
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey(TeachersModel.teacher_id), index=True
    )
    title: Mapped[str] = mapped_column(TEXT)
    text: Mapped[str] = mapped_column(TEXT)
    start: Mapped[Optional[datetime]] = mapped_column(datetime, default=None)
    end: Mapped[datetime]
    updated: Mapped[datetime]
    created: Mapped[datetime]


class AnswersModel(BaseModel):
    __tablename__ = "answers"

    answer_id: Mapped[int] = mapped_column(int, primary_key=True)
    homework_id: Mapped[int] = mapped_column(
        ForeignKey(HomeworksModel.homework_id), index=True
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey(StudentsModel.student_id), index=True
    )
    text: Mapped[Optional[str]] = mapped_column(TEXT, default=None)
    status: Mapped[AnswersStatusEnum] = mapped_column(AnswersStatusEnum)
    grade: Mapped[Optional[int]] = mapped_column(int, default=None)
    teacher_comment: Mapped[Optional[str]] = mapped_column(TEXT, default=None)
    sent_at: Mapped[datetime] = mapped_column(datetime, default_factory=datetime.now)
    checked_at: Mapped[Optional[datetime]] = mapped_column(datetime, default=None)


class AnswersMediaModel(BaseModel):
    __tablename__ = "answers_media"

    answer_media_id: Mapped[int] = mapped_column(int, primary_key=True)
    answer_id: Mapped[int] = mapped_column(
        ForeignKey(AnswersModel.answer_id), index=True
    )
    media_type: Mapped[AnswerMediaTypeEnum] = mapped_column(AnswerMediaTypeEnum)
    message_id: Mapped[int] = mapped_column(int)
    file_id: Mapped[Optional[str]] = mapped_column(TEXT, default=None)
    unique_file_id: Mapped[Optional[str]] = mapped_column(TEXT, default=None)


class AssignedGroupsModel(BaseModel):
    __tablename__ = "assigned_groups"

    assigned_group_id: Mapped[int] = mapped_column(int, primary_key=True)
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey(TeachersModel.teacher_id), index=True
    )
    group_id: Mapped[int] = mapped_column(ForeignKey(GroupsModel.group_id), index=True)
    created: Mapped[datetime] = mapped_column(datetime, default_factory=datetime.now)


class HomeworkGroupsModel(BaseModel):
    __tablename__ = "homework_groups"

    homework_group_id: Mapped[int] = mapped_column(int, primary_key=True)
    homework_id: Mapped[int] = mapped_column(
        ForeignKey(HomeworksModel.homework_id), index=True
    )
    group_id: Mapped[int] = mapped_column(ForeignKey(GroupsModel.group_id), index=True)
    created: Mapped[datetime] = mapped_column(datetime, default_factory=datetime.now)
    sent_at: Mapped[Optional[datetime]] = mapped_column(datetime, default=None)


class HomeworkMediaModel(BaseModel):
    __tablename__ = "homework_media"

    homeworks_media_id: Mapped[int] = mapped_column(int, primary_key=True)
    homework_id: Mapped[int] = mapped_column(
        ForeignKey(HomeworksModel.homework_id), index=True
    )
    message_id: Mapped[int]
    file_id: Mapped[Optional[str]] = mapped_column(TEXT, default=None)
    unique_file_id: Mapped[Optional[str]] = mapped_column(TEXT, default=None)
    media_type: Mapped[HomeworkMediaTypeEnum]
