"""
game/awards.py — Управление наградами и номинациями.
Голосование за лучшего игрока, тренера, гол месяца и т.д.
"""

import random
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class AwardNominee:
    """Номинант на награду."""
    player_id: int
    player_name: str
    team: str
    stats: Dict[str, Any] = field(default_factory=dict)
    votes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_id": self.player_id,
            "player_name": self.player_name,
            "team": self.team,
            "stats": self.stats,
            "votes": self.votes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AwardNominee":
        return cls(
            player_id=data["player_id"],
            player_name=data["player_name"],
            team=data["team"],
            stats=data.get("stats", {}),
            votes=data.get("votes", 0),
        )


# Типы наград
AWARD_TYPES = {
    "player_of_the_month": {
        "name": "Игрок месяца",
        "description": "Лучший игрок месяца по версии экспертов",
        "max_nominees": 5,
    },
    "goal_of_the_month": {
        "name": "Гол месяца",
        "description": "Красивейший гол месяца",
        "max_nominees": 5,
    },
    "manager_of_the_month": {
        "name": "Тренер месяца",
        "description": "Лучший тренер месяца",
        "max_nominees": 3,
    },
    "young_player": {
        "name": "Молодой игрок",
        "description": "Лучший игрок до 21 года",
        "max_nominees": 5,
    },
    "season_best_player": {
        "name": "Лучший игрок сезона",
        "description": "Лучший игрок по итогам сезона",
        "max_nominees": 10,
    },
    "season_best_goal": {
        "name": "Лучший гол сезона",
        "description": "Красивейший гол сезона",
        "max_nominees": 10,
    },
    "golden_boot": {
        "name": "Золотая бутса",
        "description": "Лучший бомбардир сезона",
        "max_nominees": 10,
    },
}


class AwardsManager:
    """
    Менеджер наград.
    Управляет номинациями, голосованием и определением победителей.
    """

    def __init__(self) -> None:
        self._active_awards: Dict[str, List[AwardNominee]] = {}
        self._completed_awards: List[Dict[str, Any]] = []
        self._voting_active = False
        self._current_award_type: Optional[str] = None

    # ── Номинация ───────────────────────────────────────────────────
    def nominate_player(
        self,
        award_type: str,
        player_id: int,
        player_name: str,
        team: str,
        stats: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Добавление игрока в номинацию.
        Возвращает True, если номинация успешна.
        """
        if award_type not in AWARD_TYPES:
            return False

        award_config = AWARD_TYPES[award_type]
        max_nominees = award_config["max_nominees"]

        if award_type not in self._active_awards:
            self._active_awards[award_type] = []

        nominees = self._active_awards[award_type]

        # Проверяем, не превышен ли лимит
        if len(nominees) >= max_nominees:
            return False

        # Проверяем, не номинирован ли уже
        for n in nominees:
            if n.player_id == player_id:
                return False

        nominee = AwardNominee(
            player_id=player_id,
            player_name=player_name,
            team=team,
            stats=stats or {},
        )
        nominees.append(nominee)
        return True

    def start_voting(self, award_type: str) -> bool:
        """Начало голосования за награду."""
        if award_type not in self._active_awards:
            return False
        if len(self._active_awards[award_type]) < 2:
            return False  # Нужно минимум 2 номинанта

        self._voting_active = True
        self._current_award_type = award_type
        return True

    def vote(
        self,
        voter_name: str,
        award_type: str,
        player_id: int,
        weight: float = 1.0,
    ) -> bool:
        """
        Голос за номинанта.
        :param voter_name: имя голосующего
        :param award_type: тип награды
        :param player_id: ID номинанта
        :param weight: вес голоса (1.0 — обычный, больше для экспертов)
        """
        if not self._voting_active or self._current_award_type != award_type:
            return False

        nominees = self._active_awards.get(award_type, [])
        for nominee in nominees:
            if nominee.player_id == player_id:
                nominee.votes += int(weight * 10)
                return True

        return False

    def cast_bulk_votes(
        self,
        award_type: str,
        votes: Dict[int, int],
    ) -> int:
        """
        Массовое голосование.
        :param award_type: тип награды
        :param votes: словарь {player_id: количество_голосов}
        :return: количество засчитанных голосов
        """
        if award_type not in self._active_awards:
            return 0

        nominees = self._active_awards[award_type]
        counted = 0

        for nominee in nominees:
            if nominee.player_id in votes:
                nominee.votes += votes[nominee.player_id]
                counted += votes[nominee.player_id]

        return counted

    # ── Получение результатов ───────────────────────────────────────
    def get_nominees(self, award_type: str) -> List[Dict[str, Any]]:
        """Получение списка номинантов."""
        nominees = self._active_awards.get(award_type, [])
        # Сортируем по голосам
        sorted_nominees = sorted(nominees, key=lambda n: n.votes, reverse=True)
        return [n.to_dict() for n in sorted_nominees]

    def get_winner(self, award_type: str) -> Optional[Dict[str, Any]]:
        """
        Получение победителя награды.
        Завершает голосование и переносит результат в историю.
        """
        nominees = self._active_awards.get(award_type, [])
        if not nominees:
            return None

        # Находим победителя
        winner = max(nominees, key=lambda n: n.votes)

        award_config = AWARD_TYPES.get(award_type, {})

        result = {
            "award_type": award_type,
            "award_name": award_config.get("name", award_type),
            "winner": winner.to_dict(),
            "all_nominees": [n.to_dict() for n in sorted(
                nominees, key=lambda n: n.votes, reverse=True
            )],
        }

        self._completed_awards.append(result)

        # Очищаем активную награду
        self._active_awards.pop(award_type, None)
        self._voting_active = False
        self._current_award_type = None

        return result

    def get_all_winners(self) -> List[Dict[str, Any]]:
        """Получение всех победителей."""
        return list(self._completed_awards)

    def get_award_info(self, award_type: str) -> Dict[str, Any]:
        """Получение информации о типе награды."""
        return AWARD_TYPES.get(award_type, {})

    def get_available_awards(self) -> List[str]:
        """Получение доступных типов наград."""
        return list(AWARD_TYPES.keys())

    # ── Автоматическая номинация ────────────────────────────────────
    auto_nominate_player_of_month = True

    def auto_nominate(
        self,
        award_type: str,
        players: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Автоматическая номинация игроков на основе статистики.
        Возвращает список имён номинантов.
        """
        if award_type not in AWARD_TYPES:
            return []

        award_config = AWARD_TYPES[award_type]
        max_nominees = award_config["max_nominees"]

        # Сортируем игроков по релевантной статистике
        if award_type in ("player_of_the_month", "season_best_player"):
            sorted_players = sorted(
                players, key=lambda p: p.get("rating", 0) + p.get("goals", 0) * 2,
                reverse=True,
            )
        elif award_type in ("golden_boot", "goal_of_the_month"):
            sorted_players = sorted(
                players, key=lambda p: p.get("goals", 0),
                reverse=True,
            )
        else:
            sorted_players = sorted(
                players, key=lambda p: p.get("rating", 0),
                reverse=True,
            )

        nominated_names = []
        for p in sorted_players[:max_nominees]:
            success = self.nominate_player(
                award_type=award_type,
                player_id=p.get("id", 0),
                player_name=p.get("name", "Неизвестный"),
                team=p.get("team", "Неизвестный клуб"),
                stats=p,
            )
            if success:
                nominated_names.append(p.get("name", ""))

        return nominated_names

    # ── Сериализация ────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация в словарь."""
        return {
            "active_awards": {
                k: [n.to_dict() for n in v]
                for k, v in self._active_awards.items()
            },
            "completed_awards": self._completed_awards,
            "voting_active": self._voting_active,
            "current_award_type": self._current_award_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AwardsManager":
        """Десериализация из словаря."""
        am = cls()
        am._voting_active = data.get("voting_active", False)
        am._current_award_type = data.get("current_award_type")
        am._completed_awards = data.get("completed_awards", [])
        for k, nominees_data in data.get("active_awards", {}).items():
            am._active_awards[k] = [AwardNominee.from_dict(n) for n in nominees_data]
        return am

    def __repr__(self) -> str:
        return (
            f"AwardsManager(active={len(self._active_awards)}, "
            f"completed={len(self._completed_awards)})"
        )
