"""
models/team.py — Модель команды (клуба).
Содержит состав, бюджет, тактику и методы работы с игроками.
"""

from typing import Any, Dict, List, Optional, Tuple

from core.constants import (
    Position,
    PlayStyle,
    FORMATIONS,
    MAX_SQUAD_SIZE,
    STARTING_XI_SIZE,
)
from models.player import Player


class Team:
    """
    Класс, представляющий футбольный клуб.
    Управляет составом игроков, тактикой и финансами.
    """

    def __init__(
        self,
        team_id: int,
        name: str,
        reputation: int = 50,
        budget: int = 10_000_000,
        wage_budget: int = 500_000,
        players: Optional[List[Player]] = None,
        formation: str = "4-4-2",
        style: PlayStyle = PlayStyle.balanced,
        stadium: str = "",
        city: str = "",
        country: str = "",
        home_color: str = "#FF0000",
        away_color: str = "#FFFFFF",
    ) -> None:
        self._id = team_id
        self._name = name
        self._reputation = reputation
        self._budget = budget
        self._wage_budget = wage_budget
        self._players: List[Player] = players or []
        self._formation = formation if formation in FORMATIONS else "4-4-2"
        self._style = style
        self._stadium = stadium
        self._city = city
        self._country = country
        self._home_color = home_color
        self._away_color = away_color
        self._trophies: List[Dict[str, Any]] = []
        self._season_stats: Dict[str, Any] = {
            "wins": 0, "draws": 0, "losses": 0,
            "goals_for": 0, "goals_against": 0,
        }

    # ── Свойства ────────────────────────────────────────────────────
    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def reputation(self) -> int:
        return self._reputation

    @reputation.setter
    def reputation(self, value: int) -> None:
        self._reputation = max(1, min(100, value))

    @property
    def budget(self) -> int:
        return self._budget

    @property
    def wage_budget(self) -> int:
        return self._wage_budget

    @property
    def players(self) -> List[Player]:
        return list(self._players)

    @property
    def formation(self) -> str:
        return self._formation

    @formation.setter
    def formation(self, value: str) -> None:
        if value in FORMATIONS:
            self._formation = value

    @property
    def style(self) -> PlayStyle:
        return self._style

    @style.setter
    def style(self, value: PlayStyle) -> None:
        self._style = value

    @property
    def stadium(self) -> str:
        return self._stadium

    @property
    def city(self) -> str:
        return self._city

    @property
    def country(self) -> str:
        return self._country

    @property
    def season_stats(self) -> Dict[str, Any]:
        return dict(self._season_stats)

    @property
    def total_wage(self) -> int:
        """Суммарная зарплата всех игроков."""
        return sum(p.wage for p in self._players)

    @property
    def squad_size(self) -> int:
        return len(self._players)

    # ── Работа с составом ───────────────────────────────────────────
    def get_starting_xi(self) -> List[Player]:
        """
        Получение основного состава из 11 лучших игроков
        по рейтингу с учётом позиций.
        """
        if len(self._players) <= STARTING_XI_SIZE:
            return sorted(self._players, key=lambda p: p.effective_rating, reverse=True)

        # Сортируем игроков по рейтингу
        available = [p for p in self._players if p.is_available()]
        available.sort(key=lambda p: p.effective_rating, reverse=True)

        # Берём 11 лучших
        starting: List[Player] = []
        for player in available:
            if len(starting) >= STARTING_XI_SIZE:
                break
            starting.append(player)

        return starting

    def get_substitutes(self) -> List[Player]:
        """Получение запасных игроков (все доступные минус основа)."""
        starting = set(p.id for p in self.get_starting_xi())
        return [
            p for p in self._players
            if p.is_available() and p.id not in starting
        ]

    def get_players_by_position(self, position: Position) -> List[Player]:
        """Получение всех игроков на указанной позиции."""
        return [
            p for p in self._players
            if p.position == position and p.is_available()
        ]

    def get_best_for_position(self, position: Position) -> Optional[Player]:
        """Лучший игрок на позиции по рейтингу."""
        players = self.get_players_by_position(position)
        if not players:
            return None
        return max(players, key=lambda p: p.effective_rating)

    def get_avg_rating(self) -> float:
        """Средний рейтинг основного состава."""
        starting = self.get_starting_xi()
        if not starting:
            return 0.0
        return sum(p.effective_rating for p in starting) / len(starting)

    def get_avg_age(self) -> float:
        """Средний возраст состава."""
        if not self._players:
            return 0.0
        return sum(p.age for p in self._players) / len(self._players)

    def add_player(self, player: Player) -> bool:
        """
        Добавление игрока в состав.
        Возвращает False, если состав уже полный.
        """
        if self.squad_size >= MAX_SQUAD_SIZE:
            return False
        if player.id in [p.id for p in self._players]:
            return False  # Игрок уже в команде

        player.team_id = self._id
        self._players.append(player)
        return True

    def remove_player(self, player_id: int) -> Optional[Player]:
        """
        Удаление игрока из состава.
        Возвращает удалённого игрока или None.
        """
        for i, player in enumerate(self._players):
            if player.id == player_id:
                removed = self._players.pop(i)
                removed.team_id = None
                return removed
        return None

    def get_player(self, player_id: int) -> Optional[Player]:
        """Поиск игрока по ID."""
        for player in self._players:
            if player.id == player_id:
                return player
        return None

    def get_financial_summary(self) -> Dict[str, Any]:
        """Сводка по финансам клуба."""
        return {
            "budget": self._budget,
            "wage_budget": self._wage_budget,
            "total_wage": self.total_wage,
            "remaining_budget": self._budget - self.total_wage,
        }

    def update_season_record(
        self, win: bool = False, draw: bool = False,
        loss: bool = False, goals_for: int = 0, goals_against: int = 0
    ) -> None:
        """Обновление сезона."""
        if win:
            self._season_stats["wins"] += 1
        elif draw:
            self._season_stats["draws"] += 1
        elif loss:
            self._season_stats["losses"] += 1
        self._season_stats["goals_for"] += goals_for
        self._season_stats["goals_against"] += goals_against

    def add_trophy(self, name: str, year: int) -> None:
        """Добавление трофея."""
        self._trophies.append({"name": name, "year": year})

    # ── Сериализация ────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация команды в словарь."""
        return {
            "id": self._id,
            "name": self._name,
            "reputation": self._reputation,
            "budget": self._budget,
            "wage_budget": self._wage_budget,
            "players": [p.to_dict() for p in self._players],
            "formation": self._formation,
            "style": self._style.value,
            "stadium": self._stadium,
            "city": self._city,
            "country": self._country,
            "home_color": self._home_color,
            "away_color": self._away_color,
            "trophies": self._trophies,
            "season_stats": self._season_stats,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Team":
        """Десериализация команды из словаря."""
        players = [Player.from_dict(p) for p in data.get("players", [])]
        team = cls(
            team_id=data["id"],
            name=data["name"],
            reputation=data.get("reputation", 50),
            budget=data.get("budget", 10_000_000),
            wage_budget=data.get("wage_budget", 500_000),
            players=players,
            formation=data.get("formation", "4-4-2"),
            style=PlayStyle(data.get("style", "balanced")),
            stadium=data.get("stadium", ""),
            city=data.get("city", ""),
            country=data.get("country", ""),
            home_color=data.get("home_color", "#FF0000"),
            away_color=data.get("away_color", "#FFFFFF"),
        )
        team._trophies = data.get("trophies", [])
        team._season_stats = data.get("season_stats", {
            "wins": 0, "draws": 0, "losses": 0,
            "goals_for": 0, "goals_against": 0,
        })
        return team

    def __repr__(self) -> str:
        return (
            f"Team(id={self._id}, name='{self._name}', "
            f"players={self.squad_size}, rating={self.get_avg_rating():.1f})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Team):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
