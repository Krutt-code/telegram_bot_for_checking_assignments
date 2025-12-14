from aiogram import Router

from .administrator import administrator_router
from .full_name import full_name_router
from .general_settings import general_settings_router
from .navigation import navigation_router
from .role import role_router
from .start import start_router
from .student import student_router
from .teacher import teacher_router

all_handlers_router = Router()

all_handlers_router.include_router(start_router)
all_handlers_router.include_router(navigation_router)
all_handlers_router.include_router(general_settings_router)
all_handlers_router.include_router(full_name_router)
all_handlers_router.include_router(role_router)
all_handlers_router.include_router(administrator_router)
all_handlers_router.include_router(student_router)
all_handlers_router.include_router(teacher_router)
