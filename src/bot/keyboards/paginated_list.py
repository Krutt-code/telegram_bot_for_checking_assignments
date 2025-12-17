from __future__ import annotations

from typing import Dict, List, Union

from src.bot.keyboards.pagination import build_pagination_layout
from src.core.schemas import PaginatedListKeyboardSchema


def paginated_list_inline(
    data: Union[Dict, PaginatedListKeyboardSchema],
) -> List[List[Dict[str, str]]]:
    """
    Универсальный builder inline-клавиатуры:
    - список элементов (по 1 кнопке в строке)
    - дополнительные кнопки (каждая отдельной строкой)
    - пагинация (опционально)
    """
    if isinstance(data, PaginatedListKeyboardSchema):
        schema = data
    else:
        schema = PaginatedListKeyboardSchema.model_validate(data or {})

    layout: List[List[Dict[str, str]]] = []

    for item in schema.items:
        layout.append([{"text": item.text, "callback_data": item.callback_data}])

    for btn in schema.extra_buttons:
        layout.append([{"text": btn.text, "callback_data": btn.callback_data}])

    if schema.pagination is not None:
        layout.extend(
            build_pagination_layout(
                key=schema.pagination.key,
                page=schema.pagination.page,
                total_pages=schema.pagination.total_pages,
                hide_if_single_page=schema.pagination.hide_if_single_page,
            )
        )

    return layout
