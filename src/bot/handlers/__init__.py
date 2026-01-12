from aiogram import Router

from .administrator import administrator_router
from .banned import banned_router
from .base import base_router
from .other import other_router
from .student import student_router
from .teacher import teacher_router

all_handlers_router = Router()

# Обработчик заблокированных пользователей должен быть ПЕРВЫМ
all_handlers_router.include_router(banned_router)

all_handlers_router.include_router(base_router)
all_handlers_router.include_router(administrator_router)
all_handlers_router.include_router(student_router)
all_handlers_router.include_router(teacher_router)
all_handlers_router.include_router(other_router)
