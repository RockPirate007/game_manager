"""UI пакет для интерфейса игры Football Manager."""

from .console import ConsoleUI
from .colors import (
    TEAM_COLORS,
    RATING_COLORS,
    FORM_COLORS,
    POSITION_COLORS,
    get_color,
    theme_apply,
)
from .widgets import (
    create_player_table,
    create_team_table,
    create_match_fixture,
    create_formation_display,
    create_stats_display,
    create_financial_display,
    create_news_card,
    create_bar,
)

__all__ = [
    "ConsoleUI",
    "TEAM_COLORS",
    "RATING_COLORS",
    "FORM_COLORS",
    "POSITION_COLORS",
    "get_color",
    "theme_apply",
    "create_player_table",
    "create_team_table",
    "create_match_fixture",
    "create_formation_display",
    "create_stats_display",
    "create_financial_display",
    "create_news_card",
    "create_bar",
]
