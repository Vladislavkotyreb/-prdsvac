from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    telegram_chat_id: int
    hh_user_agent: str
    hh_access_token: str
    timezone: str
    max_vacancy_age_hours: int
    db_path: Path
    telegram_admin_id: Optional[int]

    @classmethod
    def from_env(cls) -> "Settings":
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        if not token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN не задан. "
                "Локально: .env | GitHub: Settings → Secrets → Actions"
            )
        if not chat_id:
            raise ValueError(
                "TELEGRAM_CHAT_ID не задан. "
                "Локально: .env | GitHub: Settings → Secrets → Actions"
            )

        hh_user_agent = (
            os.getenv("HH_USER_AGENT")
            or "ProductDesignerVacancyBot/1.0 (kotvlad2016@gmail.com)"
        ).strip()

        admin_raw = os.getenv("TELEGRAM_ADMIN_ID", "").strip()

        return cls(
            telegram_bot_token=token,
            telegram_chat_id=int(chat_id),
            hh_user_agent=hh_user_agent,
            hh_access_token=os.getenv("HH_ACCESS_TOKEN", "").strip(),
            timezone=os.getenv("TIMEZONE", "Europe/Moscow").strip(),
            max_vacancy_age_hours=int(os.getenv("MAX_VACANCY_AGE_HOURS", "72")),
            db_path=BASE_DIR / "data" / "vacancies.db",
            telegram_admin_id=int(admin_raw) if admin_raw else None,
        )


# Регионы РФ и СНГ в HH.ru
HH_AREAS = [
    113,  # Россия
    16,   # Беларусь
    40,   # Казахстан
    5,    # Узбекистан
    48,   # Кыргызстан
    97,   # Армения
    9,    # Азербайджан
    62,   # Молдова
    28,   # Грузия
    100,  # Таджикистан
]

SEARCH_QUERIES = [
    "продуктовый дизайнер",
    "product designer",
    "product design",
    "продуктовый ux",
    "product ux designer",
    "ux ui designer",
    "UX UI дизайнер",
]

# HH employer_id для прямого поиска вакансий бигтеха на HeadHunter
BIGTECH_HH_EMPLOYERS: list[tuple[str, int]] = [
    ("Яндекс", 1740),
    ("Тинькофф", 78638),
    ("VK", 15478),
    ("Авито", 84585),
    ("Ozon", 2180),
    ("Сбер", 3529),
    ("Wildberries", 870697),
    ("2ГИС", 64174),
    ("Контур", 41862),
    ("МТС", 3776),
    ("Лаборатория Касперского", 1057),
]

BIGTECH_SEARCH_QUERIES = [
    "продуктовый дизайнер",
    "product designer",
    "ux ui designer",
    "дизайнер интерфейсов",
    "ux designer",
]

# Карьерные сайты (HTML). search_url_template — {query} URL-encoded.
BIGTECH_CAREER_SITES: list[dict[str, str]] = [
    {
        "company": "Сбер",
        "base_url": "https://rabota.sber.ru",
        "search_url_template": "https://rabota.sber.ru/search?query={query}",
        "vacancy_path_re": r"/search/\d+",
    },
]
