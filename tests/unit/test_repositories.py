"""
Модульные тесты для репозиториев (работа с БД).
"""

import pytest

from src.core.schemas import StudentCreateSchema, TelegramUserCreateSchema
from src.db.repositories.students import StudentsRepository
from src.db.repositories.telegram_users import TelegramUsersRepository


class TestTelegramUsersRepository:
    """Тесты репозитория пользователей Telegram."""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session):
        """Тест создания пользователя."""
        repo = TelegramUsersRepository()

        schema = TelegramUserCreateSchema(
            user_id=12345, username="testuser", full_name="Test User"
        )
        user_id = await repo.create(schema, session=db_session)

        assert user_id == 12345

        # Проверяем, что пользователь был создан
        user = await repo.get_by_id(user_id, session=db_session)
        assert user.user_id == 12345
        assert user.username == "testuser"
        assert user.full_name == "Test User"

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, db_session):
        """Тест получения пользователя по ID."""
        repo = TelegramUsersRepository()

        # Создаем пользователя
        schema = TelegramUserCreateSchema(user_id=12345, username="testuser")
        created_id = await repo.create(schema, session=db_session)

        # Получаем пользователя
        fetched_user = await repo.get_by_id(created_id, session=db_session)

        assert fetched_user is not None
        assert fetched_user.user_id == 12345
        assert fetched_user.username == "testuser"

    @pytest.mark.asyncio
    async def test_update_user(self, db_session):
        """Тест обновления данных пользователя."""
        repo = TelegramUsersRepository()

        # Создаем пользователя
        schema = TelegramUserCreateSchema(user_id=12345, username="oldname")
        user_id = await repo.create(schema, session=db_session)

        # Обновляем
        success = await repo.update_values_by_id(
            user_id, {"username": "newname"}, session=db_session
        )

        assert success is True

        # Проверяем изменение
        updated_user = await repo.get_by_id(user_id, session=db_session)
        assert updated_user.username == "newname"


class TestStudentsRepository:
    """Тесты репозитория студентов."""

    @pytest.mark.asyncio
    async def test_create_student(self, db_session):
        """Тест создания студента."""
        # Сначала создаем пользователя Telegram
        users_repo = TelegramUsersRepository()
        user_schema = TelegramUserCreateSchema(user_id=12345)
        await users_repo.create(user_schema, session=db_session)

        # Создаем студента
        students_repo = StudentsRepository()
        student_schema = StudentCreateSchema(
            user_id=12345, group_id=None  # Студент без группы
        )
        student_id = await students_repo.create(student_schema, session=db_session)

        # Проверяем созданного студента
        student = await students_repo.get_by_id(
            student_id, load_relationships=["user"], session=db_session
        )
        assert student.user_id == 12345
        assert student.group_id is None

    @pytest.mark.asyncio
    async def test_get_student_by_user_id(self, db_session):
        """Тест получения студента по user_id."""
        # Создаем пользователя и студента
        users_repo = TelegramUsersRepository()
        user_schema = TelegramUserCreateSchema(user_id=12345)
        await users_repo.create(user_schema, session=db_session)

        students_repo = StudentsRepository()
        student_schema = StudentCreateSchema(user_id=12345)
        created_id = await students_repo.create(student_schema, session=db_session)

        # Получаем студента через where условие
        students = await students_repo.get_all_where(
            where={"user_id": 12345}, session=db_session
        )

        assert len(students) == 1
        assert students[0].student_id == created_id
        assert students[0].user_id == 12345
