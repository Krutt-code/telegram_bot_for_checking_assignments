"""
Функциональные тесты системы навигации.
"""

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.navigation import NavigationManager
from src.core.enums import CommandsEnum, ReplyKeyboardTypeEnum


class TestNavigationSystem:
    """Тесты системы навигации бота."""

    @pytest.mark.asyncio
    async def test_navigation_push_and_pop(self):
        """Тест добавления и возврата шагов навигации."""
        storage = MemoryStorage()
        key = StorageKey(bot_id=123, chat_id=456, user_id=789)
        state = FSMContext(storage=storage, key=key)

        nav = NavigationManager(state)

        # Добавляем шаги в историю
        await nav.push(CommandsEnum.START, ReplyKeyboardTypeEnum.ROLE)
        await nav.push(CommandsEnum.STUDENT_HOMEWORKS, ReplyKeyboardTypeEnum.STUDENT)

        # Проверяем текущий (последний) шаг
        current = await nav.get_previous()
        assert current is not None
        assert current.command == CommandsEnum.STUDENT_HOMEWORKS

        # Возвращаемся назад (удаляет текущий, возвращает предыдущий)
        previous = await nav.pop_previous()

        assert previous is not None
        assert previous.command == CommandsEnum.START
        assert previous.keyboard == ReplyKeyboardTypeEnum.ROLE

    @pytest.mark.asyncio
    async def test_navigation_clear(self):
        """Тест очистки истории навигации."""
        storage = MemoryStorage()
        key = StorageKey(bot_id=123, chat_id=456, user_id=789)
        state = FSMContext(storage=storage, key=key)

        nav = NavigationManager(state)

        # Добавляем шаги
        await nav.push(CommandsEnum.START, None)
        await nav.push(CommandsEnum.STUDENT_HOMEWORKS, None)

        # Очищаем историю
        await nav.clear()

        # Проверяем, что история пуста
        history = await nav.get_history()
        assert len(history) == 0
