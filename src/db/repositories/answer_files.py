from src.core.schemas import AnswerFileCreateSchema, AnswerFileSchema
from src.db.models import AnswersFilesModel
from src.db.repositories.base_crud_methods import BaseCRUDMethods


class AnswersFilesRepository(
    BaseCRUDMethods[AnswersFilesModel, AnswerFileSchema, AnswerFileCreateSchema]
):
    model = AnswersFilesModel
    schema = AnswerFileSchema
    create_schema = AnswerFileCreateSchema
    id_column = "answer_file_id"
    base_relationships = ["telegram_file"]
