from src.core.schemas import TelegramFileCreateSchema, TelegramFileSchema
from src.db.models import TelegramFilesModel
from src.db.repositories.base_crud_methods import BaseCRUDMethods


class TelegramFilesRepository(
    BaseCRUDMethods[TelegramFilesModel, TelegramFileSchema, TelegramFileCreateSchema]
):
    model = TelegramFilesModel
    schema = TelegramFileSchema
    create_schema = TelegramFileCreateSchema
    id_column = "telegram_file_id"
