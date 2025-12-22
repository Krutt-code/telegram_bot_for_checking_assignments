from src.core.schemas import HomeworkCreateSchema, HomeworkSchema
from src.db.models import HomeworksModel
from src.db.repositories.base_crud_methods import BaseCRUDMethods


class HomeworksRepository(
    BaseCRUDMethods[HomeworksModel, HomeworkSchema, HomeworkCreateSchema]
):
    model = HomeworksModel
    schema = HomeworkSchema
    create_schema = HomeworkCreateSchema
    id_column = "homework_id"
    base_relationships = ["teacher", "teacher.user"]
