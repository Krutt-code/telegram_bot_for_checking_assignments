from src.core.schemas import TeacherCreateSchema, TeacherSchema
from src.db.models import TeachersModel
from src.db.repositories.base_crud_methods import BaseCRUDMethods


class TeachersRepository(
    BaseCRUDMethods[TeachersModel, TeacherSchema, TeacherCreateSchema]
):
    model = TeachersModel
    schema = TeacherSchema
    create_schema = TeacherCreateSchema
    id_column = "teacher_id"
    base_relationships = ["user"]
