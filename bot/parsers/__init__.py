from __future__ import annotations

from abc import ABC, abstractmethod

from bot.models import Vacancy


class BaseParser(ABC):
    source: str

    @abstractmethod
    async def fetch(self) -> list[Vacancy]:
        raise NotImplementedError
