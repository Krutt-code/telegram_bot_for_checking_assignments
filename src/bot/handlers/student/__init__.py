from aiogram import Router

from src.bot.filters.access import HasRealFullNameFilter, IsStudentFilter
from src.bot.handlers.student.answer import answer_router
from src.bot.handlers.student.answers import answers_router
from src.bot.handlers.student.group import group_router
from src.bot.handlers.student.homeworks import homeworks_router

student_router = Router()
student_router.message.filter(IsStudentFilter(), HasRealFullNameFilter())
student_router.callback_query.filter(IsStudentFilter(), HasRealFullNameFilter())

student_router.include_router(group_router)
student_router.include_router(homeworks_router)
student_router.include_router(answer_router)
student_router.include_router(answers_router)
