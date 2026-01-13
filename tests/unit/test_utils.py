"""
Модульные тесты для вспомогательных функций.
"""

import pytest

from src.utils.telegram_messages import split_telegram_html_message


class TestMessageSplitting:
    """Тесты разбиения длинных сообщений."""

    def test_short_message_no_split(self):
        """Короткое сообщение не должно разбиваться."""
        text = "Короткий текст"
        result = split_telegram_html_message(text, limit=4000)

        assert len(result) == 1
        assert result[0] == text

    def test_long_message_split(self):
        """Длинное сообщение должно разбиваться на части."""
        # Создаем сообщение длиннее limit
        text = "Часть 1\n\n" + ("X" * 4000) + "\n\nЧасть 2"
        result = split_telegram_html_message(text, limit=4000)

        assert len(result) > 1
        # Проверяем, что каждая часть не превышает лимит
        for part in result:
            assert len(part) <= 4000

    def test_split_preserves_content(self):
        """Разбиение должно сохранять весь контент."""
        text = "A" * 10000
        result = split_telegram_html_message(text, limit=4000)

        # Объединяем части обратно
        combined = "".join(result)
        assert len(combined) == len(text)

    def test_empty_message(self):
        """Пустое сообщение должно возвращать пустой список."""
        result = split_telegram_html_message("", limit=4000)

        assert result == []
