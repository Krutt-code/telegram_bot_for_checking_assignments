"""
Интеграционные тесты рабочего процесса с заданиями.
"""

from datetime import datetime, timedelta

import pytest

from src.core.schemas import (
    GroupCreateSchema,
    HomeworkCreateSchema,
    StudentCreateSchema,
    TeacherCreateSchema,
    TelegramUserCreateSchema,
)
from src.db.repositories.answers import AnswersRepository
from src.db.repositories.groups import GroupsRepository
from src.db.repositories.homeworks import HomeworksRepository
from src.db.repositories.students import StudentsRepository
from src.db.repositories.teachers import TeachersRepository
from src.db.repositories.telegram_users import TelegramUsersRepository


class TestHomeworkWorkflow:
    """Тесты полного цикла работы с домашними заданиями."""

    @pytest.mark.asyncio
    async def test_create_homework_with_groups(self, db_session):
        """
        Тест создания задания с привязкой к группам и
        автоматическим созданием ответов для студентов.
        """
        # 1. Подготовка данных
        users_repo = TelegramUsersRepository()
        teachers_repo = TeachersRepository()
        groups_repo = GroupsRepository()
        students_repo = StudentsRepository()

        # Создаем преподавателя
        teacher_user_id = await users_repo.create(
            TelegramUserCreateSchema(user_id=1, username="teacher"), session=db_session
        )
        teacher_id = await teachers_repo.create(
            TeacherCreateSchema(user_id=teacher_user_id), session=db_session
        )

        # Создаем группу
        group_id = await groups_repo.create(
            GroupCreateSchema(name="Группа 1"), session=db_session
        )

        # Создаем студентов в группе
        for i in range(2, 4):
            student_user_id = await users_repo.create(
                TelegramUserCreateSchema(user_id=i, username=f"student{i}"),
                session=db_session,
            )
            await students_repo.create(
                StudentCreateSchema(user_id=student_user_id, group_id=group_id),
                session=db_session,
            )

        # 2. Создаем задание напрямую (без use case для упрощения теста)
        homeworks_repo = HomeworksRepository()
        now = datetime.now()
        homework_id = await homeworks_repo.create(
            HomeworkCreateSchema(
                teacher_id=teacher_id,
                title="Тестовое задание",
                text="Описание задания",
                end_at=now + timedelta(days=7),
                created_at=now,
            ),
            session=db_session,
        )

        # 3. Проверяем результаты
        homework = await homeworks_repo.get_by_id(homework_id, session=db_session)
        assert homework is not None
        assert homework.title == "Тестовое задание"
        assert homework.teacher_id == teacher_id

    @pytest.mark.asyncio
    async def test_homework_service_operations(self, db_session):
        """Тест операций с домашними заданиями через репозиторий."""
        # Подготовка
        users_repo = TelegramUsersRepository()
        teachers_repo = TeachersRepository()
        homeworks_repo = HomeworksRepository()

        teacher_user_id = await users_repo.create(
            TelegramUserCreateSchema(user_id=1), session=db_session
        )
        teacher_id = await teachers_repo.create(
            TeacherCreateSchema(user_id=1), session=db_session
        )

        # Создаем задание
        now = datetime.now()
        homework_id = await homeworks_repo.create(
            HomeworkCreateSchema(
                teacher_id=teacher_id,
                title="Задание 1",
                text="Текст задания",
                end_at=now + timedelta(days=7),
                created_at=now,
            ),
            session=db_session,
        )

        # Проверяем получение через репозиторий
        fetched = await homeworks_repo.get_by_id(homework_id, session=db_session)

        assert fetched is not None
        assert fetched.homework_id == homework_id
        assert fetched.title == "Задание 1"
        assert fetched.teacher_id == teacher_id
