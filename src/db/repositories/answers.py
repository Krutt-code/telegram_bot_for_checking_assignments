from src.core.schemas import AnswerCreateSchema, AnswerSchema
from src.db.models import AnswersModel
from src.db.repositories.base_crud_methods import BaseCRUDMethods


class AnswersRepository(
    BaseCRUDMethods[AnswersModel, AnswerSchema, AnswerCreateSchema]
):
    model = AnswersModel
    schema = AnswerSchema
    create_schema = AnswerCreateSchema
    id_column = "answer_id"
    base_relationships = ["homework", "student"]
