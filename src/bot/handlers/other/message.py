from aiogram import Router
from aiogram.types import Message

from src.core.logger import get_function_logger

message_router = Router()


@message_router.message()
async def other_message_handler(message: Message) -> None:
    logger = get_function_logger(other_message_handler)
    logger.debug(f"Other message: {message.text}")
