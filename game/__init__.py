"""
game/__init__.py — Пакет игровой логики.
Экспортирует основные классы: карьера, сезон, календарь, новости, медиа, награды.
"""

from game.career import CareerManager
from game.season import Season
from game.calendar import Calendar
from game.news import NewsGenerator
from game.media import PressConference
from game.awards import AwardsManager

__all__ = [
    "CareerManager",
    "Season",
    "Calendar",
    "NewsGenerator",
    "PressConference",
    "AwardsManager",
]
