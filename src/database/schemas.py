from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.database.enums import AnswersStatusEnum, MediaEnum


class MediaSchema(BaseModel):
    media_type: MediaEnum
    message_id: int
    file_id: Optional[str] = None
    unique_file_id: Optional[str] = None


class TelegramUserSchema(BaseModel):
    user_id: int
    username: Optional[str]
    full_name: Optional[str]


class TeacherSchema(BaseModel):
    teacher_id: int
    user_id: int
    full_name: str
    created: datetime


class GroupSchema(BaseModel):
    group_id: int
    name: str


class StudentSchema(BaseModel):
    student_id: int
    user_id: int
    group_id: int


class HomeworkSchema(BaseModel):
    homework_id: int
    teacher_id: int
    title: int
    text: int
    start: Optional[datetime] = None
    end: datetime
    media: List[Optional[MediaSchema]] = Field(default_factory=list)


class AnswerSchema(BaseModel):
    answer_id: int
    homework_id: int
    student_id: int
    text: str
    status: AnswersStatusEnum
    grade: Optional[int] = None
    teacher_comment: Optional[str] = None
    sent_at: datetime
    checked_at: Optional[datetime] = None
    media: List[Optional[MediaSchema]] = Field(default_factory=list)
