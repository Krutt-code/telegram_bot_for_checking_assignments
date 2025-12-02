from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import AdminsModel
from src.database.session import with_session


class AdminsRepository:
    @staticmethod
    @with_session
    async def is_admin(user_id: int, session: AsyncSession = None) -> bool:
        """
        Отдает True если пользователь является администратором, False иначе.
        """
        res = await session.execute(
            select(AdminsModel).filter(AdminsModel.user_id == user_id)
        )
        return res.scalars().first() is not None
