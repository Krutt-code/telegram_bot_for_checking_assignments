from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.bot.lexicon.texts import TextsRU
from src.bot.session import UserSession
from src.core.enums import ReplyKeyboardTypeEnum
from src.db.use_cases.teacher_groups import TeacherGroupsUseCase


@dataclass(frozen=True, slots=True)
class JoinGroupPayload:
    group_id: int


def pack_join_group_payload(group_id: int) -> str:
    """
    Payload для deep-link `/start <payload>`.

    Telegram ограничивает допустимые символы, поэтому используем простой формат: jg<digits>
    """
    return f"jg{int(group_id)}"


def parse_join_group_payload(payload: str) -> Optional[JoinGroupPayload]:
    if not payload:
        return None
    payload = payload.strip()
    if not payload.startswith("jg"):
        return None
    raw = payload[2:]
    if not raw.isdigit():
        return None
    return JoinGroupPayload(group_id=int(raw))


async def perform_join_group(
    *,
    session: UserSession,
    group_id: int,
) -> bool:
    """
    Завершить присоединение к группе:
    - получить информацию (группа + преподаватель)
    - инициализировать роль STUDENT и привязать студента к группе
    - отправить сообщение об успехе + открыть меню студента
    """
    info = await TeacherGroupsUseCase.get_invite_info(group_id=group_id)
    if not info:
        await session.answer(TextsRU.STUDENT_JOIN_GROUP_INVALID)
        await session.answer(
            TextsRU.SELECT_ROLE, reply_markup=ReplyKeyboardTypeEnum.ROLE
        )
        return False

    await session.student_manager().initialize(group_id=group_id)

    await session.answer(
        TextsRU.STUDENT_JOIN_GROUP_SUCCESS.format(
            group_name=info.group_name,
            teacher_full_name=info.teacher_full_name,
        )
    )
    await session.answer(
        TextsRU.HELLO_STUDENT, reply_markup=ReplyKeyboardTypeEnum.STUDENT
    )
    return True
