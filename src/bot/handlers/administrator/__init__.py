from aiogram import Router

from src.bot.filters.access import IsAdminFilter

from .panel import admin_panel_router
from .user_bans import user_bans_router

administrator_router = Router()
administrator_router.message.filter(IsAdminFilter())
administrator_router.callback_query.filter(IsAdminFilter())

# Подключаем роутеры
administrator_router.include_router(admin_panel_router)
administrator_router.include_router(user_bans_router)
