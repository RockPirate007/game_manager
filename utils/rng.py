"""Обертка над модулем random для генерации случайных чисел в игре."""

import random
from typing import Any, List, Optional, Sequence, Tuple


class RNG:
    """
    Генератор случайных чисел с поддержкой сидирования
    и взвешенного выбора для игровых событий.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Инициализация генератора.

        Args:
            seed: Начальное значение зерна (None = случайное)
        """
        self._seed = seed
        self._rng = random.Random(seed)

    def seed(self, value: int) -> None:
        """
        Установить новое зерно генерации.

        Args:
            value: Новое значение зерна
        """
        self._seed = value
        self._rng.seed(value)

    def randint(self, a: int, b: int) -> int:
        """
        Случайное целое число в диапазоне [a, b].

        Args:
            a: Минимальное значение
            b: Максимальное значение

        Returns:
            Случайное число от a до b включительно
        """
        return self._rng.randint(a, b)

    def random(self) -> float:
        """Случайное дробное число в диапазоне [0.0, 1.0)."""
        return self._rng.random()

    def uniform(self, a: float, b: float) -> float:
        """
        Случайное дробное число в диапазоне [a, b].

        Args:
            a: Минимальное значение
            b: Максимальное значение
        """
        return self._rng.uniform(a, b)

    def choice(self, seq: Sequence[Any]) -> Any:
        """
        Случайный элемент из последовательности.

        Args:
            seq: Последовательность для выбора

        Returns:
            Случайный элемент
        """
        return self._rng.choice(seq)

    def choices(
        self, seq: Sequence[Any], weights: Optional[List[float]] = None, k: int = 1
    ) -> List[Any]:
        """
        Список случайных элементов с возможным весом.

        Args:
            seq: Последовательность для выбора
            weights: Веса элементов
            k: Количество выборов

        Returns:
            Список выбранных элементов
        """
        return self._rng.choices(seq, weights=weights, k=k)

    def weighted_choice(self, items: List[Tuple[Any, float]]) -> Any:
        """
        Взвешенный случайный выбор.

        Args:
            items: Список кортежей (элемент, вероятность)

        Returns:
            Выбранный элемент

        Raises:
            ValueError: Если список пуст или веса некорректны
        """
        if not items:
            raise ValueError("Список элементов не может быть пустым")

        elements, weights = zip(*items)

        # Проверяем, что все веса неотрицательны
        if any(w < 0 for w in weights):
            raise ValueError("Веса не могут быть отрицательными")

        # Проверяем, что сумма весов больше нуля
        if sum(weights) <= 0:
            raise ValueError("Сумма весов должна быть больше нуля")

        return self._rng.choices(elements, weights=weights, k=1)[0]

    def gaussian(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        """
        Случайное число из нормального распределения.

        Args:
            mu: Математическое ожидание
            sigma: Стандартное отклонение

        Returns:
            Значение из нормального распределения
        """
        return self._rng.gauss(mu, sigma)

    def shuffle(self, lst: list) -> None:
        """
        Перемешать список на месте.

        Args:
            lst: Список для перемешивания
        """
        self._rng.shuffle(lst)

    def sample(self, population: Sequence[Any], k: int) -> List[Any]:
        """
        Выбрать k уникальных элементов без повторений.

        Args:
            population: Исходная последовательность
            k: Количество элементов

        Returns:
            Список выбранных элементов
        """
        return self._rng.sample(population, k)

    def weighted_event(self, success_rate: float) -> bool:
        """
        Проверить, произошло ли событие с заданной вероятностью.

        Args:
            success_rate: Вероятность успеха (0.0 - 1.0)

        Returns:
            True если событие произошло
        """
        return self._rng.random() < success_rate

    def generate_rating(self, base: int = 50, variance: int = 20) -> int:
        """
        Сгенерировать рейтинг игрока (1-99).

        Args:
            base: Базовый рейтинг
            variance: Максимальное отклонение от базы

        Returns:
            Рейтинг от 1 до 99
        """
        raw = self.gauss(base, variance / 3)
        return max(1, min(99, int(raw)))

    def match_event_type(self) -> str:
        """
        Определить тип события матча.

        Returns:
            Тип события: 'goal', 'miss', 'save', 'foul', 'corner', 'nothing'
        """
        events = [
            ("goal", 10),
            ("miss", 20),
            ("save", 25),
            ("foul", 15),
            ("corner", 15),
            ("nothing", 15),
        ]
        return self.weighted_choice(events)

    @property
    def current_seed(self) -> Optional[int]:
        """Текущее значение зерна."""
        return self._seed

    def __repr__(self) -> str:
        return f"RNG(seed={self._seed})"
