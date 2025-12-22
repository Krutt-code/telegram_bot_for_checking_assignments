"""
Хэндлеры для заданий преподавателя:
- просмотр текущих выданных заданий (пагинация)
- создание задания (FSM)
- редактирование/удаление (inline-кнопки)
"""

from aiogram import Router

from .actions import teacher_homework_actions_router
from .create import teacher_homework_create_router
from .edit import teacher_homework_edit_router
from .review import teacher_homeworks_review_router

teacher_homeworks_router = Router()
teacher_homeworks_router.include_router(teacher_homeworks_review_router)
teacher_homeworks_router.include_router(teacher_homework_create_router)
teacher_homeworks_router.include_router(teacher_homework_actions_router)
teacher_homeworks_router.include_router(teacher_homework_edit_router)
