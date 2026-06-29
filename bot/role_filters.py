from __future__ import annotations

import re

FRONTEND_INCLUDE = [
    re.compile(r"front[\s-]*end", re.I),
    re.compile(r"фронт[\s-]*енд", re.I),
    re.compile(r"react(?:\.?\s*js)?\s*(?:developer|разработ)", re.I),
    re.compile(r"vue(?:\.?\s*js)?\s*(?:developer|разработ)", re.I),
    re.compile(r"angular\s*(?:developer|разработ)", re.I),
    re.compile(r"(?:javascript|typescript)\s*(?:developer|разработ)", re.I),
]

FRONTEND_EXCLUDE = [
    re.compile(r"back[\s-]*end|бэкенд", re.I),
    re.compile(r"full[\s-]*stack|фулстак|fullstack", re.I),
    re.compile(r"\bqa\b|quality assurance|тестиров", re.I),
    re.compile(r"devops|sre|site reliability", re.I),
    re.compile(r"product\s*manager|продуктов(?:ый|ого)\s*менедж", re.I),
    re.compile(r"дизайн|designer|design\b", re.I),
    re.compile(r"\bandroid\b|\bios\b|mobile\s*dev", re.I),
    re.compile(r"data\s*(?:scientist|analyst)|аналитик\s*данных", re.I),
]

BACKEND_INCLUDE = [
    re.compile(r"back[\s-]*end", re.I),
    re.compile(r"бэкенд", re.I),
    re.compile(r"python\s*(?:developer|разработ|engineer)", re.I),
    re.compile(r"(?:go|golang)\s*(?:developer|разработ|engineer)", re.I),
    re.compile(r"java\s*(?:developer|разработ|engineer)", re.I),
    re.compile(r"node\.?\s*js\s*(?:developer|разработ|engineer)", re.I),
    re.compile(r"php\s*(?:developer|разработ|engineer)", re.I),
    re.compile(r"backend[\s-]*разработ", re.I),
]

BACKEND_EXCLUDE = [
    re.compile(r"front[\s-]*end|фронт[\s-]*енд", re.I),
    re.compile(r"full[\s-]*stack|фулстак|fullstack", re.I),
    re.compile(r"\bqa\b|quality assurance|тестиров", re.I),
    re.compile(r"devops|sre", re.I),
    re.compile(r"дизайн|designer|design\b", re.I),
    re.compile(r"product\s*manager|продуктов(?:ый|ого)\s*менедж", re.I),
]


def _matches(title: str, include: list[re.Pattern], exclude: list[re.Pattern]) -> bool:
    text = " ".join(title.split())
    if not text:
        return False
    for pattern in exclude:
        if pattern.search(text):
            return False
    for pattern in include:
        if pattern.search(text):
            return True
    return False


def is_frontend_vacancy(title: str) -> bool:
    return _matches(title, FRONTEND_INCLUDE, FRONTEND_EXCLUDE)


def is_backend_vacancy(title: str) -> bool:
    return _matches(title, BACKEND_INCLUDE, BACKEND_EXCLUDE)


GRAPHIC_INCLUDE = [
    re.compile(r"графическ(?:ий|ого|ая|ое)\s*дизайн", re.I),
    re.compile(r"graphic\s*design(?:er)?", re.I),
    re.compile(r"print\s*design", re.I),
    re.compile(r"полиграф", re.I),
    re.compile(r"visual\s*designer(?!\s*/?\s*product)", re.I),
]

GRAPHIC_EXCLUDE = [
    re.compile(r"product[\s-]*design|продуктов(?:ый|ого)\s*дизайн", re.I),
    re.compile(r"ux/ui|ui/ux|product\s*ux", re.I),
    re.compile(r"communication\s*design|коммуникацион", re.I),
    re.compile(r"front[\s-]*end|back[\s-]*end|бэкенд|фронтенд", re.I),
    re.compile(r"motion|game\s*design|гейм", re.I),
    re.compile(r"интерьер|interior|3d\s*design", re.I),
    re.compile(r"web[\s-]*design|веб[\s-]*дизайн", re.I),
]

COMMUNICATION_INCLUDE = [
    re.compile(r"коммуникацион(?:ный|ного|ная|ное)\s*дизайн", re.I),
    re.compile(r"communication\s*design(?:er)?", re.I),
    re.compile(r"visual\s*communication", re.I),
    re.compile(r"brand\s*communication", re.I),
    re.compile(r"бренд[\s-]*коммуникац", re.I),
]

COMMUNICATION_EXCLUDE = [
    re.compile(r"product[\s-]*design|продуктов(?:ый|ого)\s*дизайн", re.I),
    re.compile(r"ux/ui|ui/ux|product\s*ux", re.I),
    re.compile(r"front[\s-]*end|back[\s-]*end|бэкенд|фронтенд", re.I),
    re.compile(r"графическ(?:ий|ого)\s*дизайн", re.I),
    re.compile(r"graphic\s*design", re.I),
    re.compile(r"motion|game\s*design|гейм", re.I),
]


def is_graphic_designer_vacancy(title: str) -> bool:
    return _matches(title, GRAPHIC_INCLUDE, GRAPHIC_EXCLUDE)


def is_communication_designer_vacancy(title: str) -> bool:
    return _matches(title, COMMUNICATION_INCLUDE, COMMUNICATION_EXCLUDE)
