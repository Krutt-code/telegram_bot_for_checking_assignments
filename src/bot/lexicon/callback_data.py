"""
Шаблоны строк callback_data.

Идея:
- Храним здесь короткие шаблоны (Telegram ограничивает callback_data по длине).
- Дальше в коде используем схемы (pydantic), которые умеют pack()/parse() по этим шаблонам.
"""

# Важно держать callback_data коротким (до ~64 байт).
CALLBACK_DATA: dict[str, str] = {
    # Заглушка (не делает ничего, просто закрывает "часики")
    "NOOP": "noop",
    # Универсальная пагинация: pg:<key>:<page>
    "PAGINATION": "pg:{key}:{page}",
    # Действия с группами преподавателя: tgrp:<action>:<group_id>
    "TEACHER_GROUP": "tgrp:{action}:{group_id}",
    # Действия со студентами в группе преподавателя: tgst:<action>:<group_id>:<student_id>:<page>
    "TEACHER_GROUP_STUDENT": "tgst:{action}:{group_id}:{student_id}:{page}",
    # Действия над заданием студента: shw:<action>:<homework_id>
    "STUDENT_HOMEWORK": "shw:{action}:{homework_id}",
}
