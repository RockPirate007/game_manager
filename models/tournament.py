"""
models/tournament.py — Модель турнира (кубка).
Поддерживает сетку игр (брекет), этапы и продвижение по турниру.
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from models.match import Match


@dataclass
class TournamentRound:
    """Этап турнира (1/8 финала, четвертьфинал и т.д.)."""
    name: str
    round_number: int
    matches: List[Match] = field(default_factory=list)
    completed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "round_number": self.round_number,
            "matches": [m.to_dict() for m in self.matches],
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TournamentRound":
        r = cls(
            name=data["name"],
            round_number=data["round_number"],
            completed=data.get("completed", False),
        )
        r.matches = [Match.from_dict(m) for m in data.get("matches", [])]
        return r


# Названия этапов по количеству команд
ROUND_NAMES = {
    2: "Финал",
    4: "Полуфинал",
    8: "Четвертьфинал",
    16: "1/8 финала",
    32: "1/16 финала",
    64: "1/32 финала",
}


class Tournament:
    """
    Класс, представляющий кубковый турнир.
    Управляет сеткой, этапами и продвижением команд.
    """

    def __init__(
        self,
        tournament_id: int,
        name: str,
        team_ids: Optional[List[int]] = None,
        team_names: Optional[Dict[int, str]] = None,
        competition: str = "",
    ) -> None:
        self._id = tournament_id
        self._name = name
        self._competition = competition
        self._team_ids = team_ids or []
        self._team_names = team_names or {}
        self._rounds: List[TournamentRound] = []
        self._current_round_index = 0
        self._winner: Optional[int] = None
        self._year = 0

        # Если команды переданы, создаём сетку автоматически
        if self._team_ids:
            self._generate_bracket()

    # ── Свойства ────────────────────────────────────────────────────
    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def competition(self) -> str:
        return self._competition

    @property
    def current_round(self) -> Optional[TournamentRound]:
        """Текущий (активный) этап."""
        if 0 <= self._current_round_index < len(self._rounds):
            return self._rounds[self._current_round_index]
        return None

    @property
    def current_round_name(self) -> str:
        """Название текущего этапа."""
        r = self.current_round
        return r.name if r else "Турнир завершён"

    @property
    def is_finished(self) -> bool:
        """Проверка: завершён ли турнир."""
        return self._winner is not None

    @property
    def winner(self) -> Optional[int]:
        """ID победителя турнира."""
        return self._winner

    @property
    def rounds(self) -> List[TournamentRound]:
        return list(self._rounds)

    # ── Генерация сетки ─────────────────────────────────────────────
    def _generate_bracket(self) -> None:
        """
        Генерация турнирной сетки.
        Автоматически определяет количество этапов
        и создаёт пустые матчи.
        """
        self._rounds.clear()
        self._current_round_index = 0
        self._winner = None

        num_teams = len(self._team_ids)
        if num_teams < 2:
            return

        # Определяем ближайшую степень двойки
        bracket_size = 2
        while bracket_size < num_teams:
            bracket_size *= 2

        # Генерируем этапы от первого до финала
        teams_remaining = bracket_size
        round_number = 0

        while teams_remaining >= 2:
            round_name = ROUND_NAMES.get(teams_remaining, f"1/{teams_remaining} финала")
            round_matches_count = teams_remaining // 2

            round_obj = TournamentRound(
                name=round_name,
                round_number=round_number,
            )

            for match_idx in range(round_matches_count):
                match_id = self._id * 1000 + round_number * 100 + match_idx
                # Пока создаём матчи с placeholder-ами
                home_id = 0
                away_id = 0
                if round_number == 0 and match_idx * 2 + 1 < len(self._team_ids):
                    home_id = self._team_ids[match_idx * 2]
                    away_id = self._team_ids[match_idx * 2 + 1]

                match_obj = Match(
                    match_id=match_id,
                    home_team_id=home_id,
                    away_team_id=away_id,
                    home_team_name=self._team_names.get(home_id, "TBD"),
                    away_team_name=self._team_names.get(away_id, "TBD"),
                    competition=self._competition,
                )
                round_obj.matches.append(match_obj)

            self._rounds.append(round_obj)
            teams_remaining //= 2
            round_number += 1

    def _get_round_name_for_teams(self, num_teams: int) -> str:
        """Получение названия раунда по числу команд."""
        return ROUND_NAMES.get(num_teams, f"Раунд ({num_teams} ком.)")

    # ── Продвижение по турниру ──────────────────────────────────────
    def advance_round(self) -> Optional[TournamentRound]:
        """
        Завершение текущего раунда и переход к следующему.
        Победители проходят в следующий раунд.
        Возвращает новый текущий раунд или None, если турнир завершён.
        """
        if self.is_finished:
            return None

        current = self.current_round
        if not current:
            return None

        # Проверяем, что все матчи текущего раунда сыграны
        if not all(m.played for m in current.matches):
            return current

        current.completed = True

        # Собираем победителей
        winners: List[int] = []
        for match in current.matches:
            winner = match.get_winner()
            if winner is not None:
                winners.append(winner)

        # Если остался один победитель — турнир завершён
        if len(winners) == 1:
            self._winner = winners[0]
            return None

        # Создаём матчи следующего раунда
        self._current_round_index += 1

        if self._current_round_index >= len(self._rounds):
            # Создаём новый раунд
            round_name = self._get_round_name_for_teams(len(winners))
            new_round = TournamentRound(
                name=round_name,
                round_number=self._current_round_index,
            )
            self._rounds.append(new_round)
        else:
            new_round = self._rounds[self._current_round_index]

        # Заполняем матчи следующего раунда победителями
        new_round.matches.clear()
        for i in range(0, len(winners) - 1, 2):
            match_id = self._id * 1000 + self._current_round_index * 100 + i // 2
            home_id = winners[i]
            away_id = winners[i + 1] if i + 1 < len(winners) else 0

            match_obj = Match(
                match_id=match_id,
                home_team_id=home_id,
                away_team_id=away_id,
                home_team_name=self._team_names.get(home_id, "TBD"),
                away_team_name=self._team_names.get(away_id, "TBD"),
                competition=self._competition,
            )
            new_round.matches.append(match_obj)

        return new_round

    def get_bracket(self) -> Dict[str, Any]:
        """
        Получение полной турнирной сетки в виде словаря.
        Содержит все раунды и их матчи.
        """
        return {
            "tournament_id": self._id,
            "name": self._name,
            "current_round": self.current_round_name,
            "winner": self._winner,
            "is_finished": self.is_finished,
            "rounds": [r.to_dict() for r in self._rounds],
        }

    def get_remaining_teams(self) -> List[int]:
        """Получение команд, ещё не выбывших из турнира."""
        if self.is_finished:
            return [self._winner] if self._winner else []

        remaining = set()
        for r in self._rounds[:self._current_round_index]:
            for m in r.matches:
                if m.played:
                    winner = m.get_winner()
                    if winner:
                        remaining.add(winner)

        # Добавляем команды текущего раунда, которые ещё не играли
        current = self.current_round
        if current:
            for m in current.matches:
                if not m.played:
                    if m.home_team_id:
                        remaining.add(m.home_team_id)
                    if m.away_team_id:
                        remaining.add(m.away_team_id)

        return list(remaining)

    # ── Сериализация ────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация турнира в словарь."""
        return {
            "id": self._id,
            "name": self._name,
            "competition": self._competition,
            "team_ids": self._team_ids,
            "team_names": self._team_names,
            "current_round_index": self._current_round_index,
            "winner": self._winner,
            "year": self._year,
            "rounds": [r.to_dict() for r in self._rounds],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tournament":
        """Десериализация турнира из словаря."""
        t = cls(
            tournament_id=data["id"],
            name=data["name"],
            team_ids=data.get("team_ids", []),
            team_names=data.get("team_names", {}),
            competition=data.get("competition", ""),
        )
        t._current_round_index = data.get("current_round_index", 0)
        t._winner = data.get("winner")
        t._year = data.get("year", 0)
        t._rounds = [TournamentRound.from_dict(r) for r in data.get("rounds", [])]
        return t

    def __repr__(self) -> str:
        status = "Завершён" if self.is_finished else self.current_round_name
        return (
            f"Tournament(id={self._id}, name='{self._name}', "
            f"status='{status}', teams={len(self._team_ids)})"
        )
