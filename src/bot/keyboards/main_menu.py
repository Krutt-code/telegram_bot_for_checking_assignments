from aiogram import Bot
from aiogram.types import BotCommand

from src.bot.lexicon.command_factory import CommandFactory
from src.bot.lexicon.command_texts import COMMAND_DESCRIPTIONS_RU
from src.core.enums import CommandsEnum

commands: dict[str, str] = {
    CommandFactory.for_button(CommandsEnum.START): COMMAND_DESCRIPTIONS_RU[
        CommandsEnum.START
    ],
    CommandFactory.for_button(CommandsEnum.HELP): COMMAND_DESCRIPTIONS_RU[
        CommandsEnum.HELP
    ],
    CommandFactory.for_button(CommandsEnum.ROLE): COMMAND_DESCRIPTIONS_RU[
        CommandsEnum.ROLE
    ],
    CommandFactory.for_button(CommandsEnum.GENERAL_SETTINGS): COMMAND_DESCRIPTIONS_RU[
        CommandsEnum.GENERAL_SETTINGS
    ],
}


# Функция для настройки кнопки Menu бота
async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command=command, description=description)
        for command, description in commands.items()
    ]
    await bot.set_my_commands(main_menu_commands)
