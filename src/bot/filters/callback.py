from __future__ import annotations

from typing import Any, Type

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery

from src.core.schemas import CallbackSchemaBase


class CallbackFilter(BaseFilter):
    """
    Универсальный фильтр callback_query по схемам callback_data.

    - Принимает классы схем (наследники CallbackSchemaBase)
    - Парсит callback.data ровно 1 раз
    - Может дополнительно проверять поля через kwargs (например key="teacher_groups")
    - В случае успеха прокидывает parsed объект в хендлер параметром `callback_data`
    """

    def __init__(self, *schemas: Type[CallbackSchemaBase], **equals: Any):
        self.schemas = schemas
        self.equals = equals

    async def __call__(self, callback: CallbackQuery) -> bool | dict[str, Any]:
        for schema in self.schemas:
            parsed = schema.parse(callback.data)
            if not parsed:
                continue

            ok = True
            for k, v in self.equals.items():
                current = getattr(parsed, k, None)
                # Поддерживаем predicate-значения, чтобы фильтровать сложнее чем по равенству
                # Пример: CallbackFilter(PaginationCallbackSchema, key=lambda s: s.startswith("x:"))
                if callable(v):
                    try:
                        if not v(current):
                            ok = False
                            break
                    except Exception:
                        ok = False
                        break
                    continue
                if current != v:
                    ok = False
                    break
            if not ok:
                continue

            return {"callback_data": parsed}
        return False
