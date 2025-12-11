from src.core.schemas import GroupCreateSchema, GroupSchema
from src.db.models import GroupsModel
from src.db.repositories.base_crud_methods import BaseCRUDMethods


class GroupsRepository(BaseCRUDMethods[GroupsModel, GroupSchema, GroupCreateSchema]):
    model = GroupsModel
    schema = GroupSchema
    create_schema = GroupCreateSchema
    id_column = "group_id"
