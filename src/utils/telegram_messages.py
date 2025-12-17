from __future__ import annotations

from typing import List

TELEGRAM_MESSAGE_LIMIT = 4096


def split_telegram_message(text: str, limit: int = TELEGRAM_MESSAGE_LIMIT) -> List[str]:
    """
    Разбивает длинный текст на части, чтобы каждая была <= limit символов.

    Стратегия:
    - пытаемся резать по двойному переносу строки, затем по переносу, затем по пробелу;
    - если "удобного" разделителя нет — режем жёстко по limit.
    """

    if limit <= 0:
        raise ValueError("limit must be > 0")

    if text is None:
        return []

    text = str(text)
    if not text:
        return []

    parts: List[str] = []
    separators = ["\n\n", "\n", " "]

    remaining = text
    while len(remaining) > limit:
        window = remaining[: limit + 1]

        cut = -1
        for sep in separators:
            idx = window.rfind(sep, 0, limit + 1)
            if idx > cut:
                cut = idx

        if cut <= 0:
            # нет разделителей — режем жёстко
            chunk = remaining[:limit]
            parts.append(chunk)
            remaining = remaining[limit:]
            continue

        # cut указывает на начало сепаратора
        chunk = remaining[:cut].rstrip()
        if chunk:
            parts.append(chunk)
        remaining = remaining[cut:].lstrip()

    if remaining:
        parts.append(remaining)

    return parts


def split_telegram_html_message(
    html: str, limit: int = TELEGRAM_MESSAGE_LIMIT
) -> List[str]:
    """
    Разбивает HTML-текст на части <= limit, не ломая разметку Telegram HTML.

    Гарантии:
    - не режет внутри HTML-тегов вида `<...>`
    - не режет внутри HTML-сущностей вида `&...;`
    - на границе сообщения закрывает все открытые теги и переоткрывает их в следующем
    """

    if limit <= 0:
        raise ValueError("limit must be > 0")

    if html is None:
        return []

    html = str(html)
    if not html:
        return []

    def is_name_char(ch: str) -> bool:
        return ch.isalnum() or ch in {"-", ":"}

    def parse_tag_name(tag_text: str) -> str:
        # <tag ...> / </tag> / <tag/>
        i = 1
        if len(tag_text) >= 2 and tag_text[1] == "/":
            i = 2
        while i < len(tag_text) and tag_text[i].isspace():
            i += 1
        start = i
        while i < len(tag_text) and is_name_char(tag_text[i]):
            i += 1
        return tag_text[start:i].lower()

    def is_closing_tag(tag_text: str) -> bool:
        return tag_text.startswith("</")

    def is_self_closing(tag_text: str) -> bool:
        # Telegram HTML не документирует self-closing, но на всякий случай поддержим.
        return tag_text.endswith("/>") or tag_text.lower().startswith("<br")

    def close_text(tag_name: str) -> str:
        return f"</{tag_name}>"

    def closings_len(stack: list[tuple[str, str]]) -> int:
        return sum(len(close_text(name)) for name, _ in reversed(stack))

    def closings_text(stack: list[tuple[str, str]]) -> str:
        return "".join(close_text(name) for name, _ in reversed(stack))

    def reopen_text(stack: list[tuple[str, str]]) -> str:
        return "".join(open_tag for _, open_tag in stack)

    def apply_tag(stack: list[tuple[str, str]], tag_text: str) -> None:
        name = parse_tag_name(tag_text)
        if not name:
            return
        if is_self_closing(tag_text):
            return
        if is_closing_tag(tag_text):
            # pop last matching
            for idx in range(len(stack) - 1, -1, -1):
                if stack[idx][0] == name:
                    del stack[idx:]
                    break
            return
        # opening tag
        stack.append((name, tag_text))

    TELEGRAM_TAGS = {
        "b",
        "strong",
        "i",
        "em",
        "u",
        "ins",
        "s",
        "strike",
        "del",
        "span",
        "tg-spoiler",
        "code",
        "pre",
        "a",
    }

    def tokenize(s: str) -> List[str]:
        tokens: List[str] = []
        i = 0
        n = len(s)
        while i < n:
            ch = s[i]
            if ch == "<":
                j = s.find(">", i + 1)
                if j == -1:
                    tokens.append(s[i:])
                    break
                tokens.append(s[i : j + 1])
                i = j + 1
                continue
            if ch == "&":
                j = s.find(";", i + 1)
                if j != -1:
                    tokens.append(s[i : j + 1])
                    i = j + 1
                    continue
            tokens.append(ch)
            i += 1
        return tokens

    def is_tag(token: str) -> bool:
        return token.startswith("<") and token.endswith(">")

    def is_preferred_boundary(token: str) -> bool:
        # "Красивые" места разрыва: конец блоков/инлайнов, переносы, пробел.
        if token in {"\n", " "}:
            return True
        if is_tag(token) and token.startswith("</"):
            name = parse_tag_name(token)
            return name in TELEGRAM_TAGS
        return False

    def emit_chunk(
        start_stack: list[tuple[str, str]],
        tokens_in_chunk: List[str],
        stack_at_end: list[tuple[str, str]],
    ) -> str:
        return (
            reopen_text(start_stack)
            + "".join(tokens_in_chunk)
            + closings_text(stack_at_end)
        )

    parts: List[str] = []

    all_tokens = tokenize(html)
    start_stack: list[tuple[str, str]] = []
    stack: list[tuple[str, str]] = []
    chunk_tokens: List[str] = []
    # snapshots[k] = stack (как tuple) после добавления chunk_tokens[k]
    snapshots: List[tuple[tuple[str, str], ...]] = []

    idx = 0
    while idx < len(all_tokens):
        token = all_tokens[idx]

        # Оценим, влезет ли token, учитывая необходимость закрыть теги.
        tmp_stack = stack.copy()
        if is_tag(token):
            apply_tag(tmp_stack, token)
        reserve = closings_len(tmp_stack)
        prospective_len = (
            len(reopen_text(start_stack))
            + sum(len(t) for t in chunk_tokens)
            + len(token)
            + reserve
        )

        if prospective_len <= limit:
            chunk_tokens.append(token)
            if is_tag(token):
                apply_tag(stack, token)
            snapshots.append(tuple(stack))
            idx += 1
            continue

        # token не влез — надо зафлашить текущий chunk.
        if not chunk_tokens:
            # Случай "один токен не влезает": очень длинный тег/атрибуты.
            if len(token) > limit:
                return split_telegram_message(html, limit=limit)
            # В теории сюда почти не должны попадать, но обработаем.
            parts.append(emit_chunk(start_stack, [token], start_stack))
            idx += 1
            continue

        # Пытаемся найти ближайшую "хорошую" границу в уже набранном chunk.
        cut = None
        for k in range(len(chunk_tokens), 0, -1):
            if not is_preferred_boundary(chunk_tokens[k - 1]):
                continue
            stack_at_k = list(snapshots[k - 1]) if k > 0 else list(tuple(start_stack))
            candidate = emit_chunk(start_stack, chunk_tokens[:k], stack_at_k)
            if len(candidate) <= limit:
                cut = k
                break

        if cut is None:
            cut = len(chunk_tokens)
            stack_at_cut = list(snapshots[-1]) if snapshots else start_stack.copy()
        else:
            stack_at_cut = list(snapshots[cut - 1]) if cut > 0 else start_stack.copy()

        parts.append(emit_chunk(start_stack, chunk_tokens[:cut], stack_at_cut))

        # Оставшиеся токены из старого chunk переносим в начало следующего.
        leftover = chunk_tokens[cut:]

        # Следующий chunk стартует с логического состояния stack_at_cut
        start_stack = stack_at_cut
        stack = stack_at_cut.copy()
        chunk_tokens = []
        snapshots = []

        # Чтобы сохранить порядок, переносим leftover обратно в поток токенов.
        # (Сообщения небольшие, это ок по сложности.)
        all_tokens = leftover + all_tokens[idx:]
        idx = 0

    if chunk_tokens:
        parts.append(emit_chunk(start_stack, chunk_tokens, stack))

    return parts


def get_a_teg(href: str, text: str) -> str:
    return f'<a href="{href}">{text}</a>'
