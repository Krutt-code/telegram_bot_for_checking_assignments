from src.core.schemas import HomeworkGroupCreateSchema, HomeworkGroupSchema
from src.db.models import HomeworkGroupsModel
from src.db.repositories.base_crud_methods import BaseCRUDMethods


class HomeworkGroupsRepository(
    BaseCRUDMethods[HomeworkGroupsModel, HomeworkGroupSchema, HomeworkGroupCreateSchema]
):
    model = HomeworkGroupsModel
    schema = HomeworkGroupSchema
    create_schema = HomeworkGroupCreateSchema
    id_column = "homework_group_id"
