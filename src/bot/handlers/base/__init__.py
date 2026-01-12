from aiogram import Router

from .full_name import full_name_router
from .general_settings import general_settings_router
from .help import help_router
from .navigation import navigation_router
from .role import role_router
from .start import start_router

base_router = Router()

base_router.include_router(start_router)
base_router.include_router(help_router)
base_router.include_router(role_router)
base_router.include_router(general_settings_router)
base_router.include_router(full_name_router)
base_router.include_router(navigation_router)
