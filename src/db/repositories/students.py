from src.core.schemas import StudentCreateSchema, StudentSchema
from src.db.models import StudentsModel
from src.db.repositories.base_crud_methods import BaseCRUDMethods


class StudentsRepository(
    BaseCRUDMethods[StudentsModel, StudentSchema, StudentCreateSchema]
):
    model = StudentsModel
    schema = StudentSchema
    create_schema = StudentCreateSchema
    id_column = "student_id"
    base_relationships = ["user"]
