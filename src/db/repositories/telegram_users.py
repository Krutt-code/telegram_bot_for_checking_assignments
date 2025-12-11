from src.core.schemas import TelegramUserCreateSchema, TelegramUserSchema
from src.db.models import TelegramUsersModel
from src.db.repositories.base_crud_methods import BaseCRUDMethods


class TelegramUsersRepository(
    BaseCRUDMethods[TelegramUsersModel, TelegramUserSchema, TelegramUserCreateSchema]
):
    model = TelegramUsersModel
    schema = TelegramUserSchema
    create_schema = TelegramUserCreateSchema
    id_column = "user_id"
