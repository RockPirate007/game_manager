"""
models/match.py — Модель матча.
Содержит логику симуляции, хранение событий и результатов.
"""

import random
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field

from core.constants import HOME_ADVANTAGE, DRAW_BIAS


@dataclass
class MatchEvent:
    """Событие матча (гол, карточка, замена и т.д.)."""
    minute: int
    event_type: str  # "goal", "yellow_card", "red_card", "substitution", "injury"
    team_id: int
    player_id: int
    player_name: str
    details: Optional[str] = None  # Доп. информация (например, assists)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "minute": self.minute,
            "event_type": self.event_type,
            "team_id": self.team_id,
            "player_id": self.player_id,
            "player_name": self.player_name,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MatchEvent":
        return cls(
            minute=data["minute"],
            event_type=data["event_type"],
            team_id=data["team_id"],
            player_id=data["player_id"],
            player_name=data["player_name"],
            details=data.get("details"),
        )


class Match:
    """
    Класс, представляющий футбольный матч.
    Поддерживает симуляцию, хранение событий и результатов.
    """

    def __init__(
        self,
        match_id: int,
        home_team_id: int,
        away_team_id: int,
        home_team_name: str = "",
        away_team_name: str = "",
        date: Optional[str] = None,
        competition: str = "",
        is_neutral: bool = False,
    ) -> None:
        self._id = match_id
        self._home_team_id = home_team_id
        self._away_team_id = away_team_id
        self._home_team_name = home_team_name
        self._away_team_name = away_team_name
        self._date = date or datetime.now().strftime("%Y-%m-%d")
        self._competition = competition
        self._is_neutral = is_neutral

        # Результат
        self._home_goals: int = 0
        self._away_goals: int = 0
        self._played: bool = False

        # События матча
        self._events: List[MatchEvent] = []

        # Статистика
        self._home_possession: int = 50
        self._away_possession: int = 50
        self._home_shots: int = 0
        self._away_shots: int = 0
        self._home_shots_on_target: int = 0
        self._away_shots_on_target: int = 0

    # ── Свойства ────────────────────────────────────────────────────
    @property
    def id(self) -> int:
        return self._id

    @property
    def home_team_id(self) -> int:
        return self._home_team_id

    @property
    def away_team_id(self) -> int:
        return self._away_team_id

    @property
    def home_team_name(self) -> str:
        return self._home_team_name

    @property
    def away_team_name(self) -> str:
        return self._away_team_name

    @property
    def date(self) -> str:
        return self._date

    @property
    def competition(self) -> str:
        return self._competition

    @property
    def played(self) -> bool:
        return self._played

    @property
    def events(self) -> List[MatchEvent]:
        return list(self._events)

    @property
    def home_goals(self) -> int:
        return self._home_goals

    @property
    def away_goals(self) -> int:
        return self._away_goals

    # ── Симуляция матча ─────────────────────────────────────────────
    def simulate(
        self,
        home_strength: float = 70.0,
        away_strength: float = 65.0,
        home_morale: float = 75.0,
        away_morale: float = 70.0,
        home_form: float = 60.0,
        away_form: float = 55.0,
        home_players: Optional[List[Dict[str, Any]]] = None,
        away_players: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Симуляция матча.
        Рассчитывает результат на основе силы команд,
        формы, морали и случайных факторов.

        Возвращает словарь с результатом и событиями.
        """
        if self._played:
            return {"error": "Матч уже сыгран"}

        # Расчёт силы каждой команды
        home_power = self._calculate_team_power(
            home_strength, home_morale, home_form, is_home=True
        )
        away_power = self._calculate_team_power(
            away_strength, away_morale, away_form, is_home=False
        )

        total_power = home_power + away_power

        # Вероятность голов для каждой команды
        home_goal_prob = (home_power / total_power) * 1.8
        away_goal_prob = (away_power / total_power) * 1.6

        # Симуляция голов (распределение Пуассона)
        self._home_goals = self._poisson_goals(home_goal_prob)
        self._away_goals = self._poisson_goals(away_goal_prob)

        # Генерация событий
        self._generate_match_events(home_players, away_players)

        # Статистика владения мячом
        possession_ratio = home_power / total_power
        self._home_possession = int(possession_ratio * 100)
        self._away_possession = 100 - self._home_possession

        # Удары
        self._home_shots = random.randint(5, 18)
        self._away_shots = random.randint(3, 14)
        self._home_shots_on_target = random.randint(
            max(1, self._home_shots // 4), self._home_shots
        )
        self._away_shots_on_target = random.randint(
            max(1, self._away_shots // 4), self._away_shots
        )

        self._played = True

        return self.get_summary()

    def _calculate_team_power(
        self, strength: float, morale: float,
        form: float, is_home: bool
    ) -> float:
        """Расчёт итоговой силы команды с учётом всех факторов."""
        from core.constants import (
            HOME_ADVANTAGE, FORM_WEIGHT,
            MORALE_WEIGHT, FATIGUE_PENALTY,
        )

        power = strength
        power += (morale - 50) * MORALE_WEIGHT * 0.5
        power += (form - 50) * FORM_WEIGHT * 0.5
        if is_home:
            power *= HOME_ADVANTAGE
        return max(10.0, power)

    def _poisson_goals(self, expected: float) -> int:
        """Генерация количества голов по распределению Пуассона."""
        import math
        L = math.exp(-expected)
        k = 0
        p = 1.0
        while p > L:
            k += 1
            p *= random.random()
        return k - 1

    def _generate_match_events(
        self,
        home_players: Optional[List[Dict[str, Any]]] = None,
        away_players: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Генерация событий матча (голы, карточки, замены)."""
        self._events = []

        # Голы хозяев
        for _ in range(self._home_goals):
            minute = random.randint(1, 90)
            scorer = self._pick_random_player(home_players, ["ST", "LW", "RW", "AM"])
            if scorer:
                assist = self._pick_random_player(home_players, ["CM", "AM", "LW", "RW"], exclude_id=scorer.get("id"))
                self._events.append(MatchEvent(
                    minute=minute,
                    event_type="goal",
                    team_id=self._home_team_id,
                    player_id=scorer.get("id", 0),
                    player_name=scorer.get("name", "Игрок"),
                    details=f"Ассист: {assist.get('name', 'Н/Д')}" if assist else None,
                ))

        # Голы гостей
        for _ in range(self._away_goals):
            minute = random.randint(1, 90)
            scorer = self._pick_random_player(away_players, ["ST", "LW", "RW", "AM"])
            if scorer:
                assist = self._pick_random_player(away_players, ["CM", "AM", "LW", "RW"], exclude_id=scorer.get("id"))
                self._events.append(MatchEvent(
                    minute=minute,
                    event_type="goal",
                    team_id=self._away_team_id,
                    player_id=scorer.get("id", 0),
                    player_name=scorer.get("name", "Игрок"),
                    details=f"Ассист: {assist.get('name', 'Н/Д')}" if assist else None,
                ))

        # Жёлтые карточки (0-5 за матч)
        for _ in range(random.randint(0, 5)):
            minute = random.randint(1, 90)
            team = random.choice([self._home_team_id, self._away_team_id])
            players = home_players if team == self._home_team_id else away_players
            player = self._pick_random_player(players)
            if player:
                self._events.append(MatchEvent(
                    minute=minute,
                    event_type="yellow_card",
                    team_id=team,
                    player_id=player.get("id", 0),
                    player_name=player.get("name", "Игрок"),
                ))

        # Красные карточки (редко)
        if random.random() < 0.05:
            minute = random.randint(1, 90)
            team = random.choice([self._home_team_id, self._away_team_id])
            players = home_players if team == self._home_team_id else away_players
            player = self._pick_random_player(players)
            if player:
                self._events.append(MatchEvent(
                    minute=minute,
                    event_type="red_card",
                    team_id=team,
                    player_id=player.get("id", 0),
                    player_name=player.get("name", "Игрок"),
                ))

        # Сортируем события по минуте
        self._events.sort(key=lambda e: e.minute)

    def _pick_random_player(
        self,
        players: Optional[List[Dict[str, Any]]],
        preferred_positions: Optional[List[str]] = None,
        exclude_id: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """Выбор случайного игрока с предпочтением по позиции."""
        if not players:
            return None

        available = [p for p in players if p.get("id") != exclude_id]

        if preferred_positions:
            preferred = [
                p for p in available
                if p.get("position") in preferred_positions
            ]
            if preferred:
                return random.choice(preferred)

        return random.choice(available) if available else None

    # ── Получение результатов ───────────────────────────────────────
    def get_score(self) -> Tuple[int, int]:
        """Получение счёта матча."""
        return (self._home_goals, self._away_goals)

    def get_result(self) -> str:
        """Результат в текстовой форме (например, '2:1')."""
        return f"{self._home_goals}:{self._away_goals}"

    def get_winner(self) -> Optional[int]:
        """
        ID победителя.
        Возвращает None в случае ничьей.
        """
        if not self._played:
            return None
        if self._home_goals > self._away_goals:
            return self._home_team_id
        elif self._away_goals > self._home_goals:
            return self._away_team_id
        return None

    def get_summary(self) -> Dict[str, Any]:
        """Получение полного отчёта о матче."""
        return {
            "id": self._id,
            "home_team_id": self._home_team_id,
            "away_team_id": self._away_team_id,
            "home_team_name": self._home_team_name,
            "away_team_name": self._away_team_name,
            "date": self._date,
            "competition": self._competition,
            "played": self._played,
            "home_goals": self._home_goals,
            "away_goals": self._away_goals,
            "result": self.get_result(),
            "winner": self.get_winner(),
            "possession": {
                "home": self._home_possession,
                "away": self._away_possession,
            },
            "shots": {
                "home": self._home_shots,
                "away": self._away_shots,
            },
            "shots_on_target": {
                "home": self._home_shots_on_target,
                "away": self._away_shots_on_target,
            },
            "events": [e.to_dict() for e in self._events],
        }

    # ── Сериализация ────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация матча в словарь."""
        return {
            "id": self._id,
            "home_team_id": self._home_team_id,
            "away_team_id": self._away_team_id,
            "home_team_name": self._home_team_name,
            "away_team_name": self._away_team_name,
            "date": self._date,
            "competition": self._competition,
            "is_neutral": self._is_neutral,
            "home_goals": self._home_goals,
            "away_goals": self._away_goals,
            "played": self._played,
            "home_possession": self._home_possession,
            "away_possession": self._away_possession,
            "home_shots": self._home_shots,
            "away_shots": self._away_shots,
            "home_shots_on_target": self._home_shots_on_target,
            "away_shots_on_target": self._away_shots_on_target,
            "events": [e.to_dict() for e in self._events],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Match":
        """Десериализация матча из словаря."""
        match = cls(
            match_id=data["id"],
            home_team_id=data["home_team_id"],
            away_team_id=data["away_team_id"],
            home_team_name=data.get("home_team_name", ""),
            away_team_name=data.get("away_team_name", ""),
            date=data.get("date"),
            competition=data.get("competition", ""),
            is_neutral=data.get("is_neutral", False),
        )
        match._home_goals = data.get("home_goals", 0)
        match._away_goals = data.get("away_goals", 0)
        match._played = data.get("played", False)
        match._home_possession = data.get("home_possession", 50)
        match._away_possession = data.get("away_possession", 50)
        match._home_shots = data.get("home_shots", 0)
        match._away_shots = data.get("away_shots", 0)
        match._home_shots_on_target = data.get("home_shots_on_target", 0)
        match._away_shots_on_target = data.get("away_shots_on_target", 0)
        match._events = [MatchEvent.from_dict(e) for e in data.get("events", [])]
        return match

    def __repr__(self) -> str:
        status = "✓" if self._played else "○"
        return (
            f"Match(id={self._id}, {self._home_team_name} vs {self._away_team_name}, "
            f"{self.get_result()}, {status})"
        )
