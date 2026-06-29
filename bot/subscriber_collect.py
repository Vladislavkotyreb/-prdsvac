from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import aiohttp

from bot.config import HH_AREAS, Settings
from bot.models import Vacancy
from bot.parsers.getmatch import GetMatchParser
from bot.parsers.habr import HabrParser
from bot.parsers.geekjob import GeekJobParser
from bot.parsers.hh import HHParser
from bot.roles import Role

logger = logging.getLogger(__name__)

GETMATCH_API_URL = "https://getmatch.ru/api/offers"


async def collect_for_role(settings: Settings, role: Role) -> list[Vacancy]:
    results: dict[str, Vacancy] = {}

    for source, vacancies in [
        ("hh.ru", await _fetch_hh(settings, role)),
        ("habr.com", await _fetch_habr(role)),
        ("geekjob.ru", await _fetch_geekjob(role)),
    ]:
        logger.info("Подписчики [%s] %s: найдено %s", role.id, source, len(vacancies))
        for vacancy in vacancies:
            if role.matcher(vacancy.title):
                results[vacancy.uid] = vacancy

    if role.uses_getmatch:
        getmatch_vacancies = await _fetch_getmatch(role)
        logger.info("Подписчики [%s] getmatch.ru: найдено %s", role.id, len(getmatch_vacancies))
        for vacancy in getmatch_vacancies:
            if role.matcher(vacancy.title):
                results[vacancy.uid] = vacancy

    return list(results.values())


async def _fetch_getmatch(role: Role) -> list[Vacancy]:
    """GetMatch для подписчиков: без фильтра product designer из канального парсера."""
    parser = GetMatchParser()
    results: dict[str, Vacancy] = {}
    offset = 0
    limit = 50
    headers = {"Accept": "application/json", "User-Agent": "ProductDesignerVacancyBot/1.0"}

    async with aiohttp.ClientSession(headers=headers) as session:
        while offset < 500:
            params = {"specialization": "design", "offset": offset, "limit": limit}
            async with session.get(GETMATCH_API_URL, params=params) as resp:
                if resp.status != 200:
                    break
                data = await resp.json()

            offers = data.get("offers", [])
            if not offers:
                break

            for offer in offers:
                if offer.get("language") not in (None, "ru"):
                    continue
                vacancy = parser._parse_item(offer)
                if vacancy:
                    results[vacancy.uid] = vacancy

            total = data.get("meta", {}).get("total", 0)
            offset += limit
            if offset >= total:
                break

    return list(results.values())


async def _fetch_hh(settings: Settings, role: Role) -> list[Vacancy]:
    parser = HHParser(settings)
    results: dict[str, Vacancy] = {}
    headers = parser._headers()
    date_to_dt = datetime.now(timezone.utc)
    date_from_dt = date_to_dt - timedelta(hours=settings.max_vacancy_age_hours)
    date_from = date_from_dt.isoformat(timespec="seconds")
    date_to = date_to_dt.isoformat(timespec="seconds")

    async with aiohttp.ClientSession(headers=headers) as session:
        for area in HH_AREAS:
            for query in role.hh_queries:
                page = 0
                while page < 3:
                    params = {
                        "text": query,
                        "area": area,
                        "per_page": 100,
                        "page": page,
                        "order_by": "publication_time",
                        "search_field": "name",
                        "date_from": date_from,
                        "date_to": date_to,
                    }
                    async with session.get(HHParser.API_URL, params=params) as resp:
                        if resp.status == 403:
                            logger.warning(
                                "HH.ru API 403 для подписчиков [%s] (auth=%s)",
                                role.id,
                                "yes" if settings.hh_access_token else "no",
                            )
                            return list(results.values())
                        if resp.status != 200:
                            break
                        data = await resp.json()

                    items = data.get("items", [])
                    if not items:
                        break

                    for item in items:
                        vacancy = parser._parse_item(item)
                        if vacancy:
                            results[vacancy.uid] = vacancy

                    page += 1
                    if page >= data.get("pages", 0):
                        break

    return list(results.values())


async def _fetch_habr(role: Role) -> list[Vacancy]:
    base = HabrParser()
    results: dict[str, Vacancy] = {}
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        for query in role.habr_queries:
            for page in range(1, 3):
                params = {"q": query, "page": page}
                async with session.get(
                    f"https://career.habr.com/vacancies", params=params
                ) as resp:
                    if resp.status != 200:
                        break
                    html = await resp.text()

                page_results = base._parse_html(html)
                if not page_results:
                    break
                for vacancy in page_results:
                    results[vacancy.uid] = vacancy

    return list(results.values())


async def _fetch_geekjob(role: Role) -> list[Vacancy]:
    base = GeekJobParser()
    results: dict[str, Vacancy] = {}
    headers = {"User-Agent": "ProductDesignerVacancyBot/1.0"}

    async with aiohttp.ClientSession(headers=headers) as session:
        for query in role.geekjob_queries:
            page = 1
            while page <= 3:
                params = {"search": query, "page": page}
                async with session.get(
                    "https://geekjob.ru/json/find/vacancy", params=params
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()

                items = data.get("data", [])
                if not items:
                    break

                for item in items:
                    vacancy = base._parse_item(item)
                    if vacancy:
                        results[vacancy.uid] = vacancy

                next_page = data.get("nextpage")
                if not next_page or next_page <= page:
                    break
                page = int(next_page)

    return list(results.values())
