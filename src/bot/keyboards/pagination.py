from __future__ import annotations

from typing import Dict, List, Tuple

from src.bot.lexicon.callback_data import CALLBACK_DATA
from src.core.schemas import PaginationCallbackSchema


def clamp_page(page: int, total_pages: int) -> Tuple[int, int]:
    """
    Нормализует page/total_pages:
    - total_pages минимум 1
    - page в диапазоне [1..total_pages]
    """
    total_pages = max(1, int(total_pages))
    page = max(1, int(page))
    if page > total_pages:
        page = total_pages
    return page, total_pages


def build_pagination_layout(
    *,
    key: str,
    page: int,
    total_pages: int,
    prev_text: str = "◀",
    next_text: str = "▶",
    counter_template: str = "{page}/{total_pages}",
    hide_if_single_page: bool = True,
) -> List[List[Dict[str, str]]]:
    """
    Возвращает layout (в формате вашего KeyboardFactory) для одной строки пагинации.

    Можно использовать как standalone inline-клавиатуру или как "ряд" внутри более сложной клавиатуры.
    """
    page, total_pages = clamp_page(page, total_pages)
    if hide_if_single_page and total_pages <= 1:
        return []

    noop = CALLBACK_DATA["NOOP"]
    prev_cb = (
        PaginationCallbackSchema(key=key, page=page - 1).pack() if page > 1 else noop
    )
    next_cb = (
        PaginationCallbackSchema(key=key, page=page + 1).pack()
        if page < total_pages
        else noop
    )

    counter_text = counter_template.format(page=page, total_pages=total_pages)
    counter_cb = noop

    return [
        [
            {"text": prev_text, "callback_data": prev_cb},
            {"text": counter_text, "callback_data": counter_cb},
            {"text": next_text, "callback_data": next_cb},
        ]
    ]
