"""
Модульные тесты для Pydantic-схем и валидации.
"""

from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from src.core.schemas import HomeworkCreateSchema


class TestHomeworkCreateSchema:
    """Тесты валидации схемы создания домашнего задания."""

    def test_valid_homework_schema(self):
        """Тест валидации корректных данных для создания задания."""
        now = datetime.now()
        data = {
            "teacher_id": 1,
            "title": "Тестовое задание",
            "text": "Описание задания",
            "end_at": now + timedelta(days=7),
            "created_at": now,
        }
        schema = HomeworkCreateSchema(**data)

        assert schema.title == data["title"]
        assert schema.text == data["text"]
        assert schema.teacher_id == 1
        assert schema.end_at == data["end_at"]

    def test_missing_required_fields(self):
        """Тест валидации отсутствия обязательных полей."""
        data = {
            "title": "Задание",
            # Отсутствуют обязательные поля: teacher_id, text, end_at, created_at
        }

        with pytest.raises(ValidationError) as exc_info:
            HomeworkCreateSchema(**data)

        errors = exc_info.value.errors()
        # Проверяем, что есть ошибки о недостающих полях
        assert len(errors) > 0

    def test_optional_start_at_field(self):
        """Тест, что поле start_at опциональное."""
        now = datetime.now()
        data = {
            "teacher_id": 1,
            "title": "Задание",
            "text": "Описание",
            "end_at": now + timedelta(days=7),
            "created_at": now,
            # start_at не указан
        }

        schema = HomeworkCreateSchema(**data)
        assert schema.start_at is None

    def test_with_start_at_field(self):
        """Тест создания схемы с указанным start_at."""
        now = datetime.now()
        data = {
            "teacher_id": 1,
            "title": "Задание",
            "text": "Описание",
            "start_at": now,
            "end_at": now + timedelta(days=7),
            "created_at": now,
        }

        schema = HomeworkCreateSchema(**data)
        assert schema.start_at == data["start_at"]
