from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import AdminsModel
from src.db.session import with_session
from src.db.wraps import log_db_performance


class AdminsRepository:
    @staticmethod
    @log_db_performance
    @with_session
    async def is_admin(user_id: int, session: AsyncSession = None) -> bool:
        """
        Отдает True если пользователь является администратором, False иначе.
        """
        res = await session.execute(
            select(AdminsModel).filter(AdminsModel.user_id == user_id)
        )
        return res.scalars().first() is not None

    @staticmethod
    @log_db_performance
    @with_session
    async def get_all_admin_ids(session: AsyncSession = None) -> list[int]:
        """
        Возвращает список ID всех администраторов.
        """
        res = await session.execute(select(AdminsModel.user_id))
        return [row[0] for row in res.all()]
