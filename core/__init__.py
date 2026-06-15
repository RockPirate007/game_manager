"""
core/__init__.py — Пакет ядра игры.
Экспортирует основные компоненты: шину событий, состояние игры, константы.
"""

from core.event_bus import EventBus, EventType, Event
from core.constants import (
    Position,
    PlayStyle,
    Difficulty,
    SeasonPhase,
    CompetitionType,
    FORMATIONS,
    MAX_SQUAD_SIZE,
    STARTING_XI_SIZE,
    MAX_SUBSTITUTES,
    SEASON_MATCHDAYS,
)

__all__ = [
    "EventBus",
    "EventType",
    "Event",
    "Position",
    "PlayStyle",
    "Difficulty",
    "SeasonPhase",
    "CompetitionType",
    "FORMATIONS",
    "MAX_SQUAD_SIZE",
    "STARTING_XI_SIZE",
    "MAX_SUBSTITUTES",
    "SEASON_MATCHDAYS",
]
