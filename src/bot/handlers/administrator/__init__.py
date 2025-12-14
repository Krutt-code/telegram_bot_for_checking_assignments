from aiogram import Router

from src.bot.filters.access import IsAdminFilter

administrator_router = Router()
administrator_router.message.filter(IsAdminFilter())
administrator_router.callback_query.filter(IsAdminFilter())
