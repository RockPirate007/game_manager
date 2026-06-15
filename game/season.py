"""
game/season.py — Управление сезоном.
Генерация расписания, продвижение туров и подведение итогов.
"""

import random
from typing import Any, Dict, List, Optional

from core.constants import SEASON_MATCHDAYS, SeasonPhase
from models.match import Match
from models.league import League


class Season:
    """
    Класс сезона.
    Управляет фазами, турами и расписанием матчей.
    """

    def __init__(self, year: int = 2024) -> None:
        self._year = year
        self._phase = SeasonPhase.PRE_SEASON
        self._matchday = 0
        self._total_matchdays = SEASON_MATCHDAYS
        self._fixtures: Dict[int, List[Match]] = {}
        self._results: List[Dict[str, Any]] = []
        self._awards: Dict[str, Any] = {}
        self._is_initialized = False

    # ── Свойства ────────────────────────────────────────────────────
    @property
    def year(self) -> int:
        return self._year

    @property
    def phase(self) -> SeasonPhase:
        return self._phase

    @property
    def matchday(self) -> int:
        return self._matchday

    @property
    def is_in_season(self) -> bool:
        """Проверка: идёт ли сезон (не межсезонье)."""
        return self._phase in (SeasonPhase.IN_SEASON, SeasonPhase.WINTER_BREAK)

    @property
    def is_finished(self) -> bool:
        return self._phase == SeasonPhase.OFF_SEASON

    @property
    def progress(self) -> float:
        """Прогресс сезона в процентах (0-100)."""
        if self._total_matchdays == 0:
            return 0.0
        return min(100.0, (self._matchday / self._total_matchdays) * 100)

    # ── Управление сезоном ──────────────────────────────────────────
    def start_season(self, team_ids: List[int]) -> None:
        """
        Начало нового сезона.
        Генерирует расписание и переходит в фазу IN_SEASON.
        """
        self._phase = SeasonPhase.PRE_SEASON
        self._matchday = 0
        self._fixtures = self.generate_fixtures(team_ids)
        self._results.clear()
        self._is_initialized = True
        self._phase = SeasonPhase.IN_SEASON

    def generate_fixtures(self, team_ids: List[int]) -> Dict[int, List[Match]]:
        """
        Генерация расписания по системе каждый с каждым.
        Возвращает словарь: номер тура -> список матчей.
        """
        fixtures: Dict[int, List[Match]] = {}
        n = len(team_ids)

        if n < 2:
            return fixtures

        # Круговой турнир: каждый с каждым дома
        matchday = 1
        for i in range(n):
            for j in range(i + 1, n):
                if matchday not in fixtures:
                    fixtures[matchday] = []

                match = Match(
                    match_id=matchday * 1000 + i * n + j,
                    home_team_id=team_ids[i],
                    away_team_id=team_ids[j],
                    competition="Лига",
                )
                fixtures[matchday].append(match)
                matchday += 1

        self._total_matchdays = len(fixtures)
        return fixtures

    def advance_matchday(self) -> Optional[Dict[str, Any]]:
        """
        Продвижение на следующий тур.
        Возвращает информацию о текущем туре или None, если сезон завершён.
        """
        if self._phase != SeasonPhase.IN_SEASON:
            return None

        self._matchday += 1

        # Зимняя пауза на середине сезона
        if self._matchday == self._total_matchdays // 2:
            self._phase = SeasonPhase.WINTER_BREAK
            return {
                "event": "winter_break",
                "matchday": self._matchday,
                "message": "Началась зимняя пауза",
            }

        # Конец сезона
        if self._matchday > self._total_matchdays:
            self._phase = SeasonPhase.OFF_SEASON
            return {
                "event": "season_end",
                "matchday": self._matchday,
                "message": "Сезон завершён",
            }

        return {
            "event": "matchday",
            "matchday": self._matchday,
            "fixtures": self.get_current_matchday(),
        }

    def resume_from_winter_break(self) -> None:
        """Возобновление после зимней паузы."""
        if self._phase == SeasonPhase.WINTER_BREAK:
            self._phase = SeasonPhase.IN_SEASON

    def get_current_matchday(self) -> List[Match]:
        """Получение матчей текущего тура."""
        return self._fixtures.get(self._matchday, [])

    def record_result(self, match: Match) -> None:
        """Запись результата матча."""
        self._results.append({
            "matchday": self._matchday,
            "match": match.get_summary(),
        })

    def end_season(self, league: Optional[League] = None) -> Dict[str, Any]:
        """
        Завершение сезона.
        Подведение итогов и определение чемпиона.
        """
        self._phase = SeasonPhase.OFF_SEASON

        result = {
            "year": self._year,
            "champion": None,
            "top_scorer": None,
            "total_goals": 0,
            "total_matches": len(self._results),
        }

        # Определяем чемпиона
        if league:
            champion_id = league.get_champion()
            if champion_id:
                result["champion"] = champion_id

        # Считаем голы
        for r in self._results:
            m = r.get("match", {})
            result["total_goals"] += m.get("home_goals", 0) + m.get("away_goals", 0)

        self._awards = result
        return result

    def get_standings_summary(self, league: Optional[League] = None) -> List[Dict[str, Any]]:
        """Краткая сводка таблицы."""
        if league:
            return league.get_standings()
        return []

    # ── Сериализация ────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация сезона в словарь."""
        return {
            "year": self._year,
            "phase": self._phase.value,
            "matchday": self._matchday,
            "total_matchdays": self._total_matchdays,
            "fixtures": {
                str(k): [m.to_dict() for m in v]
                for k, v in self._fixtures.items()
            },
            "results": self._results,
            "awards": self._awards,
            "is_initialized": self._is_initialized,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Season":
        """Десериализация сезона из словаря."""
        s = cls(year=data.get("year", 2024))
        s._phase = SeasonPhase(data.get("phase", "pre_season"))
        s._matchday = data.get("matchday", 0)
        s._total_matchdays = data.get("total_matchdays", SEASON_MATCHDAYS)
        s._results = data.get("results", [])
        s._awards = data.get("awards", {})
        s._is_initialized = data.get("is_initialized", False)
        for k_str, matches_data in data.get("fixtures", {}).items():
            s._fixtures[int(k_str)] = [Match.from_dict(m) for m in matches_data]
        return s

    def __repr__(self) -> str:
        return (
            f"Season(year={self._year}, phase={self._phase.value}, "
            f"matchday={self._matchday}/{self._total_matchdays})"
        )
