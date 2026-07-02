from __future__ import annotations

import logging
import re
from typing import Callable
from urllib.parse import quote, urljoin

import aiohttp
from bs4 import BeautifulSoup

from bot.config import BIGTECH_CAREER_SITES, BIGTECH_SEARCH_QUERIES, Settings
from bot.dates import utc_now
from bot.models import Vacancy
from bot.parsers.base import BaseParser

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


class BigTechCareersParser(BaseParser):
    """Парсит карьерные сайты российских IT-компаний (HTML)."""

    source = "careers"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def fetch(self) -> list[Vacancy]:
        from bot.filters import is_product_designer_vacancy

        return await self.fetch_matching(
            is_product_designer_vacancy,
            search_queries=tuple(BIGTECH_SEARCH_QUERIES),
        )

    async def fetch_matching(
        self,
        matcher: Callable[[str], bool],
        search_queries: tuple[str, ...] | None = None,
    ) -> list[Vacancy]:
        queries = search_queries or tuple(BIGTECH_SEARCH_QUERIES)
        results: dict[str, Vacancy] = {}
        headers = {"User-Agent": USER_AGENT}

        async with aiohttp.ClientSession(headers=headers) as session:
            for site in BIGTECH_CAREER_SITES:
                try:
                    vacancies = await self._fetch_site(session, site, matcher, queries)
                    for vacancy in vacancies:
                        results[vacancy.uid] = vacancy
                    if vacancies:
                        logger.info(
                            "careers [%s]: найдено %s",
                            site["company"],
                            len(vacancies),
                        )
                except Exception:
                    logger.exception("Ошибка парсера careers [%s]", site["company"])

        return list(results.values())

    @staticmethod
    def _search_urls(site: dict[str, str], queries: tuple[str, ...]) -> list[str]:
        if template := site.get("search_url_template"):
            return [template.format(query=quote(query)) for query in queries]
        if fixed := site.get("search_url"):
            return [fixed]
        return []

    async def _fetch_site(
        self,
        session: aiohttp.ClientSession,
        site: dict[str, str],
        matcher: Callable[[str], bool],
        queries: tuple[str, ...],
    ) -> list[Vacancy]:
        company = site["company"]
        base_url = site["base_url"]
        vacancy_pattern = re.compile(site["vacancy_path_re"])
        results: dict[str, Vacancy] = {}

        for search_url in self._search_urls(site, queries):
            async with session.get(
                search_url, timeout=aiohttp.ClientTimeout(total=20)
            ) as resp:
                if resp.status != 200:
                    logger.warning("careers [%s]: HTTP %s (%s)", company, resp.status, search_url)
                    continue
                html = await resp.text()

            soup = BeautifulSoup(html, "lxml")

            for link in soup.select("a[href]"):
                href = link.get("href", "")
                if not href:
                    continue
                full_url = urljoin(base_url, href)
                if not vacancy_pattern.search(full_url):
                    continue

                title = link.get_text(" ", strip=True)
                title = re.sub(r"\s+", " ", title)
                if not title or len(title) < 5:
                    continue
                if not matcher(title):
                    continue

                slug = re.sub(r"\W+", "-", full_url).strip("-")[-100:]
                external_id = f"{company}:{slug}"

                results[external_id] = Vacancy(
                    source=self.source,
                    external_id=external_id,
                    title=title,
                    company=company,
                    url=full_url,
                    published_at=utc_now(),
                )

        return list(results.values())
