from aiogram import Router

from .callbacks import callbacks_router
from .message import message_router

other_router = Router()
other_router.include_router(message_router)
other_router.include_router(callbacks_router)
