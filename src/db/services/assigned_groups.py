from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.schemas import GroupSchema
from src.db.models import AssignedGroupsModel, GroupsModel
from src.db.pagination import Page, paginate_select
from src.db.session import with_session


class AssignedGroupsService:
    """
    Сервис для работы с назначенными группами (assigned_groups).
    """

    @classmethod
    @with_session
    async def get_groups_page_by_teacher_id(
        cls,
        teacher_id: int,
        *,
        page: int = 1,
        per_page: int = 10,
        session: AsyncSession = None,
    ) -> Page[GroupSchema]:
        stmt = (
            select(GroupsModel)
            .join(
                AssignedGroupsModel,
                AssignedGroupsModel.group_id == GroupsModel.group_id,
            )
            .where(AssignedGroupsModel.teacher_id == teacher_id)
            .order_by(GroupsModel.group_id.asc())
        )

        # одна строка = одна связка teacher<->group
        count_stmt = (
            select(func.count())
            .select_from(AssignedGroupsModel)
            .where(AssignedGroupsModel.teacher_id == teacher_id)
        )

        page_models: Page = await paginate_select(
            session,
            stmt,
            page=page,
            per_page=per_page,
            count_stmt=count_stmt,
        )
        return page_models.map(GroupSchema.model_validate)
