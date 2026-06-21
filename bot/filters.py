from __future__ import annotations

import re

# Явные совпадения с продуктовым дизайном
INCLUDE_PATTERNS = [
    re.compile(r"продуктов(?:ый|ого|ая|ое)\s*(?:ui/?ux\s*)?дизайн", re.I),
    re.compile(r"product[\s-]*(?:ui/?ux\s*)?design(?:er)?", re.I),
    re.compile(r"product[\s-]*дизайн(?:ер)?", re.I),
    re.compile(r"ux/ui\s*designer", re.I),
    re.compile(r"ui/ux\s*designer", re.I),
    re.compile(r"product[\s-]*design[\s-]*lead", re.I),
    re.compile(r"lead\s*product\s*design", re.I),
    re.compile(r"senior\s*product\s*design", re.I),
    re.compile(r"middle\s*product\s*design", re.I),
    re.compile(r"junior\s*product\s*design", re.I),
    re.compile(r"продуктовый\s*ux", re.I),
    re.compile(r"product\s*owner.*design", re.I),
]

# Исключаем смежные, но не продуктовые роли
EXCLUDE_PATTERNS = [
    re.compile(r"графическ", re.I),
    re.compile(r"graphic\s*design", re.I),
    re.compile(r"motion", re.I),
    re.compile(r"гейм[\s-]*дизайн|game\s*design", re.I),
    re.compile(r"3d[\s-]*дизайн|3d\s*design", re.I),
    re.compile(r"интерьер|interior", re.I),
    re.compile(r"продуктов(?:ый|ого)\s*аналит", re.I),
    re.compile(r"product\s*analy", re.I),
    re.compile(r"product\s*manager", re.I),
    re.compile(r"продуктов(?:ый|ого)\s*менедж", re.I),
    re.compile(r"communication\s*design", re.I),
    re.compile(r"web[\s-]*designer(?!\s*\()", re.I),
    re.compile(r"веб[\s-]*дизайн", re.I),
    re.compile(r"тильда", re.I),
    re.compile(r"видеомонтаж", re.I),
    re.compile(r"художник", re.I),
]

# Для общих «дизайнер»-вакансий — нужен явный product/ui/ux контекст
GENERIC_DESIGNER = re.compile(r"дизайн|design", re.I)
PRODUCT_CONTEXT = re.compile(r"product|продукт|ux|ui", re.I)


def is_product_designer_vacancy(title: str) -> bool:
    text = " ".join(title.split())
    if not text:
        return False

    for pattern in EXCLUDE_PATTERNS:
        if pattern.search(text):
            return False

    for pattern in INCLUDE_PATTERNS:
        if pattern.search(text):
            return True

    if GENERIC_DESIGNER.search(text) and PRODUCT_CONTEXT.search(text):
        return True

    return False
