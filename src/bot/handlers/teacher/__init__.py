from aiogram import Router

from src.bot.filters.access import HasRealFullNameFilter, IsTeacherFilter
from src.bot.handlers.teacher.groups import teacher_groups_router

teacher_router = Router()
teacher_router.message.filter(IsTeacherFilter(), HasRealFullNameFilter())
teacher_router.callback_query.filter(IsTeacherFilter(), HasRealFullNameFilter())

teacher_router.include_router(teacher_groups_router)
