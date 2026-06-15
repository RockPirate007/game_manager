"""
game/calendar.py — Игровой календарь.
Управляет датами, определением дней матчей и планированием.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class Calendar:
    """
    Класс календаря игры.
    Отслеживает текущую дату и определяет дни матчей.
    """

    def __init__(self, start_date: Optional[str] = None) -> None:
        if start_date:
            self._current_date = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            self._current_date = datetime(2024, 7, 1)  # Начало предсезонья

        self._start_date = self._current_date
        self._matchdays: List[datetime] = []
        self._training_days: List[datetime] = []
        self._transfer_window_open = False
        self._season_start = datetime(2024, 8, 1)
        self._season_end = datetime(2025, 5, 31)

        # Генерируем календарь на сезон
        self._generate_matchday_schedule()

    def _generate_matchday_schedule(self) -> None:
        """Генерация расписания дней матчей (каждую неделю в сезоне)."""
        self._matchdays.clear()
        current = self._season_start
        while current <= self._season_end:
            # Матчи по субботам
            if current.weekday() == 5:  # Суббота
                self._matchdays.append(current)
            current += timedelta(days=1)

    # ── Свойства ────────────────────────────────────────────────────
    @property
    def current_date(self) -> datetime:
        return self._current_date

    @property
    def current_date_str(self) -> str:
        return self._current_date.strftime("%Y-%m-%d")

    @property
    def month(self) -> int:
        return self._current_date.month

    @property
    def year(self) -> int:
        return self._current_date.year

    @property
    def day_of_week(self) -> str:
        """День недели на русском."""
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        return days[self._current_date.weekday()]

    # ── Навигация по времени ────────────────────────────────────────
    def advance_day(self, days: int = 1) -> Dict[str, Any]:
        """
        Продвижение времени на указанное количество дней.
        Возвращает события, произошедшие за этот период.
        """
        self._current_date += timedelta(days=days)
        events = []

        # Проверяем окно трансферов
        if self.is_transfer_window():
            if not self._transfer_window_open:
                self._transfer_window_open = True
                events.append({
                    "type": "transfer_window_open",
                    "date": self.current_date_str,
                    "message": "Трансферное окно открыто",
                })
        else:
            if self._transfer_window_open:
                self._transfer_window_open = False
                events.append({
                    "type": "transfer_window_close",
                    "date": self.current_date_str,
                    "message": "Трансферное окно закрыто",
                })

        return {"date": self.current_date_str, "events": events}

    def advance_week(self) -> Dict[str, Any]:
        """Продвижение на одну неделю."""
        return self.advance_day(7)

    # ── Проверки ────────────────────────────────────────────────────
    def is_matchday(self) -> bool:
        """Проверка: является ли текущий день днём матча."""
        return self._current_date in self._matchdays

    def is_matchday_in_days(self, days: int) -> bool:
        """Проверка: будет ли матч через N дней."""
        target_date = self._current_date + timedelta(days=days)
        return target_date in self._matchdays

    def is_transfer_window(self) -> bool:
        """Проверка: открыто ли трансферное окно."""
        month = self._current_date.month
        # Летнее окно: июнь-август
        if 6 <= month <= 8:
            return True
        # Зимнее окно: январь
        if month == 1:
            return True
        return False

    def is_off_season(self) -> bool:
        """Проверка: является ли период межсезоньем."""
        month = self._current_date.month
        return month in (6, 7)  # Июнь-июль

    def is_in_season(self) -> bool:
        """Проверка: идёт ли сезон."""
        month = self._current_date.month
        return 8 <= month <= 5 or month in (8, 9, 10, 11, 12, 1, 2, 3, 4, 5)

    # ── Получение информации ────────────────────────────────────────
    def get_next_matchday(self) -> Optional[str]:
        """Получение даты следующего дня матча."""
        for md in self._matchdays:
            if md > self._current_date:
                return md.strftime("%Y-%m-%d")
        return None

    def get_days_until_matchday(self) -> Optional[int]:
        """Количество дней до следующего дня матча."""
        for md in self._matchdays:
            if md > self._current_date:
                delta = (md - self._current_date).days
                return delta
        return None

    def get_month_name(self) -> str:
        """Название текущего месяца на русском."""
        months = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        return months[self._current_date.month - 1]

    def get_season_phase(self) -> str:
        """Определение фазы сезона по текущей дате."""
        month = self._current_date.month
        if month in (6, 7):
            return "pre_season"
        if 8 <= month <= 12:
            return "in_season"
        if month == 1:
            return "winter_break"
        if 2 <= month <= 5:
            return "in_season"
        return "off_season"

    def get_schedule_for_month(self, year: int, month: int) -> List[Dict[str, Any]]:
        """Получение расписания на конкретный месяц."""
        result = []
        for md in self._matchdays:
            if md.year == year and md.month == month:
                result.append({
                    "date": md.strftime("%Y-%m-%d"),
                    "day_of_week": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"][md.weekday()],
                })
        return result

    def get_days_in_month(self, year: int, month: int) -> int:
        """Количество дней в месяце."""
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        last_day = next_month - timedelta(days=1)
        return last_day.day

    # ── Сериализация ────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация календаря в словарь."""
        return {
            "current_date": self._current_date.strftime("%Y-%m-%d"),
            "start_date": self._start_date.strftime("%Y-%m-%d"),
            "season_start": self._season_start.strftime("%Y-%m-%d"),
            "season_end": self._season_end.strftime("%Y-%m-%d"),
            "transfer_window_open": self._transfer_window_open,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Calendar":
        """Десериализация календаря из словаря."""
        cal = cls(start_date=data.get("start_date", "2024-07-01"))
        cal._current_date = datetime.strptime(data["current_date"], "%Y-%m-%d")
        cal._season_start = datetime.strptime(data["season_start"], "%Y-%m-%d")
        cal._season_end = datetime.strptime(data["season_end"], "%Y-%m-%d")
        cal._transfer_window_open = data.get("transfer_window_open", False)
        return cal

    def __repr__(self) -> str:
        return (
            f"Calendar(date={self.current_date_str}, "
            f"day={self.day_of_week}, "
            f"matchday={'Да' if self.is_matchday() else 'Нет'})"
        )
