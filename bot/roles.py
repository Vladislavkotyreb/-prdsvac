from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from bot.filters import is_product_designer_vacancy
from bot.role_filters import (
    is_backend_vacancy,
    is_communication_designer_vacancy,
    is_frontend_vacancy,
    is_graphic_designer_vacancy,
)


@dataclass(frozen=True)
class Role:
    id: str
    label: str
    button_label: str
    hh_queries: tuple[str, ...]
    habr_queries: tuple[str, ...]
    geekjob_queries: tuple[str, ...]
    uses_getmatch: bool
    matcher: Callable[[str], bool]


ROLES: dict[str, Role] = {
    "product_designer": Role(
        id="product_designer",
        label="продуктового дизайнера",
        button_label="UX/UI | Продуктовый дизайнер",
        hh_queries=(
            "продуктовый дизайнер",
            "product designer",
            "product design",
            "продуктовый ux",
            "product ux designer",
            "ux ui designer",
        ),
        habr_queries=("продуктовый дизайнер", "product designer", "ux ui designer"),
        geekjob_queries=("продуктовый дизайнер", "product designer", "ux designer"),
        uses_getmatch=True,
        matcher=is_product_designer_vacancy,
    ),
    "communication_designer": Role(
        id="communication_designer",
        label="коммуникационного дизайнера",
        button_label="Коммуникационный дизайнер",
        hh_queries=(
            "коммуникационный дизайнер",
            "communication designer",
            "communication design",
            "visual communication",
        ),
        habr_queries=("коммуникационный дизайнер", "communication designer", "communication design"),
        geekjob_queries=("коммуникационный дизайнер", "communication designer", "communication design"),
        uses_getmatch=True,
        matcher=is_communication_designer_vacancy,
    ),
    "graphic_designer": Role(
        id="graphic_designer",
        label="графического дизайнера",
        button_label="Графический дизайнер",
        hh_queries=(
            "графический дизайнер",
            "graphic designer",
            "graphic design",
            "visual designer",
        ),
        habr_queries=("графический дизайнер", "graphic designer", "graphic design"),
        geekjob_queries=("графический дизайнер", "graphic designer", "дизайнер"),
        uses_getmatch=True,
        matcher=is_graphic_designer_vacancy,
    ),
    "frontend": Role(
        id="frontend",
        label="frontend-разработчика",
        button_label="💻 Frontend",
        hh_queries=(
            "frontend developer",
            "frontend разработчик",
            "фронтенд разработчик",
            "react developer",
            "vue developer",
            "angular developer",
        ),
        habr_queries=("frontend", "react", "vue", "angular", "фронтенд"),
        geekjob_queries=("frontend", "react", "vue", "angular", "фронтенд"),
        uses_getmatch=False,
        matcher=is_frontend_vacancy,
    ),
    "backend": Role(
        id="backend",
        label="backend-разработчика",
        button_label="⚙️ Backend",
        hh_queries=(
            "backend developer",
            "backend разработчик",
            "бэкенд разработчик",
            "python developer",
            "go developer",
            "java developer",
        ),
        habr_queries=("backend", "python developer", "go developer", "java developer", "бэкенд"),
        geekjob_queries=("backend", "python", "golang", "java", "бэкенд"),
        uses_getmatch=False,
        matcher=is_backend_vacancy,
    ),
}

MVP_ROLE_IDS = (
    "product_designer",
    "communication_designer",
    "graphic_designer",
    "frontend",
    "backend",
)


def get_role(role_id: str) -> Optional[Role]:
    return ROLES.get(role_id)
