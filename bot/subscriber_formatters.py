from __future__ import annotations

from bot.models import Vacancy
from bot.formatters import (
    SEPARATOR,
    TELEGRAM_MAX_LENGTH,
    escape_html,
    format_continuation_header,
    format_vacancy,
)

SOURCE_LABELS = {
    "hh.ru": "HeadHunter",
    "habr.com": "Habr Career",
    "geekjob.ru": "GeekJob",
    "getmatch.ru": "GetMatch",
}


def format_subscriber_header(
    role_label: str, new_count: int, total_found: int, max_age_hours: int = 72
) -> str:
    if new_count == 0:
        return (
            f"📭 <b>Новых вакансий {escape_html(role_label)} нет</b>\n"
            f"Найдено всего: {total_found}\n"
            f"Учитываются только вакансии за последние {max_age_hours} ч"
        )
    return (
        f"✨ <b>{new_count} новых вакансий</b> {escape_html(role_label)} "
        f"(за последние {max_age_hours} ч)\n"
        f"Источники: {', '.join(SOURCE_LABELS.values())}"
    )


def format_subscriber_digest(
    role_label: str,
    new_vacancies: list[Vacancy],
    total_found: int,
    max_age_hours: int = 72,
) -> tuple[list[str], int]:
    if not new_vacancies:
        return [format_subscriber_header(role_label, 0, total_found, max_age_hours)], 0

    messages: list[str] = []
    parts = [format_subscriber_header(role_label, len(new_vacancies), total_found, max_age_hours)]
    included = 0

    for vacancy in new_vacancies:
        block = format_vacancy(vacancy)
        if len(SEPARATOR.join(parts + [block])) <= TELEGRAM_MAX_LENGTH:
            parts.append(block)
            included += 1
            continue

        if parts:
            messages.append(SEPARATOR.join(parts))

        parts = [block]
        if len(parts[0]) > TELEGRAM_MAX_LENGTH:
            parts = [parts[0][: TELEGRAM_MAX_LENGTH - 1] + "…"]
        included += 1

    if parts:
        messages.append(SEPARATOR.join(parts))

    if len(messages) > 1:
        total_parts = len(messages)
        messages[1:] = [
            format_continuation_header(index, total_parts) + SEPARATOR + message
            for index, message in enumerate(messages[1:], start=2)
        ]

    return messages, included
