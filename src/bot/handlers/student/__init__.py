from aiogram import Router

from src.bot.filters.access import HasRealFullNameFilter, IsStudentFilter

student_router = Router()
student_router.message.filter(IsStudentFilter(), HasRealFullNameFilter())
student_router.callback_query.filter(IsStudentFilter(), HasRealFullNameFilter())
