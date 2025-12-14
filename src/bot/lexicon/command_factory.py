from src.core.enums import CommandsEnum


class CommandFactory:
    @staticmethod
    def for_handler(command: CommandsEnum) -> str:
        """Без /, для использования в хендлерах"""
        return command.value

    @staticmethod
    def for_button(command: CommandsEnum) -> str:
        """С /, для кнопок"""
        return f"/{command.value}"
