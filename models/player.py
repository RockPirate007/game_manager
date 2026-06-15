"""
models/player.py — Модель игрока.
Обёртка над данными игрока с методами сериализации,
обновления характеристик и проверки состояния.
"""

import random
from typing import Any, Dict, Optional
from datetime import datetime

from core.constants import (
    Position,
    MAX_RATING,
    POTENTIAL_CAP,
    MAX_MORALE,
    MAX_FORM,
    MAX_FATIGUE,
)


class Player:
    """
    Класс, представляющий футболиста.
    Хранит все характеристики и предоставляет методы
    для их изменения и сериализации.
    """

    def __init__(
        self,
        player_id: int,
        name: str,
        age: int,
        nationality: str,
        position: Position,
        rating: int,
        potential: int,
        morale: int = 75,
        form: int = 70,
        fatigue: int = 0,
        injury_weeks: int = 0,
        goals: int = 0,
        assists: int = 0,
        appearances: int = 0,
        yellow_cards: int = 0,
        red_cards: int = 0,
        wage: int = 0,
        contract_years: int = 3,
        team_id: Optional[int] = None,
    ) -> None:
        self._id = player_id
        self._name = name
        self._age = age
        self._nationality = nationality
        self._position = position
        self._rating = min(rating, MAX_RATING)
        self._potential = min(potential, POTENTIAL_CAP)
        self._morale = min(max(morale, 0), MAX_MORALE)
        self._form = min(max(form, 0), MAX_FORM)
        self._fatigue = min(max(fatigue, 0), MAX_FATIGUE)
        self._injury_weeks = max(injury_weeks, 0)
        self._goals = goals
        self._assists = assists
        self._appearances = appearances
        self._yellow_cards = yellow_cards
        self._red_cards = red_cards
        self._wage = wage
        self._contract_years = contract_years
        self._team_id = team_id
        self._created_at = datetime.now()

    # ── Свойства (read-only для внешнего кода) ─────────────────────
    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def age(self) -> int:
        return self._age

    @property
    def nationality(self) -> str:
        return self._nationality

    @property
    def position(self) -> Position:
        return self._position

    @property
    def rating(self) -> int:
        return self._rating

    @property
    def potential(self) -> int:
        return self._potential

    @property
    def morale(self) -> int:
        return self._morale

    @property
    def form(self) -> int:
        return self._form

    @property
    def fatigue(self) -> int:
        return self._fatigue

    @property
    def injury_weeks(self) -> int:
        return self._injury_weeks

    @property
    def goals(self) -> int:
        return self._goals

    @property
    def assists(self) -> int:
        return self._assists

    @property
    def appearances(self) -> int:
        return self._appearances

    @property
    def yellow_cards(self) -> int:
        return self._yellow_cards

    @property
    def red_cards(self) -> int:
        return self._red_cards

    @property
    def wage(self) -> int:
        return self._wage

    @property
    def contract_years(self) -> int:
        return self._contract_years

    @property
    def team_id(self) -> Optional[int]:
        return self._team_id

    @team_id.setter
    def team_id(self, value: Optional[int]) -> None:
        self._team_id = value

    # ── Вычисляемые характеристики ──────────────────────────────────
    @property
    def effective_rating(self) -> int:
        """Рейтинг с учётом формы и усталости."""
        base = self._rating
        form_mod = (self._form - 50) * 0.2
        fatigue_mod = -self._fatigue * 0.15
        injury_mod = -30 if self._injury_weeks > 0 else 0
        return max(1, min(MAX_RATING, int(base + form_mod + fatigue_mod + injury_mod)))

    @property
    def overall_potential_gap(self) -> int:
        """Разница между текущим рейтингом и потенциалом."""
        return self._potential - self._rating

    @property
    def market_value(self) -> int:
        """Примерная рыночная стоимость игрока."""
        base_value = self._rating ** 2 * 1000
        age_factor = max(0.5, 1.0 - (self._age - 25) * 0.03) if self._age > 25 else 1.0
        potential_factor = 1.0 + (self._potential - self._rating) * 0.02
        return int(base_value * age_factor * potential_factor)

    # ── Методы состояния ────────────────────────────────────────────
    def is_injured(self) -> bool:
        """Проверка: травмирован ли игрок."""
        return self._injury_weeks > 0

    def is_available(self) -> bool:
        """Проверка: доступен ли игрок для матча."""
        return self._injury_weeks == 0 and self._red_cards < 2

    def is_suspended(self) -> bool:
        """Проверка: дисквалифицирован ли игрок (3 жёлтых карточки)."""
        return self._yellow_cards >= 3

    def get_status(self) -> str:
        """Получение текстового статуса игрока."""
        if self._injury_weeks > 0:
            return f"Травмирован ({self._injury_weeks} нед.)"
        if self._red_cards >= 2:
            return "Дисквалифицирован"
        if self._yellow_cards >= 3:
            return "Дисквалифицирован (жёлтые)"
        if self._fatigue > 80:
            return "Сильно уставший"
        if self._fatigue > 50:
            return "Уставший"
        if self._form < 30:
            return "Плохая форма"
        return "Здоров"

    def get_position_group(self) -> str:
        """Группа позиций: защита, полузащита, нападение, вратарь."""
        if self._position.is_goalkeeper:
            return "Вратарь"
        if self._position.is_defender:
            return "Защита"
        if self._position.is_midfielder:
            return "Полузащита"
        if self._position.is_attacker:
            return "Нападение"
        return "Неизвестно"

    # ── Обновление характеристик ────────────────────────────────────
    def update_stats(
        self,
        goals: int = 0,
        assists: int = 0,
        rating_change: int = 0,
        morale_change: int = 0,
        form_change: int = 0,
        fatigue_change: int = 0,
        yellow_card: bool = False,
        red_card: bool = False,
    ) -> None:
        """
        Обновление статистики игрока после матча или события.
        Все изменения суммируются с текущими значениями.
        """
        self._goals += goals
        self._assists += assists
        self._appearances += 1

        self._rating = min(MAX_RATING, max(1, self._rating + rating_change))
        self._morale = min(MAX_MORALE, max(0, self._morale + morale_change))
        self._form = min(MAX_FORM, max(0, self._form + form_change))
        self._fatigue = min(MAX_FATIGUE, max(0, self._fatigue + fatigue_change))

        if yellow_card:
            self._yellow_cards += 1
        if red_card:
            self._red_cards += 1

    def heal(self, weeks: int = 1) -> None:
        """Лечение травмы (уменьшение оставшихся недель)."""
        self._injury_weeks = max(0, self._injury_weeks - weeks)

    def injure(self, weeks: int) -> None:
        """Получение травмы."""
        self._injury_weeks = max(1, weeks)

    def rest(self, fatigue_reduction: int = 20) -> None:
        """Отдых — снижение усталости."""
        self._fatigue = max(0, self._fatigue - fatigue_reduction)

    def train(self, skill_gain: int = 1) -> None:
        """
        Тренировка — небольшой рост рейтинга при условии,
        что есть потенциал для роста.
        """
        if self._rating < self._potential:
            gain = min(skill_gain, self._potential - self._rating)
            self._rating = min(MAX_RATING, self._rating + gain)

    def age_one_year(self) -> None:
        """Старение игрока на один год."""
        self._age += 1
        # Старшие игроки теряют потенциал быстрее
        if self._age > 30:
            self._potential = max(self._rating, self._potential - 1)

    # ── Сериализация ────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация игрока в словарь."""
        return {
            "id": self._id,
            "name": self._name,
            "age": self._age,
            "nationality": self._nationality,
            "position": self._position.value,
            "rating": self._rating,
            "potential": self._potential,
            "morale": self._morale,
            "form": self._form,
            "fatigue": self._fatigue,
            "injury_weeks": self._injury_weeks,
            "goals": self._goals,
            "assists": self._assists,
            "appearances": self._appearances,
            "yellow_cards": self._yellow_cards,
            "red_cards": self._red_cards,
            "wage": self._wage,
            "contract_years": self._contract_years,
            "team_id": self._team_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        """Десериализация игрока из словаря."""
        return cls(
            player_id=data["id"],
            name=data["name"],
            age=data["age"],
            nationality=data["nationality"],
            position=Position(data["position"]),
            rating=data["rating"],
            potential=data["potential"],
            morale=data.get("morale", 75),
            form=data.get("form", 70),
            fatigue=data.get("fatigue", 0),
            injury_weeks=data.get("injury_weeks", 0),
            goals=data.get("goals", 0),
            assists=data.get("assists", 0),
            appearances=data.get("appearances", 0),
            yellow_cards=data.get("yellow_cards", 0),
            red_cards=data.get("red_cards", 0),
            wage=data.get("wage", 0),
            contract_years=data.get("contract_years", 3),
            team_id=data.get("team_id"),
        )

    def __repr__(self) -> str:
        return (
            f"Player(id={self._id}, name='{self._name}', "
            f"pos={self._position.value}, rating={self._rating})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
