from src.core.schemas import HomeworkFileCreateSchema, HomeworkFileSchema
from src.db.models import HomeworkFilesModel
from src.db.repositories.base_crud_methods import BaseCRUDMethods


class HomeworkFilesRepository(
    BaseCRUDMethods[HomeworkFilesModel, HomeworkFileSchema, HomeworkFileCreateSchema]
):
    model = HomeworkFilesModel
    schema = HomeworkFileSchema
    create_schema = HomeworkFileCreateSchema
    id_column = "homeworks_file_id"
    base_relationships = ["telegram_file"]
