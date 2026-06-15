"""
core/constants.py — Константы, перечисления и базовые типы игры.
Определяет позиции, формации, стили игры, уровни сложности,
фазы сезона и типы соревнований.
"""

from enum import Enum, auto
from typing import List


# ── Позиции игроков ────────────────────────────────────────────────
class Position(Enum):
    """Перечисление игровых позиций на поле."""
    GK = "GK"    # Вратарь
    LB = "LB"    # Левый защитник
    CB = "CB"    # Центральный защитник
    RB = "RB"    # Правый защитник
    DM = "DM"    # Опорный полузащитник
    CM = "CM"    # Центральный полузащитник
    AM = "AM"    # Атакующий полузащитник
    LW = "LW"    # Левый вингер
    RW = "RW"    # Правый вингер
    ST = "ST"    # Нападающий

    # Группы позиций для удобства
    @property
    def is_defender(self) -> bool:
        return self in (Position.LB, Position.CB, Position.RB, Position.DM)

    @property
    def is_midfielder(self) -> bool:
        return self in (Position.DM, Position.CM, Position.AM)

    @property
    def is_attacker(self) -> bool:
        return self in (Position.LW, Position.RW, Position.ST)

    @property
    def is_goalkeeper(self) -> bool:
        return self == Position.GK


# ── Типичные формации ──────────────────────────────────────────────
FORMATIONS: List[str] = [
    "4-3-3",
    "4-4-2",
    "4-2-3-1",
    "3-5-2",
    "5-3-2",
    "4-5-1",
    "3-4-3",
]


# ── Стили игры ─────────────────────────────────────────────────────
class PlayStyle(Enum):
    """Стиль игры команды."""
    possession = "possession"          # Игра с мячом
    counter_attack = "counter_attack"  # Контратака
    high_press = "high_press"          # Высокое давление
    direct = "direct"                  # Прямая игра
    balanced = "balanced"              # Сбалансированный
    defensive = "defensive"            # Оборонительный
    attacking = "attacking"            # Атакующий


# ── Уровни сложности ───────────────────────────────────────────────
class Difficulty(Enum):
    """Уровни сложности игры."""
    EASY = auto()    # Лёгкий
    NORMAL = auto()  # Нормальный
    HARD = auto()    # Сложный


# ── Фазы сезона ────────────────────────────────────────────────────
class SeasonPhase(Enum):
    """Фазы футбольного сезона."""
    PRE_SEASON = "pre_season"    # Предсезонье
    IN_SEASON = "in_season"      # Во время сезона
    WINTER_BREAK = "winter_break"  # Зимняя пауза
    OFF_SEASON = "off_season"    # Межсезонье


# ── Типы соревнований ──────────────────────────────────────────────
class CompetitionType(Enum):
    """Типы футбольных соревнований."""
    LEAGUE = "league"                    # Чемпионат
    CUP = "cup"                          # Кубок
    CHAMPIONS_LEAGUE = "champions_league"  # Лига чемпионов
    EUROPA_LEAGUE = "europa_league"      # Лига Европы


# ── Числовые константы ─────────────────────────────────────────────
MAX_SQUAD_SIZE = 30            # Максимальный размер состава
STARTING_XI_SIZE = 11          # Количество игроков в основном составе
MAX_SUBSTITUTES = 7            # Максимальное количество замен
SEASON_MATCHDAYS = 38          # Количество туров в сезоне (однокруговой)
WEEKS_PER_MONTH = 4            # Недель в месяце
MAX_INJURY_WEEKS = 24          # Максимальная длительность травмы в неделях
MAX_MORALE = 100               # Максимальное значение морали
MAX_FORM = 100                 # Максимальное значение формы
MAX_FATIGUE = 100              # Максимальная усталость
MAX_RATING = 100               # Максимальный рейтинг игрока
POTENTIAL_CAP = 99             # Потолок потенциала
REPUTATION_SCALE = 10          # Масштаб репутации (1-10)
BUDGET_SCALE = 1_000_000       # Масштаб бюджета (в единицах)

# ── Мультипликаторы для симуляции ──────────────────────────────────
HOME_ADVANTAGE = 1.1           # Преимущество домашней команды
DRAW_BIAS = 0.25               # Вероятность ничьей
FORM_WEIGHT = 0.3              # Вес формы в расчёте силы команды
MORALE_WEIGHT = 0.2            # Вес морали в расчёте силы команды
FATIGUE_PENALTY = 0.15         # Штраф за усталость
