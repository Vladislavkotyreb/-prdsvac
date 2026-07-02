"""Разовый тест: реальный фетч и отправка превью админу в DM."""

from __future__ import annotations

import asyncio
import logging
from collections import Counter

from aiogram import Bot
from aiogram.enums import ParseMode

from bot.config import Settings
from bot.dates import dedupe_by_title_company, is_fresh
from bot.roles import get_role
from bot.russian import format_digest_roles_label
from bot.service import VacancyService
from bot.database import VacancyDatabase
from bot.subscriber_collect import collect_for_role
from bot.subscriber_formatters import format_subscriber_digest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

ROLE_IDS = ("product_designer", "frontend_react", "backend_python")


def _count_by_source(vacancies) -> str:
    counts = Counter(v.source for v in vacancies)
    return ", ".join(f"{src}={cnt}" for src, cnt in sorted(counts.items())) or "—"


async def main() -> None:
    settings = Settings.from_env()
    if not settings.telegram_admin_id:
        raise SystemExit("TELEGRAM_ADMIN_ID не задан")

    bot = Bot(token=settings.telegram_bot_token)
    db = VacancyDatabase(settings.db_path)
    service = VacancyService(settings, db, bot)

    lines = ["🧪 <b>Проверка реального фетча</b>", ""]

    # Канал (продуктовый дизайн)
    channel_all = await service.collect_all()
    channel_fresh = service.filter_fresh(channel_all)
    channel_dedup = dedupe_by_title_company(channel_fresh)
    lines += [
        "<b>Канал @prdsvac</b>",
        f"Найдено: {len(channel_all)}, свежих: {len(channel_fresh)}, после дедупа: {len(channel_dedup)}",
        f"Источники (свежие): {_count_by_source(channel_fresh)}",
    ]
    for vacancy in channel_dedup[:3]:
        lines.append(f"• [{vacancy.source}] {vacancy.title} — {vacancy.company}")

    lines.append("")

    # Подписчики по ролям
    digest_role_id = "frontend_react"
    digest_vacancies = []
    digest_total = 0

    for role_id in ROLE_IDS:
        role = get_role(role_id)
        if not role:
            continue
        vacancies = await collect_for_role(settings, role)
        fresh = [v for v in vacancies if is_fresh(v, settings.max_vacancy_age_hours)]
        deduped = dedupe_by_title_company(fresh)
        lines += [
            f"<b>{role.button_label}</b>",
            f"Найдено: {len(vacancies)}, свежих: {len(fresh)}, после дедупа: {len(deduped)}",
            f"Источники (свежие): {_count_by_source(fresh)}",
        ]
        for vacancy in deduped[:2]:
            lines.append(f"• [{vacancy.source}] {vacancy.title} — {vacancy.company}")
        lines.append("")

        if role_id == digest_role_id:
            digest_vacancies = deduped
            digest_total = len(vacancies)

    summary = "\n".join(lines)
    await bot.send_message(
        settings.telegram_admin_id,
        summary,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=False,
    )

    role = get_role(digest_role_id)
    assert role is not None
    messages, included = format_subscriber_digest(
        format_digest_roles_label([digest_role_id]),
        digest_vacancies[:12],
        digest_total,
        settings.max_vacancy_age_hours,
    )
    if messages and included:
        messages[0] = (
            f"🧪 <b>Пример дайджеста подписчику</b> ({role.button_label})\n\n"
            + messages[0]
        )
        for message in messages:
            await bot.send_message(
                settings.telegram_admin_id,
                message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False,
            )
            await asyncio.sleep(0.3)
    else:
        await bot.send_message(
            settings.telegram_admin_id,
            f"⚠️ Для {role.button_label} свежих вакансий для дайджеста не нашлось.",
        )

    await bot.session.close()
    print("OK: сообщения отправлены админу", settings.telegram_admin_id)


if __name__ == "__main__":
    asyncio.run(main())
