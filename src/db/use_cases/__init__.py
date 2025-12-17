"""
Use-cases / orchestrators (внутри слоя db).

Здесь лежат бизнес-операции, которые:
- трогают несколько таблиц/репозиториев,
- должны выполняться атомарно (одна транзакция),
- агрегируют вызовы низкоуровневых db/services.
"""

from .assignments import AssignmentsUseCase
from .teacher_groups import TeacherGroupsUseCase

__all__ = ["AssignmentsUseCase", "TeacherGroupsUseCase"]
