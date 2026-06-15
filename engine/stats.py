# -*- coding: utf-8 -*-
"""
Калькулятор статистик - обёртка над C++ StatCalculator.
Расчет рейтинга, стоимости, формы, усталости и морали игроков.
"""

import math
import random
import importlib
from typing import Dict, List, Any, Optional

try:
    from ..models import Player, Club
except ImportError:
    from models import Player, Club


class StatCalculatorWrapper:
    """
    Обёртка над C++ калькулятором статистик.
    Расчет рейтинга, стоимости, формы, усталости и морали.
    """

    CPP_AVAILABLE = False
    _cpp_calc = None

    def __init__(self):
        """Инициализация калькулятора"""
        try:
            module = importlib.import_module('game_engine')
            self._cpp_calc = module.StatCalculator()
            StatCalculatorWrapper.CPP_AVAILABLE = True
        except (ImportError, AttributeError):
            StatCalculatorWrapper.CPP_AVAILABLE = False
            self._cpp_calc = None

        # Константы для расчетов
        self.MAX_RATING = 99
        self.MIN_RATING = 1
        self.PRIME_AGE_START = 25
        self.PRIME_AGE_END = 30
        self.DECLINE_RATE = 0.03  # Скорость угасания после 30
        self.GROWTH_RATE = 0.02   # Скорость роста до 25

    def calculate_rating(self, player: Player) -> float:
        """
        Расчет рейтинга игрока.

        Учитывает:
        - Базовые атрибуты
        - Форму
        - Возраст
        - Усталость
        - Настроение
        - Позицию
        """
        if self.CPP_AVAILABLE and self._cpp_calc is not None:
            try:
                return self._cpp_calc.calculate_rating(self._player_to_dict(player))
            except Exception:
                pass

        return self._calculate_rating_python(player)

    def _calculate_rating_python(self, player: Player) -> float:
        """Python расчет рейтинга"""
        # Базовый рейтинг из атрибутов
        base = player.attributes.overall()

        # Модификатор формы (от -10 до +10)
        form_modifier = (player.form - 50) / 5.0

        # Модификатор усталости (от -15 до 0)
        fatigue_modifier = -player.fatigue / 100 * 15

        # Модификатор настроения (от -5 до +5)
        morale_modifier = (player.morale - 50) / 10.0

        # Модификатор возраста
        age_modifier = 0
        if player.age < self.PRIME_AGE_START:
            # Молодые игроки растут
            age_modifier = (self.PRIME_AGE_START - player.age) * self.GROWTH_RATE * 10
        elif player.age > self.PRIME_AGE_END:
            # Стареющие игроки угасают
            age_modifier = -(player.age - self.PRIME_AGE_END) * self.DECLINE_RATE * 10

        # Штраф за травму
        injury_modifier = 0
        if player.injury:
            injury_modifier = -10

        # Итоговый рейтинг
        rating = (
            base +
            form_modifier +
            fatigue_modifier +
            morale_modifier +
            age_modifier +
            injury_modifier
        )

        # Ограничение диапазона
        return max(self.MIN_RATING, min(self.MAX_RATING, round(rating, 1)))

    def calculate_value(self, player: Player) -> float:
        """
        Расчет рыночной стоимости игрока.

        Факторы:
        - Рейтинг
        - Возраст
        - Потенциал
        - Контракт
        - Форма
        - Позиция
        """
        if self.CPP_AVAILABLE and self._cpp_calc is not None:
            try:
                return self._cpp_calc.calculate_value(self._player_to_dict(player))
            except Exception:
                pass

        return self._calculate_value_python(player)

    def _calculate_value_python(self, player: Player) -> float:
        """Python расчет стоимости"""
        # Базовая стоимость по рейтингу
        rating = self.calculate_rating(player)
        base_value = (rating ** 2.8) * 1000  # Экспоненциальная зависимость

        # Модификатор возраста
        if player.age <= 21:
            # Молодые игроки стоят больше (потенциал)
            age_factor = 1.0 + (21 - player.age) * 0.05
        elif player.age <= 28:
            age_factor = 1.0
        elif player.age <= 32:
            age_factor = 1.0 - (player.age - 28) * 0.1
        else:
            age_factor = max(0.3, 1.0 - (player.age - 28) * 0.15)

        # Модификатор потенциала
        potential_factor = 1.0
        if player.potential > rating + 10:
            potential_factor = 1.2
        elif player.potential < rating - 5:
            potential_factor = 0.8

        # Модификатор позиции
        position_factors = {
            'GK': 0.85, 'CB': 0.9, 'LB': 0.85, 'RB': 0.85,
            'CDM': 0.9, 'CM': 1.0, 'CAM': 1.15,
            'LW': 1.1, 'RW': 1.1, 'ST': 1.2, 'CF': 1.15,
        }
        position_factor = position_factors.get(player.position, 1.0)

        # Модификатор формы
        form_factor = 0.9 + (player.form / 100) * 0.2

        value = base_value * age_factor * potential_factor * position_factor * form_factor

        # Минимальная и максимальная стоимость
        return max(50000, min(200000000, round(value, -3)))

    def calculate_form(self, recent_results: List[Dict[str, Any]]) -> float:
        """
        Расчет формы на основе последних результатов.

        Args:
            recent_results: Список последних матчей
                [{'goals': int, 'assists': int, 'rating': float, 'win': bool}]

        Returns:
            Форма от 0 до 100
        """
        if not recent_results:
            return 50.0

        if self.CPP_AVAILABLE and self._cpp_calc is not None:
            try:
                return self._cpp_calc.calculate_form(recent_results)
            except Exception:
                pass

        return self._calculate_form_python(recent_results)

    def _calculate_form_python(self, recent_results: List[Dict[str, Any]]) -> float:
        """Python расчет формы"""
        if not recent_results:
            return 50.0

        total_score = 0
        weights = [1.0 - i * 0.1 for i in range(len(recent_results))]

        for i, result in enumerate(recent_results):
            weight = max(0.3, weights[i])  # Последние матчи важнее
            match_score = 50  # Нейтральная оценка

            # Оценка за матч
            if result.get('rating'):
                match_score = result['rating']
            else:
                if result.get('win'):
                    match_score += 15
                elif result.get('draw'):
                    match_score += 5
                else:
                    match_score -= 10

                match_score += result.get('goals', 0) * 8
                match_score += result.get('assists', 0) * 5

            total_score += match_score * weight

        # Средневзвешенная оценка
        form = total_score / sum(weights[:len(recent_results)])

        return max(0, min(100, round(form, 1)))

    def calculate_fatigue(self, match_schedule: List[Dict[str, Any]]) -> float:
        """
        Расчет усталости на основе графика матчей.

        Args:
            match_schedule: [{'minutes_played': int, 'days_ago': int}]

        Returns:
            Усталость от 0 до 100
        """
        if not match_schedule:
            return 0.0

        if self.CPP_AVAILABLE and self._cpp_calc is not None:
            try:
                return self._cpp_calc.calculate_fatigue(match_schedule)
            except Exception:
                pass

        return self._calculate_fatigue_python(match_schedule)

    def _calculate_fatigue_python(self, match_schedule: List[Dict[str, Any]]) -> float:
        """Python расчет усталости"""
        if not match_schedule:
            return 0.0

        fatigue = 0
        for match in match_schedule:
            minutes = match.get('minutes_played', 90)
            days_ago = match.get('days_ago', 0)

            # Влиянание минут
            minutes_factor = minutes / 90.0

            # Восстановление со временем (20% в день)
            recovery = max(0, 1.0 - days_ago * 0.2)

            fatigue += minutes_factor * recovery * 25  # Макс 25 за матч

        return min(100, round(fatigue, 1))

    def calculate_morale(
        self,
        recent_results: List[Dict[str, Any]],
        playing_time: Dict[str, int],
        team_standing: Optional[int] = None,
        personal_issues: Optional[List[str]] = None
    ) -> float:
        """
        Расчет настроения игрока.

        Args:
            recent_results: Последние результаты команды
            playing_time: {'matches_played': int, 'matches_available': int}
            team_standing: Позиция в таблице
            personal_issues: Личные проблемы

        Returns:
            Настроение от 0 до 100
        """
        if self.CPP_AVAILABLE and self._cpp_calc is not None:
            try:
                return self._cpp_calc.calculate_morale(
                    recent_results, playing_time,
                    team_standing, personal_issues
                )
            except Exception:
                pass

        return self._calculate_morale_python(
            recent_results, playing_time,
            team_standing, personal_issues
        )

    def _calculate_morale_python(
        self,
        recent_results: List[Dict[str, Any]],
        playing_time: Dict[str, int],
        team_standing: Optional[int] = None,
        personal_issues: Optional[List[str]] = None
    ) -> float:
        """Python расчет настроения"""
        morale = 60  # Базовое настроение

        # Влияние результатов команды
        if recent_results:
            wins = sum(1 for r in recent_results if r.get('win'))
            draws = sum(1 for r in recent_results if r.get('draw'))
            losses = len(recent_results) - wins - draws
            result_score = (wins * 5 + draws * 1 - losses * 3) / max(1, len(recent_results))
            morale += result_score * 3

        # Влияние игровой практики
        if playing_time:
            played = playing_time.get('matches_played', 0)
            available = playing_time.get('matches_available', 1)
            play_ratio = played / max(1, available)
            if play_ratio < 0.3:
                morale -= 15  # Мало играет
            elif play_ratio < 0.6:
                morale -= 5
            elif play_ratio > 0.8:
                morale += 5

        # Позиция в таблице
        if team_standing:
            if team_standing <= 3:
                morale += 8
            elif team_standing <= 6:
                morale += 4
            elif team_standing >= 15:
                morale -= 5

        # Личные проблемы
        if personal_issues:
            morale -= len(personal_issues) * 5

        return max(0, min(100, round(morale, 1)))

    def calculate_potential(
        self,
        player: Player,
        development_history: Optional[List[Dict[str, Any]]] = None
    ) -> int:
        """
        Расчет текущего потенциала игрока.

        Потенциал снижается с возрастом и зависит от развития.
        """
        base_potential = player.potential

        # Снижение потенциала с возрастом
        age_factor = 1.0
        if player.age > 25:
            age_factor = max(0.5, 1.0 - (player.age - 25) * 0.05)

        # Влияние истории развития
        dev_factor = 1.0
        if development_history:
            recent_growth = sum(
                d.get('attribute_growth', 0) for d in development_history[-5:]
            )
            if recent_growth > 5:
                dev_factor = 1.1  # Хорошо растёт
            elif recent_growth < 0:
                dev_factor = 0.9  # Стагнация

        potential = base_potential * age_factor * dev_factor
        return max(30, min(99, int(potential)))

    def calculate_injury_risk(
        self,
        player: Player,
        training_intensity: str = 'medium',
        match_load: int = 0
    ) -> float:
        """
        Расчет риска травмы.

        Returns:
            Риск от 0 до 100
        """
        risk = 10  # Базовый риск

        # Усталость
        risk += player.fatigue * 0.3

        # Возраст (старше 30 - выше риск)
        if player.age > 30:
            risk += (player.age - 30) * 3

        # Интенсивность тренировок
        intensity_map = {'low': 0, 'medium': 5, 'high': 12, 'very_high': 20}
        risk += intensity_map.get(training_intensity, 5)

        # Нагрузка матчей
        risk += match_load * 2

        # Физика (низкая физика = выше риск)
        risk += max(0, (50 - player.attributes.physical) * 0.2)

        # Травма в анамнезе
        if player.injury:
            risk += 15

        return min(100, max(0, round(risk, 1)))

    @staticmethod
    def _player_to_dict(player: Player) -> Dict[str, Any]:
        """Конвертация игрока в словарь для C++ модуля"""
        return {
            'id': player.id,
            'age': player.age,
            'position': player.position,
            'potential': player.potential,
            'form': player.form,
            'fatigue': player.fatigue,
            'morale': player.morale,
            'injury': player.injury,
            'injury_weeks': player.injury_weeks,
            'attributes': player.attributes.to_dict(),
            'appearances': player.appearances,
            'goals_season': player.goals_season,
            'assists_season': player.assists_season,
            'minutes_played': player.minutes_played,
            'value': player.value,
        }

    def batch_calculate(
        self,
        players: List[Player],
        calculations: List[str] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Пакетный расчет статистик для нескольких игроков.

        Args:
            players: Список игроков
            calculations: Какие расчеты выполнять ['rating', 'value', 'fatigue', 'morale']

        Returns:
            Словарь {player_id: {calc_name: value}}
        """
        if calculations is None:
            calculations = ['rating', 'value']

        results = {}
        for player in players:
            player_stats = {}
            if 'rating' in calculations:
                player_stats['rating'] = self.calculate_rating(player)
            if 'value' in calculations:
                player_stats['value'] = self.calculate_value(player)
            if 'fatigue' in calculations:
                player_stats['fatigue'] = player.fatigue
            if 'morale' in calculations:
                player_stats['morale'] = player.morale
            if 'form' in calculations:
                player_stats['form'] = player.form
            if 'injury_risk' in calculations:
                player_stats['injury_risk'] = self.calculate_injury_risk(player)
            if 'potential' in calculations:
                player_stats['potential'] = self.calculate_potential(player)

            results[player.id] = player_stats

        return results
