"""
models/league.py — Модель лиги (чемпионата).
Управляет таблицей результатов, обновлением турнирной таблицы
и определением чемпиона и зоны вылета.
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from core.constants import SEASON_MATCHDAYS


@dataclass
class LeagueStanding:
    """Строка в таблице лиги."""
    team_id: int
    team_name: str
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0
    points: int = 0

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    @property
    def form_string(self) -> str:
        """Строка формы (последние 5 результатов — упрощённо)."""
        # В реальной игре это хранилось бы отдельно
        return ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "team_id": self.team_id,
            "team_name": self.team_name,
            "played": self.played,
            "wins": self.wins,
            "draws": self.draws,
            "losses": self.losses,
            "goals_for": self.goals_for,
            "goals_against": self.goals_against,
            "goal_difference": self.goal_difference,
            "points": self.points,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LeagueStanding":
        return cls(
            team_id=data["team_id"],
            team_name=data["team_name"],
            played=data.get("played", 0),
            wins=data.get("wins", 0),
            draws=data.get("draws", 0),
            losses=data.get("losses", 0),
            goals_for=data.get("goals_for", 0),
            goals_against=data.get("goals_against", 0),
            points=data.get("points", 0),
        )


class League:
    """
    Класс, представляющий футбольную лигу.
    Управляет таблицей результатов и определением итогов сезона.
    """

    def __init__(
        self,
        league_id: int,
        name: str,
        country: str,
        tier: int = 1,
        team_ids: Optional[List[int]] = None,
        team_names: Optional[Dict[int, str]] = None,
        promotion_spots: int = 2,
        relegation_spots: int = 3,
        champion_spots: int = 1,
    ) -> None:
        self._id = league_id
        self._name = name
        self._country = country
        self._tier = tier
        self._promotion_spots = promotion_spots
        self._relegation_spots = relegation_spots
        self._champion_spots = champion_spots

        # Таблица: team_id -> LeagueStanding
        self._standings: Dict[int, LeagueStanding] = {}
        if team_ids and team_names:
            for tid in team_ids:
                self._standings[tid] = LeagueStanding(
                    team_id=tid,
                    team_name=team_names.get(tid, f"Team {tid}"),
                )

    # ── Свойства ────────────────────────────────────────────────────
    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def country(self) -> str:
        return self._country

    @property
    def tier(self) -> int:
        return self._tier

    @property
    def teams(self) -> List[int]:
        """Список ID команд в лиге."""
        return list(self._standings.keys())

    @property
    def team_count(self) -> int:
        return len(self._standings)

    # ── Работа с таблицей ───────────────────────────────────────────
    def add_team(self, team_id: int, team_name: str) -> None:
        """Добавление команды в таблицу."""
        if team_id not in self._standings:
            self._standings[team_id] = LeagueStanding(
                team_id=team_id,
                team_name=team_name,
            )

    def remove_team(self, team_id: int) -> None:
        """Удаление команды из таблицы."""
        self._standings.pop(team_id, None)

    def record_match(
        self,
        home_team_id: int,
        away_team_id: int,
        home_goals: int,
        away_goals: int,
    ) -> None:
        """
        Запись результата матча в таблицу.
        Обновляет статистику обеих команд.
        """
        home = self._standings.get(home_team_id)
        away = self._standings.get(away_team_id)

        if not home or not away:
            return

        home.played += 1
        away.played += 1

        home.goals_for += home_goals
        home.goals_against += away_goals
        away.goals_for += away_goals
        away.goals_against += home_goals

        if home_goals > away_goals:
            # Победа хозяев
            home.wins += 1
            home.points += 3
            away.losses += 1
        elif home_goals < away_goals:
            # Победа гостей
            away.wins += 1
            away.points += 3
            home.losses += 1
        else:
            # Ничья
            home.draws += 1
            away.draws += 1
            home.points += 1
            away.points += 1

    def update_table(self) -> List[LeagueStanding]:
        """
        Обновление и сортировка таблицы.
        Возвращает отсортированный список по очкам,
        затем разнице мячей, затем забитым мячам.
        """
        standings = list(self._standings.values())
        standings.sort(
            key=lambda s: (s.points, s.goal_difference, s.goals_for),
            reverse=True,
        )
        return standings

    def get_standings(self) -> List[Dict[str, Any]]:
        """Получение текущей таблицы в виде списка словарей."""
        sorted_standings = self.update_table()
        return [s.to_dict() for s in sorted_standings]

    def get_team_position(self, team_id: int) -> Optional[int]:
        """
        Позиция команды в таблице (1-based).
        Возвращает None, если команда не найдена.
        """
        sorted_standings = self.update_table()
        for i, standing in enumerate(sorted_standings, 1):
            if standing.team_id == team_id:
                return i
        return None

    def get_team_standing(self, team_id: int) -> Optional[LeagueStanding]:
        """Получение строки таблицы для команды."""
        return self._standings.get(team_id)

    def is_champion(self, team_id: int) -> bool:
        """Проверка: является ли команда чемпионом."""
        position = self.get_team_position(team_id)
        return position is not None and position <= self._champion_spots

    def get_champion(self) -> Optional[int]:
        """Получение ID чемпиона (первая команда в таблице)."""
        sorted_standings = self.update_table()
        if sorted_standings:
            return sorted_standings[0].team_id
        return None

    def get_promoted(self) -> List[int]:
        """Получение ID команд, выходящих в высший дивизион."""
        sorted_standings = self.update_table()
        return [s.team_id for s in sorted_standings[:self._promotion_spots]]

    def get_relegated(self) -> List[int]:
        """Получение ID команд, выбывающих в низший дивизион."""
        sorted_standings = self.update_table()
        total = len(sorted_standings)
        # Поседние N команд
        return [s.team_id for s in sorted_standings[total - self._relegation_spots:]]

    def get_qualification_spots(self) -> Dict[str, List[int]]:
        """
        Получение позиций квалификации в еврокубки.
        Возвращает словарь с типами кубков и ID команд.
        """
        sorted_standings = self.update_table()
        result: Dict[str, List[int]] = {
            "champions_league": [],
            "europa_league": [],
            "europa_conference": [],
        }

        # Лига чемпионов — топ-4
        for i, s in enumerate(sorted_standings[:4]):
            result["champions_league"].append(s.team_id)

        # Лига Европы — 5-е место
        if len(sorted_standings) > 4:
            result["europa_league"].append(sorted_standings[4].team_id)

        # Лига Конференции — 6-е место
        if len(sorted_standings) > 5:
            result["europa_conference"].append(sorted_standings[5].team_id)

        return result

    def reset_table(self) -> None:
        """Сброс таблицы для нового сезона."""
        for standing in self._standings.values():
            standing.played = 0
            standing.wins = 0
            standing.draws = 0
            standing.losses = 0
            standing.goals_for = 0
            standing.goals_against = 0
            standing.points = 0

    # ── Сериализация ────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация лиги в словарь."""
        return {
            "id": self._id,
            "name": self._name,
            "country": self._country,
            "tier": self._tier,
            "promotion_spots": self._promotion_spots,
            "relegation_spots": self._relegation_spots,
            "champion_spots": self._champion_spots,
            "standings": {str(k): v.to_dict() for k, v in self._standings.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "League":
        """Десериализация лиги из словаря."""
        league = cls(
            league_id=data["id"],
            name=data["name"],
            country=data["country"],
            tier=data.get("tier", 1),
            promotion_spots=data.get("promotion_spots", 2),
            relegation_spots=data.get("relegation_spots", 3),
            champion_spots=data.get("champion_spots", 1),
        )
        for tid_str, standing_data in data.get("standings", {}).items():
            league._standings[int(tid_str)] = LeagueStanding.from_dict(standing_data)
        return league

    def __repr__(self) -> str:
        return (
            f"League(id={self._id}, name='{self._name}', "
            f"teams={self.team_count})"
        )
