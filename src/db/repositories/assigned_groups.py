from src.core.schemas import AssignedGroupCreateSchema, AssignedGroupSchema
from src.db.models import AssignedGroupsModel
from src.db.repositories.base_crud_methods import BaseCRUDMethods


class AssignedGroupsRepository(
    BaseCRUDMethods[AssignedGroupsModel, AssignedGroupSchema, AssignedGroupCreateSchema]
):
    model = AssignedGroupsModel
    schema = AssignedGroupSchema
    create_schema = AssignedGroupCreateSchema
    id_column = "assigned_group_id"
    base_relationships = ["teacher", "group"]
