"""Цветовые константы и темы для UI."""

from typing import Any, Dict, Optional

# Цвета для рейтингов игроков
RATING_COLORS = {
    "legendary": "bold bright_green",  # 90+
    "world_class": "bold green",       # 85-89
    "excellent": "green",              # 80-84
    "good": "bright_cyan",            # 75-79
    "average": "yellow",              # 70-74
    "below_average": "dark_orange",   # 65-69
    "poor": "red",                    # 60-64
    "terrible": "bold red",           # Below 60
}

# Цвета для результатов матчей (форма команды)
FORM_COLORS = {
    "W": "bold green",    # Победа
    "D": "yellow",        # Ничья
    "L": "bold red",      # Поражение
    "w": "green",         # Победа (мини)
    "d": "dark_yellow",   # Ничья (мини)
    "l": "red",           # Поражение (мини)
}

# Цвета позиций игроков
POSITION_COLORS = {
    "GK": "bold yellow",       # Вратарь
    "CB": "bold blue",         # Центральный защитник
    "LB": "cyan",              # Левый защитник
    "RB": "cyan",              # Правый защитник
    "LWB": "bright_blue",      # Левый вингербек
    "RWB": "bright_blue",      # Правый вингербек
    "CDM": "bright_cyan",      # Опорный полузащитник
    "CM": "cyan",              # Центральный полузащитник
    "CAM": "bright_magenta",   # Атакующий полузащитник
    "LM": "magenta",           # Левый полузащитник
    "RM": "magenta",           # Правый полузащитник
    "LW": "bright_red",        # Левый вингер
    "RW": "bright_red",        # Правый вингер
    "CF": "bold red",          # Центральный нападающий
    "ST": "bold bright_red",   # Нападающий
    "SS": "bright_magenta",    # Второй нападающий
}

# Цвета клубов (основные цвета для таблиц)
TEAM_COLORS: Dict[str, str] = {
    # Англия - Премьер-лига
    "Арсенал": "bold red",
    "Астон Вилла": "bold dark_orange",
    "Борнмут": "bold red",
    "Брентфорд": "bold red",
    "Брайтон": "bright_blue",
    "Бернли": "bold dark_orange",
    "Челси": "bold blue",
    "Кристал Пэлас": "bright_blue",
    "Эвертон": "bright_blue",
    "Фулхэм": "white",
    "Ипсвич": "bright_blue",
    "Лестер": "bright_blue",
    "Ливерпуль": "bold red",
    "Манчестер Сити": "bright_cyan",
    "Манчестер Юнайтед": "bold red",
    "Ньюкасл": "white",
    "Ноттингем Форест": "bold red",
    "Саутгемптон": "bold red",
    "Тоттенхэм": "white",
    "Вулверхэмптон": "bold dark_orange",
    "Вест Хэм": "bold dark_orange",
    # Россия - Премьер-лига
    "Зенит": "bright_blue",
    "Спартак": "bold red",
    "ЦСКА": "bold red",
    "Локомотив": "bold green",
    "Динамо": "bright_blue",
    "Краснодар": "bold green",
    "Ростов": "yellow",
    "Крылья Советов": "bright_cyan",
    "Ахмат": "bold green",
    "Урал": "dark_orange",
    "Факел": "bold red",
    "Оренбург": "bright_green",
    "Балтика": "bright_cyan",
    "Рубин": "bold red",
    "Пари НН": "bright_blue",
    "Сочи": "white",
}

# Стандартные цвета темы
DEFAULT_THEME = {
    "background": "on grey11",
    "foreground": "white",
    "primary": "bright_cyan",
    "secondary": "bright_magenta",
    "success": "bold green",
    "warning": "yellow",
    "error": "bold red",
    "info": "bright_blue",
    "muted": "dim",
    "accent": "bright_yellow",
    "header": "bold bright_cyan on grey15",
    "panel_border": "cyan",
    "table_header": "bold cyan",
    "table_row_odd": "white",
    "table_row_even": "bright_white",
}


def get_color(rating: int) -> str:
    """
    Получить цвет по рейтингу игрока.

    Args:
        rating: Рейтинг (1-99)

    Returns:
        Стиль Rich для цвета
    """
    if rating >= 90:
        return RATING_COLORS["legendary"]
    elif rating >= 85:
        return RATING_COLORS["world_class"]
    elif rating >= 80:
        return RATING_COLORS["excellent"]
    elif rating >= 75:
        return RATING_COLORS["good"]
    elif rating >= 70:
        return RATING_COLORS["average"]
    elif rating >= 65:
        return RATING_COLORS["below_average"]
    elif rating >= 60:
        return RATING_COLORS["poor"]
    else:
        return RATING_COLORS["terrible"]


def get_team_color(team_name: str) -> str:
    """
    Получить цвет команды.

    Args:
        team_name: Название команды

    Returns:
        Стиль Rich для цвета команды
    """
    return TEAM_COLORS.get(team_name, "white")


def get_position_color(position: str) -> str:
    """
    Получить цвет позиции.

    Args:
        position: Код позиции (GK, CB, etc.)

    Returns:
        Стиль Rich для цвета позиции
    """
    return POSITION_COLORS.get(position.upper(), "white")


def get_form_color(result: str) -> str:
    """
    Получить цвет результата матча.

    Args:
        result: Результат (W, D, L)

    Returns:
        Стиль Rich для цвета результата
    """
    return FORM_COLORS.get(result.upper(), "white")


def theme_apply(
    text: str, theme_key: str, theme: Optional[Dict[str, str]] = None
) -> str:
    """
    Применить цвет из темы к тексту.

    Args:
        text: Текст для окрашивания
        theme_key: Ключ темы (primary, secondary, etc.)
        theme: Словарь темы (по умолчанию DEFAULT_THEME)

    Returns:
        Строка с применённым стилем Rich
    """
    if theme is None:
        theme = DEFAULT_THEME

    color = theme.get(theme_key, "white")
    return f"[{color}]{text}[/]"


def get_category_color(category: str) -> str:
    """
    Получить цвет по категории новости/события.

    Args:
        category: Категория

    Returns:
        Стиль Rich
    """
    colors = {
        "transfer": "cyan",
        "match": "green",
        "injury": "red",
        "award": "yellow",
        "general": "white",
        "press_conf": "magenta",
        "training": "bright_green",
        "finance": "bright_yellow",
        "youth": "bright_blue",
        "scouting": "bright_cyan",
        "staff": "bright_magenta",
        "stadium": "dark_orange",
        "fan": "bright_white",
        "league": "bold cyan",
        "cup": "bold yellow",
        "international": "bold bright_blue",
    }
    return colors.get(category.lower(), "white")
