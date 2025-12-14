from aiogram import Bot
from aiogram.filters import BaseFilter, Command
from aiogram.types import Message

from src.bot.lexicon.command_texts import COMMAND_DESCRIPTIONS_RU
from src.core.enums import CommandsEnum


class CommandFilter(BaseFilter):
    def __init__(self, *commands: CommandsEnum, check_command_text: bool = True):
        self.commands = commands
        self.check_command_text = check_command_text

    def _check_command_text(self, message: Message) -> bool:
        if not self.check_command_text:
            return False
        for command in self.commands:
            if message.text == COMMAND_DESCRIPTIONS_RU[command]:
                return True
        return False

    async def __call__(self, message: Message, bot: Bot) -> bool:
        return bool(
            await Command(*self.commands)(message, bot)
            or self._check_command_text(message)
        )
