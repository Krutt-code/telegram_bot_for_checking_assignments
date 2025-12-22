from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.schemas import AssignedGroupSchema, GroupSchema
from src.db.models import AssignedGroupsModel, GroupsModel
from src.db.pagination import Page, paginate_select
from src.db.repositories import AssignedGroupsRepository
from src.db.session import with_session


class AssignedGroupsService:
    """
    Сервис для работы с назначенными группами.
    """

    assigned_groups_repository: AssignedGroupsRepository = AssignedGroupsRepository

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

    @classmethod
    @with_session
    async def get_by_group_id(
        cls, group_id: int, session: AsyncSession = None
    ) -> Optional[AssignedGroupSchema]:
        assigned_groups = await cls.assigned_groups_repository.get_all_where(
            where={AssignedGroupsModel.group_id: group_id},
            load_relationships=["teacher", "teacher.user", "group"],
            session=session,
        )
        return assigned_groups[0] if assigned_groups else None

    @classmethod
    @with_session
    async def get_all_groups_by_teacher_id(
        cls,
        teacher_id: int,
        *,
        session: AsyncSession = None,
    ) -> list[GroupSchema]:
        stmt = (
            select(GroupsModel)
            .join(
                AssignedGroupsModel,
                AssignedGroupsModel.group_id == GroupsModel.group_id,
            )
            .where(AssignedGroupsModel.teacher_id == teacher_id)
            .order_by(GroupsModel.group_id.asc())
        )
        res = await session.execute(stmt)
        models = res.unique().scalars().all()
        return [GroupSchema.model_validate(m) for m in models]
