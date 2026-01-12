from aiogram import Router

from .administrator import administrator_router
from .other import other_router
from .student import student_router
from .teacher import teacher_router

all_handlers_router = Router()

all_handlers_router.include_router(administrator_router)
all_handlers_router.include_router(student_router)
all_handlers_router.include_router(teacher_router)
all_handlers_router.include_router(other_router)
