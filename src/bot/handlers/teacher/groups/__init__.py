"""
Хэндлеры для работы с группами преподавателя в режиме преподавателя.

При переходе в меню "Группы" пользователь видит список групп, которые закреплены за ним.
Этот список отображается в виде кнопок к сообщению

Так же есть кнопка для создания новой группы.
"""

from aiogram import Router

from .actions import teacher_group_actions_router
from .create import teacher_groups_create_router
from .review import teacher_groups_review_router
from .students import teacher_group_students_router
from .view import teacher_group_view_router

teacher_groups_router = Router()
teacher_groups_router.include_router(teacher_groups_review_router)
teacher_groups_router.include_router(teacher_groups_create_router)
teacher_groups_router.include_router(teacher_group_view_router)
teacher_groups_router.include_router(teacher_group_actions_router)
teacher_groups_router.include_router(teacher_group_students_router)
