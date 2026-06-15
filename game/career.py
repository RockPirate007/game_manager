"""
game/career.py — Управление карьерой менеджера.
Отслеживает клубы, трофеи, достижения и репутацию.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime


class CareerManager:
    """
    Менеджер карьеры.
    Хранит историю работы менеджера, достижения и статистику.
    """

    def __init__(self) -> None:
        self._manager_name: str = ""
        self._nationality: str = ""
        self._start_year: int = 2024
        self._current_club_id: Optional[int] = None
        self._clubs_managed: List[Dict[str, Any]] = []
        self._trophies: List[Dict[str, Any]] = []
        self._matches_managed: int = 0
        self._wins: int = 0
        self._draws: int = 0
        self._losses: int = 0
        self._reputation: int = 30  # Начальная репутация
        self._achievements: List[Dict[str, Any]] = []
        self._career_history: List[Dict[str, Any]] = []

    # ── Свойства ────────────────────────────────────────────────────
    @property
    def manager_name(self) -> str:
        return self._manager_name

    @property
    def reputation(self) -> int:
        return self._reputation

    @property
    def matches_managed(self) -> int:
        return self._matches_managed

    @property
    def win_rate(self) -> float:
        """Процент побед."""
        if self._matches_managed == 0:
            return 0.0
        return (self._wins / self._matches_managed) * 100

    @property
    def trophies_count(self) -> int:
        return len(self._trophies)

    @property
    def years_active(self) -> int:
        """Количество лет в профессии."""
        return datetime.now().year - self._start_year

    # ── Начало карьеры ──────────────────────────────────────────────
    def start_career(
        self,
        manager_name: str,
        nationality: str = "Россия",
        start_year: int = 2024,
    ) -> Dict[str, Any]:
        """
        Начало новой карьеры менеджера.
        Возвращает начальные данные карьеры.
        """
        self._manager_name = manager_name
        self._nationality = nationality
        self._start_year = start_year
        self._reputation = 30

        self._career_history.append({
            "event": "career_start",
            "year": start_year,
            "manager": manager_name,
            "message": f"{manager_name} начинает карьеру менеджера",
        })

        return self.get_career_stats()

    def join_club(
        self,
        club_id: int,
        club_name: str,
        year: int,
        position: str = "Главный тренер",
    ) -> None:
        """
        Принятие должности в клубе.
        """
        if self._current_club_id is not None:
            self.leave_club(year, "Перешёл в другой клуб")

        self._current_club_id = club_id
        self._clubs_managed.append({
            "club_id": club_id,
            "club_name": club_name,
            "start_year": year,
            "end_year": None,
            "position": position,
        })

        self._career_history.append({
            "event": "join_club",
            "year": year,
            "club": club_name,
            "message": f"{self._manager_name} назначен в {club_name}",
        })

    def leave_club(self, year: int, reason: str = "") -> None:
        """
        Увольнение из клуба.
        """
        if not self._clubs_managed:
            return

        last = self._clubs_managed[-1]
        last["end_year"] = year
        last["reason"] = reason

        self._career_history.append({
            "event": "leave_club",
            "year": year,
            "club": last["club_name"],
            "reason": reason,
            "message": f"{self._manager_name} покинул {last['club_name']}: {reason}",
        })

        self._current_club_id = None

    # ── Статистика матчей ───────────────────────────────────────────
    def record_match_result(self, win: bool = False, draw: bool = False,
                           loss: bool = False) -> None:
        """Запись результата матча."""
        self._matches_managed += 1
        if win:
            self._wins += 1
            self._reputation = min(100, self._reputation + 1)
        elif draw:
            self._draws += 1
            self._reputation = min(100, self._reputation + 0.5)
        elif loss:
            self._losses += 1
            self._reputation = max(0, self._reputation - 0.5)

    # ── Трофеи и достижения ─────────────────────────────────────────
    def add_trophy(self, name: str, club_name: str, year: int) -> None:
        """Добавление трофея."""
        self._trophies.append({
            "name": name,
            "club": club_name,
            "year": year,
        })
        self._reputation = min(100, self._reputation + 5)
        self._check_achievements()

    def add_achievement(self, name: str, description: str, year: int) -> None:
        """Добавление достижения."""
        achievement = {
            "name": name,
            "description": description,
            "year": year,
        }
        if achievement not in self._achievements:
            self._achievements.append(achievement)

    def _check_achievements(self) -> None:
        """Проверка и выдача достижений."""
        # Первый трофей
        if len(self._trophies) == 1:
            self.add_achievement(
                "Первый трофей",
                "Выиграл первый трофей в карьере",
                datetime.now().year,
            )

        # Серия побед
        if self._wins >= 10:
            self.add_achievement(
                "Десять побед",
                "Одержал 10 побед в качестве менеджера",
                datetime.now().year,
            )

        # Высокая репутация
        if self._reputation >= 80:
            self.add_achievement(
                "Элита",
                "Достиг репутации 80+",
                datetime.now().year,
            )

        # Много матчей
        if self._matches_managed >= 100:
            self.add_achievement(
                "Опытный тренер",
                "Провёл 100+ матчей",
                datetime.now().year,
            )

    # ── Получение данных ────────────────────────────────────────────
    def get_career_stats(self) -> Dict[str, Any]:
        """Получение полной статистики карьеры."""
        return {
            "manager_name": self._manager_name,
            "nationality": self._nationality,
            "start_year": self._start_year,
            "current_club_id": self._current_club_id,
            "years_active": self.years_active,
            "matches_managed": self._matches_managed,
            "wins": self._wins,
            "draws": self._draws,
            "losses": self._losses,
            "win_rate": round(self.win_rate, 1),
            "trophies_count": self.trophies_count,
            "reputation": round(self._reputation, 1),
            "clubs_managed": len(self._clubs_managed),
        }

    def get_achievements(self) -> List[Dict[str, Any]]:
        """Получение списка достижений."""
        return list(self._achievements)

    def get_trophies(self) -> List[Dict[str, Any]]:
        """Получение списка трофеев."""
        return list(self._trophies)

    def get_clubs_history(self) -> List[Dict[str, Any]]:
        """Получение истории клубов."""
        return list(self._clubs_managed)

    def get_career_timeline(self) -> List[Dict[str, Any]]:
        """Получение таймлайна карьеры."""
        return list(self._career_history)

    # ── Сериализация ────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация карьеры в словарь."""
        return {
            "manager_name": self._manager_name,
            "nationality": self._nationality,
            "start_year": self._start_year,
            "current_club_id": self._current_club_id,
            "clubs_managed": self._clubs_managed,
            "trophies": self._trophies,
            "matches_managed": self._matches_managed,
            "wins": self._wins,
            "draws": self._draws,
            "losses": self._losses,
            "reputation": self._reputation,
            "achievements": self._achievements,
            "career_history": self._career_history,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CareerManager":
        """Десериализация карьеры из словаря."""
        cm = cls()
        cm._manager_name = data.get("manager_name", "")
        cm._nationality = data.get("nationality", "")
        cm._start_year = data.get("start_year", 2024)
        cm._current_club_id = data.get("current_club_id")
        cm._clubs_managed = data.get("clubs_managed", [])
        cm._trophies = data.get("trophies", [])
        cm._matches_managed = data.get("matches_managed", 0)
        cm._wins = data.get("wins", 0)
        cm._draws = data.get("draws", 0)
        cm._losses = data.get("losses", 0)
        cm._reputation = data.get("reputation", 30)
        cm._achievements = data.get("achievements", [])
        cm._career_history = data.get("career_history", [])
        return cm

    def __repr__(self) -> str:
        return (
            f"CareerManager(name='{self._manager_name}', "
            f"reputation={self._reputation:.0f}, "
            f"trophies={self.trophies_count})"
        )
