from aiogram import Router

from .callbacks import callbacks_router
from .full_name import full_name_router
from .general_settings import general_settings_router
from .help import help_router
from .navigation import navigation_router
from .role import role_router
from .start import start_router

other_router = Router()
other_router.include_router(callbacks_router)
other_router.include_router(full_name_router)
other_router.include_router(general_settings_router)
other_router.include_router(navigation_router)
other_router.include_router(role_router)
other_router.include_router(start_router)
other_router.include_router(help_router)
