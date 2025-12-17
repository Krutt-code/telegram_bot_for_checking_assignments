from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Callable, Generic, List, Optional, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True, slots=True)
class Page(Generic[T]):
    items: List[T]
    page: int
    per_page: int
    total_items: int
    total_pages: int

    def map(self, fn: Callable[[T], U]) -> "Page[U]":
        return Page(
            items=[fn(x) for x in self.items],
            page=self.page,
            per_page=self.per_page,
            total_items=self.total_items,
            total_pages=self.total_pages,
        )


def _calc_total_pages(total_items: int, per_page: int) -> int:
    if per_page <= 0 or total_items <= 0:
        return 1
    return max(1, int(ceil(total_items / per_page)))


def _normalize_page(page: int, total_pages: int) -> int:
    page = max(1, int(page))
    if page > total_pages:
        page = total_pages
    return page


async def paginate_select(
    session: AsyncSession,
    stmt: Select,
    *,
    page: int = 1,
    per_page: int = 10,
    count_stmt: Optional[Select] = None,
) -> Page:
    """
    Универсальная пагинация для SQLAlchemy Select (async).
    """
    per_page = max(1, int(per_page))

    if count_stmt is None:
        subq = stmt.order_by(None).subquery()
        count_stmt = select(func.count()).select_from(subq)

    total_items = int((await session.scalar(count_stmt)) or 0)
    total_pages = _calc_total_pages(total_items, per_page)
    page = _normalize_page(page, total_pages)

    offset = (page - 1) * per_page
    res = await session.execute(stmt.limit(per_page).offset(offset))
    items = res.unique().scalars().all()

    return Page(
        items=list(items),
        page=page,
        per_page=per_page,
        total_items=total_items,
        total_pages=total_pages,
    )
