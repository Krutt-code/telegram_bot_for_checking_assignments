"""
Система централизованной навигации для телеграм-бота.

Управляет историей переходов пользователя и обеспечивает возможность
возврата на предыдущие шаги или отмены текущего сценария.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Sequence

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.lexicon.texts import TextsRU
from src.core.enums import CommandsEnum, ReplyKeyboardTypeEnum
from src.core.logger import get_class_logger
from src.core.schemas import NavigationStepSchema

if TYPE_CHECKING:
    from src.bot.session import UserSession

# Команды, которые являются точками входа и очищают историю навигации
ENTRY_POINT_COMMANDS = {
    CommandsEnum.START,
    CommandsEnum.ROLE,
    CommandsEnum.STUDENT_ROLE,
    CommandsEnum.TEACHER_ROLE,
    CommandsEnum.ADMIN_PANEL,
}


class NavigationManager:
    """
    Менеджер навигации для управления историей переходов пользователя.

    Использует FSMContext для хранения истории навигации.
    """

    HISTORY_KEY = "navigation_history"
    CANCEL_TARGET_KEY = "navigation_cancel_target"
    _NAV_KEYS = {HISTORY_KEY, CANCEL_TARGET_KEY}

    def __init__(self, state: FSMContext):
        self.state = state
        self.logger = get_class_logger(self)

    async def _set_history(self, history: Sequence[NavigationStepSchema]) -> None:
        await self.state.update_data(
            {self.HISTORY_KEY: [step.model_dump(mode="json") for step in history]}
        )

    async def get_history(self) -> List[NavigationStepSchema]:
        """Получить историю навигации."""
        data = await self.state.get_data()
        raw = data.get(self.HISTORY_KEY, [])
        if not raw:
            return []
        return [NavigationStepSchema.model_validate(item) for item in raw]

    async def set_cancel_target(self, step: Optional[NavigationStepSchema]) -> None:
        """
        Установить "якорь отмены" — куда возвращаться при CANCEL.

        Обычно это экран/меню, из которого пользователь вошёл в сценарий.
        """
        if step is None:
            await self.state.update_data({self.CANCEL_TARGET_KEY: None})
            return
        await self.state.update_data(
            {self.CANCEL_TARGET_KEY: step.model_dump(mode="json")}
        )

    async def get_cancel_target(self) -> Optional[NavigationStepSchema]:
        """Получить "якорь отмены"."""
        data = await self.state.get_data()
        raw = data.get(self.CANCEL_TARGET_KEY)
        if not raw:
            return None
        return NavigationStepSchema.model_validate(raw)

    async def clear_cancel_target(self) -> None:
        """Очистить "якорь отмены"."""
        await self.state.update_data({self.CANCEL_TARGET_KEY: None})

    async def push(
        self,
        command: CommandsEnum,
        keyboard: Optional[ReplyKeyboardTypeEnum] = None,
        text: Optional[str] = None,
    ) -> None:
        """
        Добавить шаг в историю навигации.

        Args:
            command: Команда для возврата
            keyboard: Клавиатура для отображения
            text: Текст сообщения (опционально)
        """
        history = await self.get_history()
        self.logger.debug(f"Добавляем шаг в историю навигации: {command}")
        history.append(
            NavigationStepSchema(command=command, keyboard=keyboard, text=text)
        )
        await self._set_history(history)

    async def pop(self) -> Optional[NavigationStepSchema]:
        """
        Удалить и вернуть последний шаг из истории.

        Returns:
            Словарь с данными предыдущего шага или None, если история пуста
        """
        history = await self.get_history()
        self.logger.debug(f"Удаляем последний шаг из истории: {history[-1]}")
        if not history:
            return None

        previous_step = history.pop()
        await self._set_history(history)
        return previous_step

    async def clear(self) -> None:
        """Очистить историю навигации."""
        await self.state.update_data({self.HISTORY_KEY: []})

    async def clear_fsm_keep_history(self) -> None:
        """
        Полностью очистить FSM (state + data), но сохранить историю навигации.

        Это нужно для универсальной "Отмены": обычно мы хотим стереть данные сценария,
        но НЕ хотим терять navigation_history.
        """
        history = await self.get_history()
        cancel_target = await self.get_cancel_target()
        await self.state.clear()
        await self._set_history(history)
        await self.set_cancel_target(cancel_target)
        self.logger.debug(f"Очищаем FSM и сохраняем историю навигации: {history}")

    async def clear_state_and_data_keep_navigation(self) -> None:
        """
        Завершить сценарий: сбросить state и очистить data от сценарных ключей,
        сохранив только данные навигации.

        Это безопаснее, чем `state.set_state(None)`, потому что не оставляет
        "мусор" из временных ключей сценария в FSMContext.data.
        """
        data = await self.state.get_data()
        preserved = {k: v for k, v in data.items() if k in self._NAV_KEYS}
        await self.state.set_state(None)
        await self.state.set_data(preserved)

    async def get_previous(self) -> Optional[NavigationStepSchema]:
        """
        Получить предыдущий шаг без удаления из истории.

        Returns:
            Словарь с данными предыдущего шага или None
        """
        history = await self.get_history()
        return history[-1] if history else None

    async def pop_previous(
        self,
        default_keyboard: Optional[ReplyKeyboardTypeEnum] = None,
        default_text: Optional[str] = None,
    ) -> Optional[NavigationStepSchema]:
        """
        Получить предыдущий шаг, удалив только текущий шаг из истории.

        Этот метод упрощает типичный паттерн возврата назад:
        1. Удаляет текущий шаг из истории
        2. Получает предыдущий шаг
        3. Возвращает данные с дефолтными значениями если не указаны

        Важно: предыдущий шаг НЕ удаляется, чтобы повторные заходы в один и тот же
        сценарий корректно возвращались назад (история сохраняет текущий экран).

        Args:
            default_keyboard: Клавиатура по умолчанию, если не указана в истории
            default_text: Текст по умолчанию, если не указан в истории

        Returns:
            Словарь с данными предыдущего шага или None, если истории нет.
            Словарь содержит: {"keyboard": ..., "text": ..., "command": ...}
        """
        history = await self.get_history()

        # Проверяем что есть хотя бы 2 шага (текущий и предыдущий)
        if len(history) < 2:
            return None

        # Удаляем текущий шаг
        await self.pop()

        # Берём предыдущий шаг, но НЕ удаляем его из истории
        previous_step = await self.get_previous()
        if previous_step is None:
            return None

        updates: dict = {}
        if previous_step.keyboard is None and default_keyboard is not None:
            updates["keyboard"] = default_keyboard
        if previous_step.text is None and default_text is not None:
            updates["text"] = default_text

        return previous_step.model_copy(update=updates) if updates else previous_step

    async def rewind_history_to(self, command: CommandsEnum) -> bool:
        """
        Обрезать историю до последнего вхождения command (включительно).
        Возвращает True если command найден, иначе False (история не меняется).
        """
        history = await self.get_history()
        last_idx = -1
        for i, step in enumerate(history):
            if step.command == command:
                last_idx = i
        if last_idx < 0:
            return False
        await self._set_history(history[: last_idx + 1])
        return True


class NavigationHelper:
    """
    Вспомогательный класс для работы с навигацией в обработчиках.
    """

    @staticmethod
    async def register_entry_point(state: FSMContext) -> None:
        """
        Зарегистрировать точку входа (очищает историю навигации).

        Args:
            state: FSM контекст
        """
        nav_manager = NavigationManager(state)
        await nav_manager.clear()

    @staticmethod
    async def register_navigation_step(
        state: FSMContext,
        command: CommandsEnum,
        keyboard: Optional[ReplyKeyboardTypeEnum] = None,
        text: Optional[str] = None,
    ) -> None:
        """
        Зарегистрировать шаг навигации.

        Args:
            state: FSM контекст
            command: Команда текущего шага
            keyboard: Клавиатура текущего шага
            text: Текст сообщения (опционально)
        """
        # Проверяем, не является ли команда точкой входа
        if command in ENTRY_POINT_COMMANDS:
            await NavigationHelper.register_entry_point(state)

        nav_manager = NavigationManager(state)
        await nav_manager.push(command, keyboard, text)

    @staticmethod
    async def go_back(
        message: Message, state: FSMContext, session: "UserSession"
    ) -> bool:
        """
        Вернуться на предыдущий шаг.

        Args:
            message: Сообщение пользователя
            state: FSM контекст
            session: Сессия пользователя

        Returns:
            True, если возврат выполнен успешно, False в противном случае
        """
        nav_manager = NavigationManager(state)

        # Получаем предыдущий шаг с дефолтными значениями
        previous_step = await nav_manager.pop_previous(
            default_text=TextsRU.SELECT_ACTION
        )

        if not previous_step:
            await session.answer(TextsRU.BACK_NOT_POSSIBLE)
            return False

        # Возвращаемся на предыдущий шаг
        await session.answer(TextsRU.BACK_OK)
        await session.answer(
            previous_step.text or TextsRU.SELECT_ACTION,
            reply_markup=previous_step.keyboard,
        )

        return True


async def handle_back_command(
    message: Message, state: FSMContext, session: "UserSession"
) -> None:
    """
    Обработчик команды "Назад".

    Args:
        message: Сообщение пользователя
        state: FSM контекст
        session: Сессия пользователя
    """
    await NavigationHelper.go_back(message, state, session)
