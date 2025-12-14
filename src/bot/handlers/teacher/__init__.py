from aiogram import Router

from src.bot.filters.access import HasRealFullNameFilter, IsTeacherFilter

teacher_router = Router()
teacher_router.message.filter(IsTeacherFilter(), HasRealFullNameFilter())
teacher_router.callback_query.filter(IsTeacherFilter(), HasRealFullNameFilter())
