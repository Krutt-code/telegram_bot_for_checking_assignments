from sqlalchemy import select

from src.core.schemas import UserLockSchema
from src.db.models import UserLocksModel
from src.db.repositories.base_crud_methods import BaseCRUDMethods
from src.db.session import with_session
from src.db.wraps import log_db_performance


class UserLocksRepository(
    BaseCRUDMethods[UserLocksModel, UserLockSchema, UserLockSchema]
):
    model = UserLocksModel
    schema = UserLockSchema
    create_schema = UserLockSchema
    id_column = "user_id"
    base_relationships = []

    @classmethod
    @with_session
    @log_db_performance
    async def is_banned(cls, user_id: int, session=None) -> bool:
        """
        Проверяет, заблокирован ли пользователь.

        Args:
            user_id: ID пользователя
            session: Сессия БД

        Returns:
            True если пользователь заблокирован, иначе False
        """
        stmt = select(UserLocksModel).where(UserLocksModel.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @classmethod
    @with_session
    @log_db_performance
    async def get_all_banned_user_ids(cls, session=None) -> list[int]:
        """
        Получает список всех заблокированных пользователей.

        Args:
            session: Сессия БД

        Returns:
            Список ID заблокированных пользователей
        """
        stmt = select(UserLocksModel.user_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    @with_session
    @log_db_performance
    async def ban_user(
        cls, user_id: int, reason: str | None = None, session=None
    ) -> None:
        """
        Блокирует пользователя.

        Args:
            user_id: ID пользователя
            reason: Причина блокировки
            session: Сессия БД
        """
        lock_data = UserLockSchema(user_id=user_id, reason=reason)
        await cls.create(lock_data, session=session)

    @classmethod
    @with_session
    @log_db_performance
    async def unban_user(cls, user_id: int, session=None) -> None:
        """
        Разблокирует пользователя.

        Args:
            user_id: ID пользователя
            session: Сессия БД
        """
        await cls.delete_by_id(user_id, session=session)
