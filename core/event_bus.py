"""
core/event_bus.py — Простая шина событий для связи компонентов игры.
Позволяет подписываться на события, отправлять их и отписываться.
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto


class EventType(Enum):
    """Типы событий, которые 발생ают в игре."""
    # События матча
    MATCH_START = auto()
    MATCH_END = auto()
    GOAL = auto()
    RED_CARD = auto()
    YELLOW_CARD = auto()
    PENALTY = auto()
    INJURY_DURING_MATCH = auto()
    SUBSTITUTION = auto()
    HALF_TIME = auto()

    # События трансферов
    TRANSFER = auto()
    TRANSFER_OFFER = auto()
    CONTRACT_RENEWAL = auto()
    LOAN = auto()

    # События игроков
    INJURY = auto()
    RECOVERY = auto()
    FORM_CHANGE = auto()
    MORALE_CHANGE = auto()
    LEVEL_UP = auto()

    # События клуба
    FINANCE_UPDATE = auto()
    REPUTATION_CHANGE = auto()
    MANAGER_HIRED = auto()
    MANAGER_FIRED = auto()

    # Новости и прочее
    NEWS = auto()
    AWARD = auto()
    SEASON_START = auto()
    SEASON_END = auto()
    TRANSFER_WINDOW_OPEN = auto()
    TRANSFER_WINDOW_CLOSE = auto()


@dataclass
class Event:
    """Объект события с метаданными."""
    event_type: EventType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация события в словарь."""
        return {
            "event_type": self.event_type.name,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
        }


class EventBus:
    """
    Шина событий для публикации и подписки.
    Поддерживает несколько подписчиков на одно событии
    и фильтрацию по типу.
    """

    def __init__(self) -> None:
        # Словарь: тип_события -> список колбэков
        self._subscribers: Dict[EventType, List[Callable]] = {}
        # Журнал последних событий для отладки
        self._history: List[Event] = []
        self._max_history = 100

    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        """
        Подписаться на событие.
        :param event_type: тип события
        :param callback: функция, которая будет вызвана при событии
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """
        Отписаться от события.
        :param event_type: тип события
        :param callback: функция для удаления из подписчиков
        """
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                cb for cb in self._subscribers[event_type] if cb != callback
            ]

    def emit(self, event_type: EventType, data: Optional[Dict[str, Any]] = None,
             source: Optional[str] = None) -> None:
        """
        Отправить событие всем подписчикам.
        :param event_type: тип события
        :param data: данные события
        :source: источник события (например, 'match_engine')
        """
        event = Event(
            event_type=event_type,
            data=data or {},
            source=source,
        )

        # Сохраняем в журнал
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        # Уведомляем подписчиков
        for callback in self._subscribers.get(event_type, []):
            try:
                callback(event)
            except Exception as e:
                # Логируем ошибку, но не прерываем выполнение
                print(f"[EventBus] Ошибка в обработчике {event_type.name}: {e}")

    def get_history(self, event_type: Optional[EventType] = None,
                    limit: int = 50) -> List[Event]:
        """
        Получить историю событий.
        :param event_type: фильтр по типу (None = все)
        :param limit: максимальное количество событий
        """
        if event_type is not None:
            filtered = [e for e in self._history if e.event_type == event_type]
        else:
            filtered = self._history
        return filtered[-limit:]

    def clear_history(self) -> None:
        """Очистить журнал событий."""
        self._history.clear()

    def subscriber_count(self, event_type: EventType) -> int:
        """Количество подписчиков на событие."""
        return len(self._subscribers.get(event_type, []))
